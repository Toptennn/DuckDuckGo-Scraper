# DuckDuckGo Scraper Web App

This project exposes the original Streamlit scraper as a REST API with **FastAPI** and a simple **Next.js** frontend.

## Backend

The API lives in `backend/main.py` and provides a `/search` endpoint which accepts the same search parameters as the Streamlit version. Start the backend with:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Frontend

A minimal Next.js client is located in `frontend/`. After installing Node.js run:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000` and use the form to query the API.

## Notes

The scraping logic is unchanged and still relies on Selenium. Ensure Chrome and the correct driver are available when running the backend.
