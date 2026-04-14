from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import time

from app.database import SessionLocal, engine, Base
from app.models import Item


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    max_retries = 10
    for attempt in range(max_retries):
        try:
            engine.connect()
            print("Connected to DB, creating tables...")
            Base.metadata.create_all(bind=engine)
            break
        except Exception:
            print("Waiting for DB...")
            time.sleep(3)


@app.get("/", response_class=HTMLResponse)
def read_items(request: Request, db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return templates.TemplateResponse(
        request=request,
        name="items.html",
        context={"request": request, "items": items}
    )


@app.post("/add", response_class=HTMLResponse)
def create_item(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
):
    item = Item(title=title, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    items = db.query(Item).all()
    return templates.TemplateResponse(
        request=request,
        name="items.html",
        context={"request": request, "items": items}
    )
