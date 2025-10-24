import json
import os
import sqlite3
import tempfile
from backend.app.storage import init_db, save_snapshot, list_hosts, list_snapshots_for_host, get_snapshot_json

def test_storage_write_and_read_roundtrip():
  with tempfile.TemporaryDirectory() as tmp:
    db_path = os.path.join(tmp, "snapshots.db")
    snap_dir = os.path.join(tmp, "snapshots")
    os.makedirs(snap_dir, exist_ok=True)

    init_db(db_path)

    # Save a snapshot
    ip = "203.0.113.10"
    ts = "2025-09-10T03:00:00Z"
    data = {
        "timestamp": ts,
        "ip": ip,
        "services": [{"port": 80, "protocol": "HTTP", "status": 200}]
    }

    path = save_snapshot(db_path, snap_dir, ip, ts, data)
    assert os.path.exists(path), "JSON file should be written to disk"

    # Indexing should expose host and timestamp
    hosts = list_hosts(db_path)
    assert ip in hosts

    tss = list_snapshots_for_host(db_path, ip)
    assert ts in tss

    # Reading back JSON should match
    loaded = get_snapshot_json(db_path, ip, ts)
    assert loaded is not None
    assert loaded["ip"] == ip
    assert loaded["timestamp"] == ts
    assert loaded["services"][0]["port"] == 80

def test_insert_or_ignore_duplicate_safe():
  with tempfile.TemporaryDirectory() as tmp:
    db_path = os.path.join(tmp, "snapshots.db")
    snap_dir = os.path.join(tmp, "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    init_db(db_path)

    ip = "198.51.100.7"
    ts = "2025-09-11T00:00:00Z"
    data = {"ip": ip, "timestamp": ts, "services": []}

    # first insert
    save_snapshot(db_path, snap_dir, ip, ts, data)
    # duplicate insert should not raise, thanks to INSERT OR IGNORE
    save_snapshot(db_path, snap_dir, ip, ts, data)

    # exactly one row in DB for that (ip, ts)
    with sqlite3.connect(db_path) as conn:
        n = conn.execute("SELECT COUNT(*) FROM snapshots WHERE ip=? AND timestamp=?", (ip, ts)).fetchone()[0]
    assert n == 1
