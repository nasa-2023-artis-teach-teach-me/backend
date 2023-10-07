from sqlalchemy.orm import Session
from models import Fire
from typing import List 
import geopandas as gpd
import geojson

def get_fire(db: Session, fire_id: int):
    return db.query(Fire).filter(Fire.id == fire_id).first()


