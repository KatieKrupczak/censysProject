import os
import json
import sqlite3
from typing import List, Optional, Dict, Any
SCHMEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  path TEXT NOT NULL,
  UNIQUE(ip, timestamp)
);
"""

# Initialize the database and ensures the directory for the database exists
def init_db(db_path: str):
  os.makedirs(os.path.dirname(db_path), exist_ok=True)
  with sqlite3.connect(db_path) as conn:
    conn.execute(SCHMEMA)
    conn.commit()

# Save a snapshot's JSON data to disk and record its metadata in the database
def save_snapshot(db_path: str, snap_dir: str, ip: str, timestamp: str, data: json) -> str:
  # Save JSON data to disk
  ip_dir = os.path.join(snap_dir, ip) # snapshots/<ip>/timestamp.json
  os.makedirs(ip_dir, exist_ok=True)

  safe_timestamp = timestamp.replace(":", "-")
  file_path = os.path.join(ip_dir, f"{safe_timestamp}.json")
  with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

  # Record metadata in the database
  with sqlite3.connect(db_path) as conn:
    try:
      conn.execute(
        "INSERT OR IGNORE INTO snapshots (ip, timestamp, path) VALUES (?, ?, ?)",
        (ip, timestamp, file_path)
      )
      conn.commit()
    except sqlite3.Error as e:
      raise RuntimeError(f"Database error: {str(e)}")
  
  return file_path

# List all distinct host IPs that have snapshots stored
def list_hosts(db_path: str) -> List[str]:
  with sqlite3.connect(db_path) as conn:
    rows = conn.execute("SELECT DISTINCT ip FROM snapshots ORDER BY ip ASC")
    hosts = [row[0] for row in rows.fetchall()]
  return hosts

# List all timestamps for snapshots of a specific host IP
def list_snapshots_for_host(db_path: str, ip: str) -> List[str]:
  with sqlite3.connect(db_path) as conn:
    rows = conn.execute(
      "SELECT timestamp FROM snapshots WHERE ip = ? ORDER BY timestamp ASC",
      (ip,)
    )
    timestamps = [row[0] for row in rows.fetchall()]
  return timestamps

# Retrieve the JSON data for a specific snapshot by host IP and timestamp
def get_snapshot_data(db_path: str, ip: str, timestamp: str) -> Optional[Dict[str, Any]]:
  with sqlite3.connect(db_path) as conn:
    row = conn.execute(
      "SELECT path FROM snapshots WHERE ip = ? AND timestamp = ?",
      (ip, timestamp)
    ).fetchone()
  if row is None:
    return None
  file_path = row[0]
  
  try:
    with open(file_path, "r") as f:
      data = json.load(f)
    return data
  except FileNotFoundError:
    return None