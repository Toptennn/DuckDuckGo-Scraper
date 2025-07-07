from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from backend.scraper.duckduckgo import DuckDuckGoScraper

app = FastAPI(title="DuckDuckGo Scraper API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    normal_query: Optional[str] = ""
    exact_phrase: Optional[str] = ""
    semantic_query: Optional[str] = ""
    include_terms: Optional[str] = ""
    exclude_terms: Optional[str] = ""
    filetype: Optional[str] = ""
    site_include: Optional[str] = ""
    site_exclude: Optional[str] = ""
    intitle: Optional[str] = ""
    inurl: Optional[str] = ""
    max_pages: int = 20
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SearchResult(BaseModel):
    query: str
    pages_retrieved: int
    results: List[Dict]


def _add_normal_query(queries, parts):
    if queries.get("normal_query"):
        parts.append(queries["normal_query"])

def _add_exact_phrase(queries, parts):
    if queries.get("exact_phrase"):
        parts.append(f'"{queries["exact_phrase"]}"')

def _add_semantic_query(queries, parts):
    if queries.get("semantic_query"):
        parts.append(f'~"{queries["semantic_query"]}"')

def _add_include_terms(queries, parts):
    if queries.get("include_terms"):
        terms = [t.strip() for t in queries["include_terms"].split(',') if t.strip()]
        parts.extend([f"+{t}" for t in terms])

def _add_exclude_terms(queries, parts):
    if queries.get("exclude_terms"):
        terms = [t.strip() for t in queries["exclude_terms"].split(',') if t.strip()]
        parts.extend([f"-{t}" for t in terms])

def _add_filetype(queries, parts):
    if queries.get("filetype"):
        parts.append(f"filetype:{queries['filetype']}")

def _add_site_include(queries, parts):
    if queries.get("site_include"):
        parts.append(f"site:{queries['site_include']}")

def _add_site_exclude(queries, parts):
    if queries.get("site_exclude"):
        parts.append(f"-site:{queries['site_exclude']}")

def _add_intitle(queries, parts):
    if queries.get("intitle"):
        parts.append(f"intitle:{queries['intitle']}")

def _add_inurl(queries, parts):
    if queries.get("inurl"):
        parts.append(f"inurl:{queries['inurl']}")

def build_query(queries: dict) -> str:
    parts = []
    _add_normal_query(queries, parts)
    _add_exact_phrase(queries, parts)
    _add_semantic_query(queries, parts)
    _add_include_terms(queries, parts)
    _add_exclude_terms(queries, parts)
    _add_filetype(queries, parts)
    _add_site_include(queries, parts)
    _add_site_exclude(queries, parts)
    _add_intitle(queries, parts)
    _add_inurl(queries, parts)
    return " ".join(parts)

@app.post("/search", response_model=SearchResult)
def search(req: SearchRequest):
    queries = req.dict()
    max_pages = queries.pop("max_pages")
    start_date = queries.pop("start_date")
    end_date = queries.pop("end_date")
    final_query = build_query(queries)

    scraper = DuckDuckGoScraper()
    df, pages_retrieved = scraper.scrape(
        final_query,
        max_pages,
        headless=True,
        start_date=start_date,
        end_date=end_date,
    )
    results = df.to_dict(orient="records")
    return SearchResult(query=final_query, pages_retrieved=pages_retrieved, results=results)

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "DuckDuckGo Scraper API is running"}
