from pydantic import BaseModel

class Fire(BaseModel):
    id: int
    country_id: str
    latitude: float
    longitude: float
    brightness: float
    scan: float
    track: float
    acq_date: str
    acq_time: int
    confidence: int
    bright_t31: float
    frp: float
    daynight: str

    class Config:
        from_attributes = True
