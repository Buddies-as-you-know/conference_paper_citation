import json
from typing import Dict
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
import pathlib
from logging import getLogger
logger = getLogger(__name__)
PATH_TEMPLATES = str(
    pathlib.Path(__file__).resolve() \
        .parent.parent / "backend/templates"
)
app = FastAPI()
templates = Jinja2Templates(directory=PATH_TEMPLATES)

@app.get("/")
async def read_root(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search/")
async def search_venue(venue: str) -> JSONResponse:
    
    endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search/bulk'
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
    params : Dict[str, str] = {'venue': venue, 'fields': ",".join(fields)}
    logger.info(params)
    r = requests.get(url=endpoint, params=params)
    print(r)
    r_dict = json.loads(r.text)
    total = r_dict["total"]
    data = r_dict["data"]
    sorted_data = sorted(data, key=lambda x: int(x["influentialCitationCount"]), reverse=True)

    return JSONResponse(content={"total": total, "sorted_data": sorted_data})
