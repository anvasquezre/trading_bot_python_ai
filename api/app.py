
import json
from typing import Dict, Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from middleware import model_predict
import logging
from pydantic import BaseModel
import settings
import pandas as pd



class UserId(BaseModel):
    id: str | None = None

# { "id": "string | int" }

app = FastAPI(title="Finance API",
              description=''' Finance data retrieval ''',
              version="0.1.0",
              )


@app.post("/test/")
async def test(id: UserId):
    '''Test jobs predictions'''
    '''Get jobs predictions'''
    logging.debug("ejecutar modelo...")
    result= None
    id = str(id.id)
    if id:
        result = model_predict(id)
        logging.debug("modelo ejecutado...")
    return result