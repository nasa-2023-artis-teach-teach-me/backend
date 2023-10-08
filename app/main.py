"""
This module contains FastAPI endpoints for handling fire reports and images.
"""
import os
import asyncio
from functools import lru_cache
import json
import requests
from typing import List
import uvicorn
from concurrent.futures.process import ProcessPoolExecutor
from fastapi import Depends, FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from typing import Dict
from sqlalchemy.orm import Session
from app.map import get_transaction_count
from app.database import SessionLocal
from app import crud
from app import config
from app.group import Group
from app.src.readers import INPUT
from app.s3 import store_image
from app.database import create_tables

from uuid import UUID, uuid4
from pydantic import BaseModel, Field

AI_SERVER_URL = os.environ.get("AI_SERVER_URL", "http://10.3.25.2:8000")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
create_tables()

class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = "in_progress"
    result: int = None

jobs: Dict[UUID, Job] = {}

async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)  # wait and return result


def get_ai_reponse(data: dict):
        
        try:
            r = requests.get(AI_SERVER_URL)

            if not r.ok:
                raise requests.exceptions.ConnectionError

            r = requests.post(
                f"{AI_SERVER_URL}/api/llava",
                {
                    "longitude": data.get('longitude'),
                    "latitude": data.get('latitude'),
                    "message": data.get('message'),
                    "category": data.get('category'),
                    "id": data.get('id'),
                    "image_url": data.get('image_url'),
                    "timestamp": data.get('timestamp')
                },
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }
            )

            try:
                DEFAULT_MSG = r.json().get("response")
            except:
                pass

        except requests.exceptions.ConnectionError:
            DEFAULT_MSG = "To prevent flames, consider the following steps:\n\n1. Ensure p. Maintain clear surroundings: Keep the area around the structure clear of dls: Choose fire-resistant materials for construction and clothing to minimiznguish fires quickly, reducing the damage and risk to life.\n5. Regular mainn good working order.\n"

            
        data['ai_message'] = DEFAULT_MSG

        requests.patch(
            f"http://localhost:8000/api/report/{data.get('id')}",
            data
        )


async def start_ai_task(uid: UUID, data: dict) -> None:
    jobs[uid].result = await run_in_process(get_ai_reponse, data)

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

@app.post("/api/fire", response_model=None)
def post_fire(
    latitude:float = Form(...),
    longitude:float = Form(...),
    brightness:float = Form(...),
    scan:float = Form(...),
    track:float = Form(...),
    acq_date:str = Form(...),
    acq_time:int = Form(...),
    confidence:int = Form(...),
    bright_t31:float = Form(...),
    frp:float = Form(...),
    daynight:str = Form(...),
    db: Session = Depends(get_db),
):
    report_data = {
        "latitude": latitude,
        "longitude": longitude,
        "brightness": brightness,
        "scan": scan,
        "track": track,
        "acq_date": acq_date,
        "acq_time": acq_time,
        "confidence": confidence,
        "bright_t31": bright_t31,
        "frp": frp,
        "daynight": daynight,
    }

    report_data = crud.post_fire(db, report_data)
    return report_data

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

    reports = crud.get_report_by_date(db, date)

    for report in reports:
        try:
            positions.append([float(report.longitude), float(report.latitude)])
        except ValueError:
            pass

    if len(positions) == 0:
        return []

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

    return result


@app.get("/api/report", response_model=None)
async def get_report(db: Session = Depends(get_db)):
    """
    Get fire data.

    Parameters:
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing fire data.
    """
    report_data = crud.get_report(db)
    return report_data



@app.get("/api/report/date/{date}", response_model=None)
async def get_report_by_date(date: str, db: Session = Depends(get_db)):
    """
    Get fire data by date.

    Parameters:
    - date (str): The date of the fire data to retrieve.
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing fire data.
    """
    report_data = crud.get_report_by_date(db, date)
    return report_data



@app.post("/api/report", response_model=None)
async def post_report(
    background_tasks: BackgroundTasks,
    latitude: str = Form(...),
    longitude: str = Form(...),
    message: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(None),
    from_nasa: bool = Form(...),
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
        "category": category,
        "image": image,
        "from_nasa": from_nasa
    }

    if image is not None:
        image_data = await report_data["image"].read()
        image_url = store_image(image_data)
        result = crud.post_report(db, report_data, image_url)
    else:
        image_url = ""
        result = crud.post_report(db, report_data, image_url)
    
    report_data["id"] = result.id
    report_data["image_url"] = result.image_url

    new_task = Job()
    jobs[new_task.uid] = new_task

    print(f"REQUESTING AI FOR {report_data}")

    background_tasks.add_task(start_ai_task, new_task.uid, report_data)

    return result


@app.get("/api/report/{report_id}", response_model=None)
async def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    """
    Get report data by its ID.

    Parameters:
    - report_id (int): The ID of the report data to retrieve.
    - db (Session): The database session to use.

    Returns:
    dict: A dictionary containing report data.
    """
    report_data = crud.get_report_by_id(db, report_id)
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
                       ai_message: str = Form(None),
                       new_image: UploadFile = File(None),
                       from_nasa: bool = Form(None),
                       db: Session = Depends(get_db)):
    """
    update report data
    """
    report_data = {
        "latitude": latitude,
        "longitude": longitude,
        "message": message,
        "ai_message": ai_message,
        "image": new_image,
        "from_nasa": from_nasa
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

@app.on_event("startup")
async def startup_event():
    app.state.executor = ProcessPoolExecutor()

@app.get("/api/report/updat/fire/{date}", response_model=None)
async def update_report_with_raw(date: str, db: Session = Depends(get_db)):
    report_data = crud.update_report_with_raw(db, date)
    return report_data

def start():
    """
    Start the FastAPI application using Uvicorn.
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
