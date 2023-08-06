import os

from sync.backends.inmemory import InMemoryDs
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sync.backends.sqlalchemy import SQADataSource
from demo.daphne import DaphneBase, VlanServiceProvider, VlanServiceConnection
from demo.desire import (
    DesireBase,
    CloudServiceProvider,
    CloudRegion,
    CloudHandover,
    NIC,
)
from demo.util import Repr

from sync.mapping import Mapping, Mode, AttributeMap

DESIRE_SQLITE = "/tmp/desire.sqlite"
DAPHNE_SQLITE = "/tmp/daphne.sqlite"


def cleanup():
    if os.path.exists(DESIRE_SQLITE):
        os.remove(DESIRE_SQLITE)
    if os.path.exists(DAPHNE_SQLITE):
        os.remove(DAPHNE_SQLITE)


def daphne_ds():
    return InMemoryDs()


def daphne_sqa_ds():
    return SQADataSource(f"sqlite:///{DAPHNE_SQLITE}", DaphneBase)


def desire_ds():
    return InMemoryDs()


def desire_sqa_ds():
    return SQADataSource(f"sqlite:///{DESIRE_SQLITE}", DesireBase)


def populate_daphne(daphne):
    for o in {
        VlanServiceProvider(
            name="AWS",
            canUpgrade=False,
            children=[
                VlanServiceConnection(name="nic-1", region="eu-central-1", pop="INX6"),
                VlanServiceConnection(name="nic-2", region="eu-central-1", pop="EqFA5"),
                VlanServiceConnection(name="nic-3", region="eu-west-2", pop="EqFA5"),
            ],
        ),
        VlanServiceProvider(name="AZURE", canUpgrade=True, children=[]),
    }:
        daphne.persist(o)


def populate_desire(desire):
    for o in {
        CloudServiceProvider(
            name="AWS",
            children=[
                CloudRegion(
                    name="eu-central-1",
                    children=[
                        CloudHandover(name="INX6", children=[NIC(name="nic-1")]),
                        CloudHandover(name="EqFA5", children=[NIC(name="nic-2a")]),
                    ],
                ),
                CloudRegion(
                    name="eu-west-1",
                    children=[
                        CloudHandover(name="LON1", children=[NIC(name="nic-3a")])
                    ],
                ),
                CloudRegion(
                    name="eu-west-2",
                    children=[
                        CloudHandover(
                            name="EqFA5",
                            children=[NIC(name="nic-3", external_ref="nic3-eref")],
                        )
                    ],
                ),
            ],
        ),
        CloudServiceProvider(
            name="IBM",
            children=[
                CloudRegion(
                    name="EU-Frankfurt",
                    children=[
                        CloudHandover(name="fra03", children=[NIC(name="nic-4")])
                    ],
                )
            ],
        ),
    }:
        desire.persist(o)


def make_mappings():
    return [
        Mapping(
            entity_types=(VlanServiceConnection, CloudRegion),
            modes={Mode.LEFT_TO_RIGHT},
            keys={
                AttributeMap("region", "name"),
                AttributeMap(
                    "parent", "parent", VlanServiceProvider, CloudServiceProvider
                ),
            },
        ),
        Mapping(
            entity_types=(VlanServiceProvider, CloudServiceProvider),
            modes={Mode.LEFT_TO_RIGHT, Mode.RIGHT_TO_LEFT},
            keys={AttributeMap("name", "name")},
            attributes={AttributeMap("canUpgrade", "upgrade_allowed")},
        ),
        Mapping(
            entity_types=(VlanServiceConnection, CloudHandover),
            modes={Mode.LEFT_TO_RIGHT},
            keys={
                AttributeMap("pop", "name"),
                AttributeMap("__self__", "parent", VlanServiceConnection, CloudRegion),
            },
        ),
        Mapping(
            entity_types=(VlanServiceConnection, NIC),
            modes={Mode.RIGHT_TO_LEFT},
            keys={
                AttributeMap("name", "name"),
                AttributeMap("region", ("parent", "parent", "name")),
                AttributeMap("pop", ("parent", "name")),
                AttributeMap(
                    "parent",
                    ("parent", "parent", "parent"),
                    VlanServiceProvider,
                    CloudServiceProvider,
                ),
            },
            attributes={AttributeMap("externalRef", "external_ref")},
        ),
        Mapping(
            entity_types=(VlanServiceConnection, NIC),
            modes={Mode.LEFT_TO_RIGHT},
            keys={
                AttributeMap("name", "name"),
                AttributeMap(
                    "__self__", "parent", VlanServiceConnection, CloudHandover
                ),
            },
            attributes={AttributeMap("externalRef", "external_ref")},
        ),
    ]


UserCompanyBase = declarative_base()


class Company(UserCompanyBase, Repr):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship("User", back_populates="company")


class User(UserCompanyBase, Repr):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="users")
