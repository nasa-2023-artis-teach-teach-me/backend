"""
This file implement crud actions
"""
import json
from datetime import datetime, timedelta
import geojson
from fastapi import HTTPException
from sqlalchemy import and_, func
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
    point = geojson.Point((float(data.longitude), float(data.latitude), 0))
    properties = {
        # "id": data.id,
        # "country_id": data.country_id,
        # "brightness": data.brightness,
        # "scan": data.scan,
        # "track": data.track,
        # "acq_date": data.acq_date,
        # "acq_time": data.acq_time,
        # "confidence": data.confidence,
        # "bright_t31": data.bright_t31,
        # "frp": data.frp,
        # "daynight": data.daynight,
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
            "position": [float(data.longitude), float(data.latitude)]
        })

    return result


def get_fire_raw_by_date_str(db: Session, date: str):
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
        point = geojson.Point((float(data.longitude), float(data.latitude), 0))
        properties = {
            # "id": data.id,
            # "country_id": data.country_id,
            # "brightness": data.brightness,
            # "scan": data.scan,
            # "track": data.track,
            # "acq_date": data.acq_date,
            # "acq_time": data.acq_time,
            # "confidence": data.confidence,
            # "bright_t31": data.bright_t31,
            # "frp": data.frp,
            # "daynight": data.daynight,
            # "src": "firm"
        }
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)
        feature_collection = geojson.FeatureCollection(features)

    reports = get_report_by_date(db, date)

    for report in reports:

        point = geojson.Point((float(report.longitude), float(report.latitude), 0))
        properties = {
            "id": report.id,
            "message": report.message,
            "image_url": report.image_url,
            "acq_time": str(report.timestamp),
            "acq_date": str(report.timestamp).split(' ')[0],
            "src": "report"
        }
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)
        feature_collection = geojson.FeatureCollection(features)
    
    if len(features) == 0:
        return {
            "type": "FeatureCollection",
            "features": []
        }

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
        timestamp=(datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S"),
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_report(db: Session):
    """
    Retrieve a report by its unique ID from the database.

    Args:
        db (Session): The SQLAlchemy database session.

    Returns:
        Report: The report data.
    """
    data = db.query(Report).all()
    return list(data)


def get_report_by_id(db: Session, report_id: int):
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

def get_report_by_date(db: Session, date: str):

    start = datetime.strptime(date, '%Y-%m-%d')
    end = start + timedelta(days=1)
    
    db_report = db.query(Report).filter(and_(Report.timestamp > start, Report.timestamp < end)).all()
    return db_report


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

    data = db.query(Report).filter(Report.longitude == lon).all()
    return data

def update_report_with_raw(db: Session, date: str,):
    fire_raw = get_fire_raw_by_date_str(db, date)
    for all_pos in fire_raw:
        pos_lon = all_pos["position"][0]
        pos_lat = all_pos["position"][1]

        fire_data = db.query(Fire).filter(Fire.longitude == pos_lon).filter(Fire.latitude == pos_lat).first()
        if fire_data:
            db_report = Report(
                latitude=fire_data.latitude,
                longitude=fire_data.longitude,
                image_url= "string",
                message=
                f"""The provided "fire_data" represents information about a specific fire event that occurred on {fire_data.acq_date}. 
    The fire's location is indicated by its longitude of {fire_data.longitude} and latitude of {fire_data.latitude}. 
    This fire had a high level of confidence, scoring {fire_data.confidence}, which suggests a strong likelihood that it was indeed a fire. 
    The brightness of the fire was measured at 311.81, and it emitted a fire radiative power (FRP) of {fire_data.frp}. 
    The scan value of 2.3 indicates the satellite scan angle, while the track is {fire_data.scan}. 
    The fire was detected at 221 seconds past midnight, as indicated by the {fire_data.longitude}.
    Additionally, the brightness temperature at 3.1 micrometers (bright_t31) was {fire_data.bright_t31}, 
    and the event occurred during the nighttime, denoted by "daynight" as {fire_data.daynight}.
    The absence of a country ID suggests that the fire may be located in an area with unclear jurisdiction or remote location. 
    This data provides valuable insights into the characteristics and location of the fire event on the specified date.""",
                timestamp= datetime.strptime(fire_data.acq_date, "%Y-%m-%d") ,
            )
            db.add(db_report)
            db.commit()
            db.refresh(db_report)
    return "update success"