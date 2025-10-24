from typing import Dict, Any, List, Tuple, Set

ServiceKey = Tuple[int, str]  # (port, protocol)

# Create an index of services from the snapshot data.
# The index maps (port, protocol) to the service details.
def index_services(snapshot: Dict[str, Any]) -> Dict[ServiceKey, Dict[str, Any]]:
  services_index = {}
  services = snapshot.get("services", []) or []
  
  for service in services:
    port = service.get("port")
    protocol = service.get("protocol")
    if port is not None and protocol is not None:
      key = (int(port), str(protocol))
      services_index[key] = service
  return services_index

def diff_service(svc1: Dict[str, Any], svc2: Dict[str, Any]) -> Dict[str, Any]:
  changes = {}
  
  def cmp(path: str, val1: Any, val2: Any):
    if val1 != val2:
      changes[path] = {"from": val1, "to": val2}
    
  # flat fields
  cmp("status", svc1.get("status"), svc2.get("status"))

  # software sub-object
  software1 = svc1.get("software", {}) or {}
  software2 = svc2.get("software", {}) or {}
  for field in ["vendor", "product", "version"]:
    cmp(f"software.{field}", software1.get(field), software2.get(field))
  
  # tls sub-object
  tls1 = svc1.get("tls", {}) or {}
  tls2 = svc2.get("tls", {}) or {}
  for field in ["version", "cipher", "cert_fingerprint_sha256"]:
    cmp(f"tls.{field}", tls1.get(field), tls2.get(field))
  
  # vulnerabilities as sets
  vulns1 = set(svc1.get("vulnerabilities", []) or [])
  vulns2 = set(svc2.get("vulnerabilities", []) or [])
  added_vulns = vulns2 - vulns1
  removed_vulns = vulns1 - vulns2

  if added_vulns: changes["vulnerabilities_added"] = list(added_vulns)
  if removed_vulns: changes["vulnerabilities_removed"] = list(removed_vulns)

  return changes

def diff_snapshots(snap1: Dict[str, Any], snap2: Dict[str, Any]) -> Dict[str, Any]:
  index1 = index_services(snap1)
  index2 = index_services(snap2)

  keys1 = set(index1.keys())
  keys2 = set(index2.keys())

  added = sorted(keys2 - keys1)
  removed = sorted(keys1 - keys2)
  common = keys1 & keys2

  result = {
    "services_added": [{"port": p, "protocol": proto} for (p, proto) in added],
    "services_removed": [{"port": p, "protocol": proto} for (p, proto) in removed],
    "services_modified": []
  }

  for key in sorted(common):
    svc1 = index1[key]
    svc2 = index2[key]
    changes = diff_service(svc1, svc2)
    if changes:
      port, protocol = key
      result["services_modified"].append({
        "port": port,
        "protocol": protocol,
        "changes": changes
      })
  
  return result