import json
import logging
import pathlib
from typing import Dict

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
async def search_venue(venue: str = Form(...)) -> JSONResponse:
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
    params: Dict[str, str] = {"venue": venue, "fields": ",".join(fields)}

    # APIへのリクエスト情報をログに記録
    logging.info(f"Sending request to {endpoint} with parameters: {params}")

    r = requests.get(url=endpoint, params=params)

    # レスポンスのステータスコードをログに記録
    logging.info(f"Received response with status code {r.status_code}")

    if r.status_code != 200:
        logging.error(f"Error in API response: {r.text}")
        return JSONResponse(
            content={"error": "API request failed", "details": r.text}, status_code=r.status_code
        )

    r_dict = json.loads(r.text)
    total = r_dict["total"]
    data = r_dict["data"]
    sorted_data = sorted(data, key=lambda x: int(x["influentialCitationCount"]), reverse=True)

    # 結果の要約をログに記録
    logging.info(f"Total papers found: {total}")

    return JSONResponse(content={"total": total, "sorted_data": sorted_data})
