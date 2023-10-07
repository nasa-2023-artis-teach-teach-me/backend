from sqlalchemy import Column, Float, Integer, String
from database import Base

class Fire(Base):
    __tablename__ = "fires"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    brightness = Column(Float)
    scan = Column(Float)
    track = Column(Float)
    acq_date = Column(String)
    acq_time = Column(Integer)
    confidence = Column(Integer)
    bright_t31 = Column(Float)
    frp = Column(Float)
    daynight = Column(String)

