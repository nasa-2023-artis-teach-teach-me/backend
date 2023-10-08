"""Module containing the Pydantic Fire model."""

from pydantic import BaseModel


class Fire(BaseModel):
    """
    Pydantic model representing a fire event.

    Attributes:
        id (int): The unique identifier for the fire event.
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
    id: int
    country_id: str
    latitude: str
    longitude: str
    brightness: float
    scan: float
    track: float
    acq_date: str
    acq_time: int
    confidence: int
    bright_t31: float
    frp: float
    daynight: str
