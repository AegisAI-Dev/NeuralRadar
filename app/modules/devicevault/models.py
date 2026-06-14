from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    name = Column(String, default="—")
    detected_hostname = Column(String, default="—")
    mac_address = Column(String, index=True, default="—")
    vendor = Column(String, default="—")
    device_type = Column(String, default="Unclassified")
    status = Column(String, default="Online")
    tags = Column(String, default="")
    notes = Column(String, default="")
    discovery_source = Column(String, default="—")
    confidence = Column(String, default="—")
    first_seen = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_seen = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    response_time = Column(String, default="0")
    source_module = Column(String, default="IPHawk")
    
    # Relationships
    services = relationship("OpenPort", back_populates="device", cascade="all, delete-orphan")

class OpenPort(Base):
    __tablename__ = "open_ports"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    ip_address = Column(String, index=True)
    port = Column(Integer, index=True)
    protocol = Column(String, default="TCP")
    service_guess = Column(String, default="—")
    state = Column(String, default="Open")
    response_time = Column(String, default="0")
    first_seen = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_seen = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    source_module = Column(String, default="PortScope")

    device = relationship("Device", back_populates="services")
