"""Module containing SQLAlchemy models for the Fire and Report tables."""

from sqlalchemy import Column, Float, Integer, String, TIMESTAMP
from app.database import Base

class Fire(Base):
    """
    SQLAlchemy model for the Fire table.

    Attributes:
        id (int): The unique identifier for a fire.
        country_id (str): The country identifier.
        latitude (float): The latitude coordinate of the fire.
        longitude (float): The longitude coordinate of the fire.
        brightness (float): The brightness level of the fire.
        scan (float): The scan value.
        track (float): The track value.
        acq_date (str): The acquisition date of the fire.
        acq_time (int): The acquisition time of the fire.
        confidence (int): The confidence level of the fire.
        bright_t31 (float): The bright_t31 value.
        frp (float): The frp (Fire Radiative Power) value.
        daynight (str): The day or night indicator.

    """
    __tablename__ = "fires"
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(String, unique=True, index=True)
    latitude = Column(String)
    longitude = Column(String)
    brightness = Column(Float)
    scan = Column(Float)
    track = Column(Float)
    acq_date = Column(String)
    acq_time = Column(Integer)
    confidence = Column(Integer)
    bright_t31 = Column(Float)
    frp = Column(Float)
    daynight = Column(String)

class Report(Base):
    """
    SQLAlchemy model for the Report table.

    Attributes:
        id (int): The unique identifier for a report.
        latitude (float): The latitude coordinate associated with the report.
        longitude (float): The longitude coordinate associated with the report.
        image_url (str): The URL of the image associated with the report.
        message (str): The message or description of the report.
        timestamp (TIMESTAMP): The timestamp when the report was created.

    """
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(String)
    longitude = Column(String)
    image_url = Column(String)
    message = Column(String)
    ai_message = Column(String)
    timestamp = Column(TIMESTAMP)
