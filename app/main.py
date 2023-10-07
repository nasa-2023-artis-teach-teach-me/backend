"""
This module contains FastAPI endpoints for handling fire reports and images.
"""
from functools import lru_cache
import json
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from app.map import get_transaction_count
from app.database import SessionLocal
from app import crud
from app import config
from app.group import Group
from app.src.readers import INPUT
from app.s3 import store_image

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """
    Create a database session and yield it for use in FastAPI dependencies.

    This function creates a database session using the `SessionLocal` object
    and yields it for use as a dependency in FastAPI route functions. The
    session is automatically closed when it's no longer needed.

    Note: Make sure to close the session when you're done with it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings():
    """
    Get the env settings.
    """
    return config.Settings()


@app.get("/")
async def count(settings: Annotated[config.Settings, Depends(get_settings)]):
    """
    Get the transaction count.

    Parameters:
    - settings: Annotated[config.Settings, Depends(get_settings)] - The application settings.

    Returns:
    dict: A dictionary with a message and transaction count.
    """
    transaction_count = get_transaction_count(settings.MAP_KEY)
    return {"message": "Hello World", "transaction count": transaction_count}


@app.get("/api/fire/{fire_id}", response_model=None)
async def get_fire(fire_id: int, db: Session = Depends(get_db)):
    """
    Get fire data by its ID.

    Parameters:
    - fire_id (int): The ID of the fire data to retrieve.
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing fire data.
    """
    fire_data = crud.get_fire(db, fire_id)
    return fire_data


@app.get("/api/fire/date/{date}", response_model=None)
async def get_fire_by_date(date: str, db: Session = Depends(get_db)):
    """
    Get fire data by date.

    Parameters:
    - date (str): The date of the fire data to retrieve.
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing fire data.
    """
    fire_data = crud.get_fire_by_date(db, date)
    return fire_data

@app.get("/api/fire/raw/{date}", response_model=None)
async def get_raw_fire(date: str, db: Session = Depends(get_db)):

    positions: List[List[int, int]] = []

    fires = crud.get_fire_raw_by_date(db, date)

    for fire in fires:
        positions.append(fire.get("position"))

    groups = Group(INPUT(positions))
    result = []

    for group in groups.gen():

        ids = []
        xs = [pos.x for pos in group]
        ys = [pos.y for pos in group]

        for location in group:

            loc = [location.x, location.y]

            for fire in fires:

                if fire.get("position") == loc:
                    ids.append(fire.get("id"))
                    break

        result.append({
            "center": [sum(xs)/len(xs), sum(ys)/len(ys)],
            "positions": json.loads(repr(group)),
            "id": ids
        })

    print(result)

    return result


@app.post("/api/report", response_model=None)
async def post_report(
    latitude: str = Form(...),
    longitude: str = Form(...),
    message: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """
    Create a new report with latitude, longitude, message, and an uploaded image.

    Parameters:
    - latitude (float): The latitude coordinate of the report.
    - longitude (float): The longitude coordinate of the report.
    - message (str): The message or description of the report.
    - image (UploadFile): The uploaded image associated with the report.
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing the created report data.
    """
    report_data = {
        "latitude": latitude,
        "longitude": longitude,
        "message": message,
        "image": image,
    }

    if image is not None:
        image_data = await report_data["image"].read()
        image_url = store_image(image_data)
        report_data = crud.post_report(db, report_data, image_url)
    else:
        image_url = ""
        report_data = crud.post_report(db, report_data, image_url)
    return report_data


@app.get("/api/report/{report_id}", response_model=None)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Get report data by its ID.

    Parameters:
    - report_id (int): The ID of the report data to retrieve.
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing report data.
    """
    report_data = crud.get_report(db, report_id)
    return report_data

@app.post("/api/image")
async def upload_image(image: UploadFile = File(...)):
    """
    upload image to minio with status code 200
    """
    image_data = await image.read()
    image_url = store_image(image_data)
    return {"url": image_url}


@app.patch("/api/report/{report_id}")
async def update_report(report_id: int, latitude: str = Form(None),
                       longitude: str = Form(None),
                       message: str = Form(None),
                       new_image: UploadFile = File(None),
                       db: Session = Depends(get_db)):
    """
    update report data
    """
    report_data = {
        "latitude": latitude,
        "longitude": longitude,
        "message": message,
        "image": new_image,
    }

    if new_image is not None:
        image_data = await report_data["image"].read()
        image_url = store_image(image_data)
        report_data = crud.update_report(db, report_id, report_data, image_url)
    else:
        report_data = crud.update_report(db, report_id, report_data)
    return report_data


@app.get("/api/report/{lon}/{lat}", response_model=None)
async def get_report_by_lonlat(lon: str, lat: str, db: Session = Depends(get_db)):

    report_data = crud.get_report_by_lonlat(db, lon, lat)
    return report_data

def start():
    """
    Start the FastAPI application using Uvicorn.
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
