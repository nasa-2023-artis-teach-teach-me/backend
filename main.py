import uvicorn
from fastapi import Depends, FastAPI
from functools import lru_cache
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from map import get_transaction_count
from database import SessionLocal
import crud, schemas, config
from typing import List 
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
async def fire(fire_id: int,db: Session = Depends(get_db)):
    fire_data = crud.get_fire(db,fire_id)
    return fire_data

@app.get("/api/fire/date/{date}", response_model=None)
async def get_fire_by_date(date: str,db: Session = Depends(get_db)):
    fire_data = crud.get_fire_by_date(db,date)
    return fire_data

def start():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
