import logging
import pathlib
from operator import itemgetter
from typing import Dict, List

import requests
from fastapi import FastAPI, Form, Request  # <- Formを追加
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
PATH_TEMPLATES = str(pathlib.Path(__file__).resolve().parent.parent / "backend/templates")
app = FastAPI()
templates = Jinja2Templates(directory=PATH_TEMPLATES)


@app.get("/")
async def read_root(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search/")
async def search_venue(venues: List[str] = Form(...)) -> JSONResponse:
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    fields = (
        "title",
        "year",
        "referenceCount",
        "citationCount",
        "influentialCitationCount",
        "isOpenAccess",
        "fieldsOfStudy",
        "authors",
        "venue",
    )
    all_papers = []
    total_count = 0

    for venue in venues:
        params: Dict[str, str] = {"venue": venue, "fields": ",".join(fields)}
        r = requests.get(url=endpoint, params=params)
        if r.status_code != 200:
            logging.error(f"Error in API response for venue {venue}: {r.text}")
            continue  # Skip this venue and continue with the next one

        r_dict = r.json()
        total = r_dict.get("total", 0)
        total_count += total
        data = r_dict.get("data", [])
        all_papers.extend(data)

        # Optional: If you want to include some delay between API calls to avoid hitting rate limits
        # time.sleep(1)

    if not all_papers:
        return JSONResponse(content={"error": "API request failed for all venues"}, status_code=500)

    # Sort the aggregated results by 'influentialCitationCount'
    sorted_data = sorted(all_papers, key=itemgetter("influentialCitationCount"), reverse=True)

    # 結果の要約をログに記録
    logging.info(f"Total papers found across all venues: {total_count}")

    return JSONResponse(content={"total": total_count, "sorted_data": sorted_data})
