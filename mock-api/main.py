from fastapi import FastAPI, APIRouter, Query, HTTPException, status
from typing import Optional, List, Dict
import uvicorn
import json

app = FastAPI()
router = APIRouter()


@router.get("/_cat/indices/{date_pattern}", response_model=List[Dict])
async def indexes(
    date_pattern: str,
    v: Optional[str] = Query(None),
    h: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    bytes: Optional[str] = Query(None),
):
    """
    Mock endpoint for:
    GET /_cat/indices/*<YYYY>*<MM>*<DD>?v&h=index,pri.store.size,pri&format=json&bytes=b
    """
    # date_pattern = *<YYYY>*<MM>*<DD>
    date_file = date_pattern.replace("*", "-")[1:]
    filename = f"{date_file}.json"

    # Load local file if present; empty list otherwise
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except Exception as e:
        data = []

    return data


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
