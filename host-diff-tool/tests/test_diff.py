import json
from backend.app.diff import diff_snapshots

def test_diff_added_service_and_status_change():
  # Snapshot A: only HTTP:80 with 200
  snap_a = {
    "timestamp": "2025-09-10T03:00:00Z",
    "ip": "125.199.235.74",
    "services": [
        {"port": 80, "protocol": "HTTP", "status": 200,
          "software": {"vendor": "microsoft", "product": "internet_information_services", "version": "8.5"}}
    ],
    "service_count": 1,
  }

  # Snapshot B: HTTP:80 becomes 301, HTTPS:443 appears with vuln
  snap_b = {
    "timestamp": "2025-09-15T08:49:45Z",
    "ip": "125.199.235.74",
    "services": [
      {"port": 80, "protocol": "HTTP", "status": 301,
        "software": {"vendor": "microsoft", "product": "internet_information_services", "version": "8.5"}},
      {"port": 443, "protocol": "HTTPS", "status": 200,
        "software": {"vendor": "microsoft", "product": "asp.net"},
        "tls": {
          "version": "tlsv1_2",
          "cipher": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
          "cert_fingerprint_sha256": "8e2f33d95cacbda559f4d4c65a0c4ea774735720130aac88efcd0c599ab452b9"
        },
        "vulnerabilities": ["CVE-2023-99999"]}
    ],
    "service_count": 2,
  }

  diff = diff_snapshots(snap_a, snap_b)

  # Added HTTPS:443
  assert {"port": 443, "protocol": "HTTPS"} in diff["services_added"]
  # No removed services
  assert diff["services_removed"] == []

  # Changed HTTP:80 — status 200 -> 301
  changed = [c for c in diff["services_modified"] if c["port"] == 80 and c["protocol"] == "HTTP"]
  assert len(changed) == 1
  assert changed[0]["changes"]["status"] == {"from": 200, "to": 301}

def test_diff_removed_service_and_software_change():
  # A has 22/SSH and 80/HTTP; B removes 22 and changes software.version on 80
  snap_a = {
    "services": [
      {"port": 22, "protocol": "SSH", "status": 200,
        "software": {"vendor": "openssh", "product": "openssh", "version": "9.2p1"}},
      {"port": 80, "protocol": "HTTP", "status": 200,
        "software": {"vendor": "nginx", "product": "nginx", "version": "1.24.0"}}
    ]
  }
  snap_b = {
    "services": [
      {"port": 80, "protocol": "HTTP", "status": 200,
        "software": {"vendor": "nginx", "product": "nginx", "version": "1.25.3"}}
    ]
  }

  diff = diff_snapshots(snap_a, snap_b)

  # SSH removed
  assert {"port": 22, "protocol": "SSH"} in diff["services_removed"]

  # HTTP changed version
  changed = [c for c in diff["services_modified"] if c["port"] == 80 and c["protocol"] == "HTTP"]
  assert len(changed) == 1
  assert changed[0]["changes"]["software.version"] == {"from": "1.24.0", "to": "1.25.3"}

def test_vuln_added_and_removed():
  a = { "services": [
    {"port": 443, "protocol": "HTTPS", "vulnerabilities": ["CVE-2023-0001", "CVE-2023-0002"]}
  ]}
  b = { "services": [
    {"port": 443, "protocol": "HTTPS", "vulnerabilities": ["CVE-2023-0002", "CVE-2024-9999"]}
  ]}

  diff = diff_snapshots(a, b)
  changed = [c for c in diff["services_modified"] if c["port"] == 443][0]["changes"]

  assert sorted(changed["vulnerabilities_added"]) == ["CVE-2024-9999"]
  assert sorted(changed["vulnerabilities_removed"]) == ["CVE-2023-0001"]