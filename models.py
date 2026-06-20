from sqlalchemy import Column, Integer, String
from database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String)
    event_type = Column(String)
    severity = Column(String)