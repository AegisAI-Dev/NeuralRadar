from sqlalchemy import Column, Integer, String
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
