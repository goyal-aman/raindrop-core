from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, status
from pydantic import BaseModel
import time

app = FastAPI()

# simple in-memory store
ingest_jobs = set()

class IngestRequest(BaseModel):
    url: str


def fake_ingest_job(url: str):
    """Simulate background ingestion (non-blocking)"""
    print(f"Fake ingest started: {url}")
    time.sleep(5)  # pretend ingestion takes time
    ingest_jobs.add(url)  # mark done (for demo)
    print(f"Fake ingest completed: {url}")

def summarize_job(url: str):
    """Simulate background ingestion (non-blocking)"""
    print(f"\n [STARTED] {url}")
    from .agent_util import main
    import asyncio
    result = asyncio.run(
        main(
            user_id="random", 
            session_id="random", 
            url = url
    ))    

    print(f"\n [COMPLETED] {url} {result}")


@app.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_url(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(summarize_job, request.url)
    return {"status": "accepted", "url": request.url}


@app.get("/ingest")
async def get_ingest_status(url: str = Query(...)):
    print(f"DEBUG GET: {url} {ingest_jobs}")
    if url not in ingest_jobs:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"status": "work completed", "url": url}
