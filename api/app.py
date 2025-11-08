from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, status
from pydantic import BaseModel
import time
import sqlite3
from pathlib import Path

app = FastAPI()

# simple in-memory store
ingest_jobs = set()

from .models import SessionLocal, Ingest, init_db
from sqlalchemy.exc import IntegrityError


@app.on_event("startup")
def startup_event():
    # initialize DB / tables
    init_db()


class IngestRequest(BaseModel):
    url: str


def summarize_job(url: str):
    """Simulate background ingestion (non-blocking) with DB persistence"""
    print(f"\n [STARTED] {url}")

    # use SQLAlchemy session to check/insert
    session = SessionLocal()
    try:
        existing = session.get(Ingest, url)
        if existing:
            print(f"URL already present in db, skipping: {url}")
            return

        ts = time.time()
        ingest = Ingest(url=url, status="WIP", content=None, created_at=ts, updated_at=ts)
        session.add(ingest)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Concurrent insert detected, skipping: {url}")
            return
    finally:
        session.close()

    from .agent_util import main
    import asyncio
    result = asyncio.run(
        main(
            user_id="random", 
            session_id="random", 
            url = url
    ))    

    # update the DB row with result
    session = SessionLocal()
    try:
        row = session.get(Ingest, url)
        if row:
            row.status = "DONE"
            row.content = result
            row.updated_at = time.time()
            session.add(row)
            session.commit()
    finally:
        session.close()

    print(f"\n [COMPLETED] {url} {result}")


@app.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_url(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(summarize_job, request.url)
    return {"status": "accepted", "url": request.url}


@app.get("/ingest")
async def get_ingest_status(url: str = Query(...)):
    # read status from DB via SQLAlchemy session
    session = SessionLocal()
    try:
        row = session.get(Ingest, url)
        if not row:
            raise HTTPException(status_code=404, detail="URL not found")
        return {"status": row.status, "url": url, "content": row.content}
    finally:
        session.close()
