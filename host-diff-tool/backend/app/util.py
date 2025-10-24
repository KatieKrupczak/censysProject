import re
from typing import Tuple, Optional

# host_<ip>_<timestamp>.json
# Expect filenames like: host_125.199.235.74_2025-09-10T03-00-00Z.json
PAT = re.compile(r"host_(?P<ip>\d+\.\d+\.\d+\.\d+)_(?P<ts>[^.]+)\.json")

def parse_filename_fallback(filename: str) -> Tuple[Optional[str], Optional[str]]:
  match = PAT.match(filename)
  if not match:
    return None, None
  ip = match.group("ip")
  timestamp = match.group("ts").replace("-", ":", 2)  # revert - to : in time portion
  return ip, timestamp