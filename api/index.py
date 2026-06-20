from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from typing import List
import json
import math
import os

app = FastAPI()

class QueryData(BaseModel):
    regions: List[str]
    threshold_ms: float

def get_p95(data):
    if not data: return 0.0
    s = sorted(data)
    k = (len(s) - 1) * 0.95
    f = math.floor(k)
    c = math.ceil(k)
    if f == c: return s[int(k)]
    return s[int(f)] * (c - k) + s[int(c)] * (k - f)

# 1. Brute-force handler for the OPTIONS pre-flight request
@app.options("/{path:path}")
def options_handler(path: str, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {"status": "ok"}

# 2. The main POST endpoint with brute-forced headers
@app.post("/")
@app.post("/api/latency")
def analyze_latency(query: QueryData, response: Response):
    # Manually attach CORS headers so Vercel can't strip them
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access
