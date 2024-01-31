import logging
import pathlib
from operator import itemgetter
from typing import Dict, List, Optional
import requests
from fastapi import FastAPI, Form, Request  # <- Formを追加
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
PATH_TEMPLATES = str(
    pathlib.Path(__file__).resolve().parent.parent / "backend/templates"
)
app = FastAPI()
templates = Jinja2Templates(directory=PATH_TEMPLATES)


@app.get("/")
async def read_root(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search/", response_class=HTMLResponse)  # noqa: F821
async def search_venue(
    request: Request,
    venues: List[str] = Form(...),
    query: Optional[str] = Form(None),
    year_from: Optional[int] = Form(None),  # 年の最小値
    year_to: Optional[int] = Form(None),  # 年の最大値
    citation_count_from: Optional[int] = Form(None),  # 引用数の最小値
    citation_count_to: Optional[int] = Form(None),  # 引用数の最大値
) -> Response:
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
        query_params: Dict[str, str] = {
            "query": query,
            "venue": venue,
            "fields": ",".join(fields),
        }
        # 'year' パラメータを <min>-<max> の形式で設定
        if year_from is not None and year_to is not None:
            query_params["year"] = f"{year_from}-{year_to}"
        elif year_from is not None:
            query_params["year"] = f"{year_from}-"
        elif year_to is not None:
            query_params["year"] = f"-{year_to}"

        # 'citationCount' パラメータを <min>-<max> の形式で設定
        if citation_count_from is not None and citation_count_to is not None:
            query_params[
                "citationCount"
            ] = f"{citation_count_from}-{citation_count_to}"
        elif citation_count_from is not None:
            query_params["citationCount"] = f"{citation_count_from}-"
        elif citation_count_to is not None:
            query_params["citationCount"] = f"-{citation_count_to}"
        r = requests.get(url=endpoint, params=query_params)
        if r.status_code != 200:
            logging.error(f"Error in API response for venue {venue}: {r.text}")
            continue  # Skip this venue and continue with the next one
        r_dict = r.json()
        total = r_dict.get("total", 0)
        total_count += total
        data = r_dict.get("data", [])
        all_papers.extend(data)

    if not all_papers:
        return JSONResponse(
            content={"error": "API request failed for all venues"},
            status_code=500,
        )
    for paper in all_papers:
        paper_id = paper.get("paperId", "")
        paper["url"] = f"https://www.semanticscholar.org/paper/{paper_id}"
    # Sort the aggregated results by 'influentialCitationCount'
    sorted_data = sorted(
        all_papers, key=itemgetter("influentialCitationCount"), reverse=True
    )

    # 結果の要約をログに記録
    logging.info(f"Total papers found across all venues: {total_count}")

    return templates.TemplateResponse(
        "template.html", {"request": request, "papers": sorted_data}
    )
