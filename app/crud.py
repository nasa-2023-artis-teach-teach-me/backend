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

def post_fire(db: Session, data: object):
    db_fire = Fire(
        country_id = data.get("country_id"),
        latitude = data.get("latitude"),
        longitude = data.get("longitude"),
        brightness = data.get("brightness"),
        scan = data.get("scan"),
        track = data.get("track"),
        acq_date = data.get("acq_date"),
        acq_time = data.get("acq_time"),
        confidence = data.get("confidence"),
        bright_t31 = data.get("bright_t31"),
        frp = data.get("frp"),
        daynight = data.get("daynight")
    )
    db.add(db_fire)
    db.commit()
    db.refresh(db_fire)
    return db_fire

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

    reports = get_report_by_date(db, date, True)

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
        category=report_data["category"],
        message=report_data["message"],
        timestamp=(datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S"),
        from_nasa = report_data["from_nasa"]
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

def get_report_by_date(db: Session, date: str, only_fire: bool = False):

    start = datetime.strptime(date, '%Y-%m-%d')
    end = start + timedelta(days=1)

    db_report = None

    if only_fire:
        db_report = db.query(Report).filter(and_(Report.timestamp > start, Report.timestamp < end)).filter(Report.category == 'fire-report').all()
    else:
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
    if report_data.get("ai_message") is not None:
        existing_report.ai_message = report_data["ai_message"]
    if report_data.get("category") is not None:
        existing_report.category = report_data["category"]
    if image_url is not None:
        existing_report.image_url = image_url
    if report_data.get("from_nasa") is not None:
        existing_report.from_nasa = report_data["from_nasa"]
    db.commit()

    db.refresh(existing_report)
    return existing_report

def get_report_by_lonlat(db: Session, lon: str, lat: str):

    data = db.query(Report).filter(Report.longitude == lon).filter(Report.latitude == lat).all()
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
                f"""This is a fire reported by NASA FIRMS on {fire_data.acq_date} at [{fire_data.longitude}, {fire_data.latitude}], which has a confidence level of {fire_data.confidence}%. The pixel-integrated fire radiative power is {fire_data.frp} MW, and the brightness temperature measured (in Kelvin) of channel 21/22 is {fire_data.brightness}, while channel 31 recoreds a temperature of {fire_data.bright_t31}.""",
                from_nasa= True,
                timestamp= datetime.strptime(fire_data.acq_date, "%Y-%m-%d") ,
            )
            db.add(db_report)
            db.commit()
            db.refresh(db_report)
    return "update success"