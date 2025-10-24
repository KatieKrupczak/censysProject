# primitives for building routes, handling file uploads, and managing HTTP exceptions
from fastapi import FastAPI, UploadFile, File, HTTPException
# lets the frontend access the backend API from a different origin
from fastapi.middleware.cors import CORSMiddleware
# request/response models with data validation and serialization
from pydantic import BaseModel
from typing import List
import json, os

from .storage import init_db, save_snapshot, list_hosts, list_snapshots_for_host, get_snapshot_json
from .diff import diff_snapshots
from .util import parse_filename_fallback

app = FastAPI() # create FastAPI application instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; adjust in production XXX
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath("./data"))
DB_PATH = os.path.join(DATA_DIR, "snapshots.db")
SNAP_DIR = os.path.join(DATA_DIR, "snapshots")

os.makedirs(SNAP_DIR, exist_ok=True)
init_db(DB_PATH)

class HostList(BaseModel):
    hosts: List[str]

class SnapshotList(BaseModel):
    ip: str
    timestamps: List[str]

@app.get("/api/health") # health check endpoint to confirm API is running
def health():
    return {"status": "ok"}

@app.post("/api/upload") # endpoint to upload snapshot files
async def upload_snapshot(file: UploadFile = File(...)):
    # try to read and parse the uploaded file as JSON
    try:
        content = await file.read()
        data = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # extract ip and timestamp from JSON data
    ip = data.get("ip")
    timestamp = data.get("timestamp")

    if not ip or not timestamp:
        # try to parse from filename as fallback
        ip2, timestamp2 = parse_filename_fallback(file.filename or "")
        ip = ip or ip2
        timestamp = timestamp or timestamp2

    if not ip or not timestamp:
        raise HTTPException(status_code=400, detail="Missing 'ip' or 'timestamp' in JSON/filename")

    # save the snapshot to disk and database
    saved_path = save_snapshot(DB_PATH, SNAP_DIR, ip, timestamp, data)

    # return success response with details
    return {"ok": True, "ip": ip, "timestamp": timestamp, "path": saved_path}

@app.get("/api/hosts", response_model=HostList) # endpoint to list all hosts with snapshots
def get_hosts():
    hosts = list_hosts(DB_PATH) # returns a sorted list of distict host IPs from SQLite DB
    return HostList(hosts=hosts)

@app.get("/api/snapshots/{ip}", response_model=SnapshotList) # endpoint to list snapshots for a specific host
def get_snapshots(ip: str):
    timestamps = list_snapshots_for_host(DB_PATH, ip) # returns sorted list of timestamps for the given host IP
    return SnapshotList(ip=ip, timestamps=timestamps)

@app.get("/api/snapshot/{ip}/{timestamp}") # endpoint to retrieve a specific snapshot's JSON data
def get_snapshot(ip: str, timestamp: str):
    data = get_snapshot_json(DB_PATH, ip, timestamp)
    if data is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return data

@app.get("/api/diff/{ip}/{ts1}/{ts2}") # endpoint to diff two snapshots for a host XXX
def diff_snapshot(ip: str, ts1: str, ts2: str):
    a_json = get_snapshot_json(DB_PATH, ip, ts1)
    b_json = get_snapshot_json(DB_PATH, ip, ts2)
    if a_json is None or b_json is None:
        raise HTTPException(status_code=404, detail="One or both snapshots not found")
    diff = diff_snapshots(a_json, b_json)
    return {"ip": ip, "ts1": ts1, "ts2": ts2, "diff": diff}