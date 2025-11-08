# Inline

<!-- LOGO PLACEHOLDER -->

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)

Inline is a small FastAPI service that accepts a URL to be processed asynchronously and returns an AI-generated summary for that URL.

Overview
--------
Inline is a minimal web API that ingests a URL and creates an AI-generated summary of the linked content. The service exposes two HTTP endpoints:

- POST /ingest  — enqueue a URL for summarization (background job)
- GET /ingest   — query the status and (when ready) the generated summary for a URL

This project uses a local SQLite DB (db.sqlite) to persist ingest jobs and integrates with Google ADK / google-genai for the underlying summarization agent.

Quick links
-----------
- Main application module: api/app.py
- Background agent runner: run.py (summarize logic lives under summarize_agent/)

Author / Creator
----------------
Author: Aman G — https://github.com/goyal-aman

Requirements
------------
- Python 3.10+ (recommended 3.11)
- SQLite (db.sqlite is used by default and included in repo)
- API Keys from google ai studio (Other LLM Support not available at this moment)
- Install project Python dependencies: pip install -r requirements.txt

Environment variables
---------------------
The application will run with the default SQLite DB without extra env vars, but the summarization agent depends on Google Cloud credentials. Recommended environment variables:

- GOOGLE_API_KEY
- FIRECRAWL_API_KEY

How it works (short)
--------------------
1. Client sends POST /ingest with JSON body {"url": "https://..."}.
2. The FastAPI app enqueues a background task (summarize_job) and returns HTTP 202 Accepted immediately.
3. The background job persists a row in SQLite, calls into the summarize agent (summarize_agent via Google ADK / google-genai) and then updates the DB entry with status and generated summary.
4. Clients poll GET /ingest?url=<url> to read the status and summary (when ready).

Run locally (recommended)
-------------------------
1. Create and activate a virtual environment (macOS):

    python -m venv .venv
    source .venv/bin/activate

2. Install dependencies:

    pip install -r requirements.txt

3. Ensure env vars are set

4. Start the API with uvicorn (from repository root):

    uvicorn api.app:app --host 0.0.0.0 --port 8000

Note: you asked for "unicorn api.app:app" — the correct command is uvicorn (one 'n').

Endpoints and examples
----------------------
1) Enqueue a URL for summarization (async)

Request

curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/article"}'

Response (HTTP 202)

{
  "status": "accepted",
  "url": "https://example.com/article"
}

2) Check status / fetch generated summary

Request

curl -s "http://localhost:8000/ingest?url=https://example.com/article"

Possible responses
- 200 OK (when job exists):
  {
    "status": "WIP" | "DONE",
    "url": "https://example.com/article",
    "content": null | "The AI-generated summary text..."
  }
- 404 Not Found (when URL not present):
  {
    "detail": "URL not found"
  }

Notes about URLs
----------------
The service uses the URL string as a key in the SQLite DB. If you send duplicate URLs concurrently, the application guards against duplicate inserts.

Database
--------
A local SQLite file (db.sqlite) is used by default. The FastAPI app calls init_db() on startup to ensure tables exist. No manual migration step is required for the current minimal schema.

Development tips
----------------
- The background summarization logic lives in summarize_agent/ and is invoked via run.py and api/agent_util.py
- Logging is intentionally quiet in the repository; enable DEBUG-level logging in run.py or the ASGI server if you need deeper tracing.

Contributing
------------
This project is open source — contributions, issues, and pull requests are welcome. Please:

- Open an issue for bugs or feature requests
- Fork the repo and submit a PR with tests and clear commit messages

License
-------
This project is released under the Apache License 2.0. See the bundled LICENSE file for details.

Acknowledgements
----------------
Thanks for checking out this project. I appreciate contributions and improvements from the community.

