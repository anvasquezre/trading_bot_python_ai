import json
import logging
from typing import Dict, Optional

import pandas as pd
import settings
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from middleware import model_predict
from pydantic import BaseModel


class UserId(BaseModel):
    id: str | None = None


# { "id": "string | int" }

app = FastAPI(
    title="Finance API",
    description=""" Finance data retrieval """,
    version="0.1.0",
)


@app.post("/test/")
async def test(id: UserId):
    """Test jobs predictions"""
    """Get jobs predictions"""
    logging.debug("ejecutar modelo...")
    result = None
    id = str(id.id)
    if id:
        result = model_predict(id)
        logging.debug("modelo ejecutado...")
    return result
