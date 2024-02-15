import logging
import pathlib
from operator import itemgetter
import requests
from fastapi import FastAPI, Form, Request  # <- Formを追加
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Dict, List, Tuple, Optional
import httpx
import asyncio
from starlette.responses import Response  # 必要に応じて

logging.basicConfig(level=logging.INFO)
PATH_TEMPLATES = str(
    pathlib.Path(__file__).resolve().parent.parent / "backend/templates"
)
app = FastAPI()
templates = Jinja2Templates(directory=PATH_TEMPLATES)


@app.get("/")
async def read_root(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


async def fetch_data_for_venue(
    client: httpx.AsyncClient, endpoint: str, query_params: dict
) -> dict:
    try:
        response = await client.get(endpoint, params=query_params)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error in API response: {response.text}")
            return {"total": 0, "data": []}
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return {"total": 0, "data": []}


@app.post("/search/", response_class=HTMLResponse)
async def search_venue(
    request: Request,
    venues: List[str] = Form(...),
    query: Optional[str] = Form(None),
    year_from: Optional[int] = Form(None),
    year_to: Optional[int] = Form(None),
    citation_count_from: Optional[int] = Form(None),
    citation_count_to: Optional[int] = Form(None),
) -> Response:
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    fields = [
        "title",
        "year",
        "referenceCount",
        "citationCount",
        "influentialCitationCount",
        "isOpenAccess",
        "fieldsOfStudy",
        "authors",
        "venue",
    ]
    all_papers = []
    total_count = 0

    async with httpx.AsyncClient() as client:
        tasks = []
        for venue in venues:
            query_params = {
                "query": query,
                "venue": venue,
                "fields": ",".join(fields),
            }
            if year_from is not None and year_to is not None:
                query_params["year"] = f"{year_from}-{year_to}"
            elif year_from is not None:
                query_params["year"] = f"{year_from}-"
            elif year_to is not None:
                query_params["year"] = f"-{year_to}"

            if (
                citation_count_from is not None
                and citation_count_to is not None
            ):
                query_params["citationCount"] = (
                    f"{citation_count_from}-{citation_count_to}"
                )
            elif citation_count_from is not None:
                query_params["citationCount"] = f"{citation_count_from}-"
            elif citation_count_to is not None:
                query_params["citationCount"] = f"-{citation_count_to}"

            tasks.append(fetch_data_for_venue(client, endpoint, query_params))

        results = await asyncio.gather(*tasks)
        for result in results:
            total_count += result.get("total", 0)
            all_papers.extend(result.get("data", []))

    if not all_papers:
        return JSONResponse(
            content={"error": "API request failed for all venues"},
            status_code=500,
        )

    for paper in all_papers:
        paper_id = paper.get("paperId", "")
        paper["url"] = f"https://www.semanticscholar.org/paper/{paper_id}"

    sorted_data = sorted(
        all_papers, key=itemgetter("citationCount"), reverse=True
    )

    logging.info(f"Total papers found across all venues: {total_count}")

    return templates.TemplateResponse(
        "template.html", {"request": request, "papers": sorted_data}
    )
