from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import _Null

from demo.util import Repr, UpdatedAt

DaphneBase = declarative_base()

class VlanServiceProvider(DaphneBase, UpdatedAt, Repr):
    __tablename__ = "vlan_service_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    canUpgrade = Column(Boolean)
    children = relationship("VlanServiceConnection", back_populates="parent")
    pending_update = Column(Boolean, default=False, nullable=False)


class VlanServiceConnection(DaphneBase, UpdatedAt, Repr):
    __tablename__ = "vlan_service_connections"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    region = Column(String)
    pop = Column(String)
    externalRef = Column(String)
    parent_id = Column(Integer, ForeignKey("vlan_service_providers.id"))
    parent = relationship("VlanServiceProvider", back_populates="children")
