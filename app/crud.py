"""
This file implement crud actions
"""
import json
from datetime import datetime
import geojson
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Fire, Report


def get_fire(db: Session, fire_id: int):
    """
    Retrieve fire data by its unique ID.

    Args:
        db (Session): The SQLAlchemy database session.
        fire_id (int): The unique ID of the fire to retrieve.

    Returns:
        dict: A GeoJSON representation of the fire data.
    """
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
        "daynight": data.daynight,
    }

    feature = geojson.Feature(geometry=point, properties=properties)
    features.append(feature)
    feature_collection = geojson.FeatureCollection(features)

    geojson_string = geojson.dumps(feature_collection, sort_keys=True)
    geojson_dict = json.loads(geojson_string)
    return geojson_dict

def get_fire_raw_by_date(db: Session, date: str):
    """
    Retrieve fire data by date and confidence level and return it as GeoJSON.

    Args:
        db (Session): The SQLAlchemy database session.
        date (str): The date for which to retrieve fire data.

    Returns:
        dict: A GeoJSON representation of the retrieved fire data.
    """
    confidence: int = 70
    fire_data = list(
        db.query(Fire)
        .filter(Fire.acq_date == date)
        .filter(Fire.confidence >= confidence)
        .all()
    )

    result = []

    for data in fire_data:

        result.append({
            "id": data.id,
            "position": [data.longitude, data.latitude]
        })

    return result


def get_fire_by_date(db: Session, date: str):
    """
    Retrieve fire data by date and confidence level and return it as GeoJSON.

    Args:
        db (Session): The SQLAlchemy database session.
        date (str): The date for which to retrieve fire data.

    Returns:
        dict: A GeoJSON representation of the retrieved fire data.
    """
    confidence: int = 70
    fire_data = list(
        db.query(Fire)
        .filter(Fire.acq_date == date)
        .filter(Fire.confidence >= confidence)
        .all()
    )
    features = []

    for data in fire_data:
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
            "daynight": data.daynight,
        }
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)
        feature_collection = geojson.FeatureCollection(features)

    geojson_string = geojson.dumps(feature_collection, sort_keys=True)
    geojson_dict = json.loads(geojson_string)
    return geojson_dict


def post_report(db: Session, report_data: object, image_url: str = None):
    """
    Create and store a new report in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        report_data (object): The report data, including latitude, longitude, message, etc.
        image_url (str): The URL of the stored image.

    Returns:
        Report: The created report object stored in the database.
    """
    db_report = Report(
        latitude=report_data["latitude"],
        longitude=report_data["longitude"],
        image_url=image_url,
        message=report_data["message"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_report(db: Session, report_id: int):
    """
    Retrieve a report by its unique ID from the database.

    Args:
        db (Session): The SQLAlchemy database session.
        report_id (int): The unique ID of the report to retrieve.

    Returns:
        Report: The report data corresponding to the given report ID.
    """
    data = db.query(Report).filter(Report.id == report_id).first()
    return data



def update_report(db: Session, report_id: int ,report_data: object, image_url: str = None):
    """
    Update a report by its unique ID from the database.

    Args:
        db (Session): The SQLAlchemy database session.
        report_id (int): The unique ID of the report to retrieve.

    Returns:
        Report: The report data corresponding to the given report ID.
    """
    existing_report = db.query(Report).filter(Report.id == report_id).first()
    if existing_report is None:
        raise HTTPException(status_code=404, detail="Report with not found")

    if report_data.get("latitude") is not None:
        existing_report.latitude = report_data["latitude"]
    if report_data.get("longitude") is not None:
        existing_report.longitude = report_data["longitude"]
    if report_data.get("message") is not None:
        existing_report.message = report_data["message"]
    if image_url is not None:
        existing_report.image_url = image_url

    db.commit()

    db.refresh(existing_report)
    return existing_report

def get_report_by_lonlat(db: Session, lon: str, lat: str):

    print(lon)

    data = db.query(Report).filter(Report.longitude == lon).all()
    return data