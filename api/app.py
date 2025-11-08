from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, status
from pydantic import BaseModel
import time
import sqlite3
from pathlib import Path

app = FastAPI()

# simple in-memory store
ingest_jobs = set()

DB_PATH = Path(__file__).resolve().parent.parent / "db.sqlite"


def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingests (
                url TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                content TEXT,
                created_at REAL,
                updated_at REAL
            )
        """)
        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup_event():
    # ensure parent dir exists (usually the repo root) and init DB
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_db()


class IngestRequest(BaseModel):
    url: str


def summarize_job(url: str):
    """Simulate background ingestion (non-blocking) with DB persistence"""
    print(f"\n [STARTED] {url}")

    # open a short-lived connection and check if url already exists
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT status FROM ingests WHERE url = ?", (url,))
    row = cur.fetchone()
    if row:
        print(f"URL already present in db, skipping: {url}")
        conn.close()
        return

    ts = time.time()
    cur.execute(
        "INSERT INTO ingests (url, status, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (url, "WIP", None, ts, ts),
    )
    conn.commit()
    conn.close()

    from .agent_util import main
    import asyncio
    result = asyncio.run(
        main(
            user_id="random", 
            session_id="random", 
            url = url
    ))    

    # update the DB row with result
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "UPDATE ingests SET status = ?, content = ?, updated_at = ? WHERE url = ?",
        ("DONE", result, time.time(), url),
    )
    conn.commit()
    conn.close()

    print(f"\n [COMPLETED] {url} {result}")



@app.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_url(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(summarize_job, request.url)
    return {"status": "accepted", "url": request.url}


@app.get("/ingest")
async def get_ingest_status(url: str = Query(...)):
    # read status from DB (fallback to 404 if not present)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT status, content FROM ingests WHERE url = ?", (url,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"status": row["status"], "url": url, "content": row["content"]}
