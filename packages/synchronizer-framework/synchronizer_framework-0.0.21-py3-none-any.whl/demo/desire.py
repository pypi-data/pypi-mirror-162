from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship

from demo.util import Repr, UpdatedAt

DesireBase = declarative_base()


class CloudServiceProvider(DesireBase, UpdatedAt, Repr):
    __tablename__ = "cloud_service_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    upgrade_allowed = Column(Boolean)
    children = relationship("CloudRegion", back_populates="parent")
    pending_update = Column(Boolean, default=False, nullable=False)


class CloudRegion(DesireBase, UpdatedAt, Repr):
    __tablename__ = "cloud_regions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    external_ref = Column(String)
    parent_id = Column(Integer, ForeignKey("cloud_service_providers.id"))
    parent = relationship("CloudServiceProvider", back_populates="children")
    children = relationship("CloudHandover", back_populates="parent")


class CloudHandover(DesireBase, UpdatedAt, Repr):
    __tablename__ = "cloud_handovers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    external_ref = Column(String)
    parent_id = Column(Integer, ForeignKey("cloud_regions.id"))
    parent = relationship("CloudRegion", back_populates="children")
    children = relationship("NIC", back_populates="parent")


class NIC(DesireBase, UpdatedAt, Repr):
    __tablename__ = "nics"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    external_ref = Column(String)
    parent_id = Column(Integer, ForeignKey("cloud_handovers.id"))
    parent = relationship("CloudHandover", back_populates="children")
