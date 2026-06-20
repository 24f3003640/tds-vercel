from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import math
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

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

@app.post("/")
@app.post("/api/latency")
def analyze_latency(query: QueryData):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, '..', 'q-vercel-latency.json')
    
    with open(file_path, "r") as f:
        records = json.load(f)
        
    results = {}
    
    for region in query.regions:
        region_records = [r for r in records if r["region"].lower() == region.lower()]
        
        if not region_records:
            continue
            
        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime_pct"] for r in region_records]
        
        avg_latency = sum(latencies) / len(latencies)
        avg_uptime = sum(uptimes) / len(uptimes)
        breaches = sum(1 for lat in latencies if lat > query.threshold_ms)
        p95_latency = get_p95(latencies)
        
        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
        
    return results
