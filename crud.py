from sqlalchemy.orm import Session
from models import Fire, Report
from typing import List 
import geojson
import json

def get_fire(db: Session, fire_id: int):
    features = []
    data = db.query(Fire).filter(Fire.id == fire_id).first()
    point = geojson.Point((data.longitude, data.latitude, 0))
    properties = {
        "id": data.id,
        "country_id": data.country_id,
        "brightness": data.brightness,
        "scan": data.scan,
        "track": data.track,
        "acq_date": data.acq_date,
        "acq_time": data.acq_time,
        "confidence": data.confidence,
        "bright_t31": data.bright_t31,
        "frp": data.frp,
        "daynight": data.daynight
    }
    
    feature = geojson.Feature(geometry=point, properties=properties)
    features.append(feature)
    feature_collection = geojson.FeatureCollection(features)

    geojson_string = geojson.dumps(feature_collection, sort_keys=True)
    geojson_dict = json.loads(geojson_string)
    return geojson_dict


def get_fire_by_date(db: Session, date: str):
    confidence: int = 70
    data = list(db.query(Fire).filter(Fire.acq_date == date).filter(Fire.confidence >= confidence).all())
    features = []

    for data in data:
        point = geojson.Point((data.longitude, data.latitude, 0))
        properties = {
            "id": data.id,
            "country_id": data.country_id,
            "brightness": data.brightness,
            "scan": data.scan,
            "track": data.track,
            "acq_date": data.acq_date,
            "acq_time": data.acq_time,
            "confidence": data.confidence,
            "bright_t31": data.bright_t31,
            "frp": data.frp,
            "daynight": data.daynight
        }
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)
        feature_collection = geojson.FeatureCollection(features)

    geojson_string = geojson.dumps(feature_collection, sort_keys=True)
    geojson_dict = json.loads(geojson_string)
    return geojson_dict


def post_report(db: Session, report_data: object):
    db_report = Report(latitude=report_data.latitude, longitude=report_data.longitude, image_url=report_data.image_url, message=report_data.message, timestamp=report_data.timestamp)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_report(db: Session, report_id: int):
    data = db.query(Report).filter(Report.id == report_id).first()
    return data