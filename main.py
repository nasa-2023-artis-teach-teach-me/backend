import uvicorn
from fastapi import Depends, FastAPI, UploadFile, File
from functools import lru_cache
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from map import get_transaction_count
from database import SessionLocal
import crud, schemas, config
from typing import List
from s3 import store_image
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@lru_cache()
def get_settings():
    return config.Settings()

@app.get("/")
async def count(settings: Annotated[config.Settings, Depends(get_settings)]):
    count = get_transaction_count(settings.MAP_KEY)
    return {"message": "Hello World", "transaction count": count}

@app.get("/api/fire/{fire_id}", response_model=None)
async def get_fire(fire_id: int,db: Session = Depends(get_db)):
    fire_data = crud.get_fire(db,fire_id)
    return fire_data

@app.get("/api/fire/date/{date}", response_model=None)
async def get_fire_by_date(date: str,db: Session = Depends(get_db)):
    fire_data = crud.get_fire_by_date(db,date)
    return fire_data


@app.post("/api/report", response_model=None)
async def post_report(report_data: schemas.ReportCreate ,db: Session = Depends(get_db)):
    report_data = crud.post_report(db,report_data)
    return report_data

@app.get("/api/report/{report_id}", response_model=None)
async def get_report(report_id: int,db: Session = Depends(get_db)):
    report_data = crud.get_report(db,report_id)
    return report_data

# upload image to minio with status code 200
@app.post("/api/image")
async def upload_image(image: UploadFile = File(...)):
    image_data = await image.read()
    image_url = store_image(image_data)
    return {"url": image_url}


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
