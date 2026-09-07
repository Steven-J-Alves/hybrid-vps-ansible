#!/usr/bin/env python3
"""Pull tf-outputs.json artifact from the most recent successful eca:apply job
in the hybrid-networking-terraform project (main branch).

Requires:
  GITLAB_API_TOKEN  read_api scope
Writes:
  ./tf-outputs.json
"""
import json
import os
import sys
import urllib.request

TOKEN = os.environ["GITLAB_API_TOKEN"]
UPSTREAM = (
    "kriolu-kloud%2Fdevops%2Fnetworking%2Fhybrid-architecture"
    "%2Fhybrid-networking-terraform"
)
BASE = "https://gitlab.kriolu-kloud.cv/api/v4"


def api(path: str):
    req = urllib.request.Request(f"{BASE}{path}", headers={"PRIVATE-TOKEN": TOKEN})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def download(path: str, dest: str):
    req = urllib.request.Request(f"{BASE}{path}", headers={"PRIVATE-TOKEN": TOKEN})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())


jobs = api(f"/projects/{UPSTREAM}/jobs?scope[]=success&per_page=50")
if not isinstance(jobs, list):
    print("API returned non-list:", jobs, file=sys.stderr)
    sys.exit(2)

job_id = next(
    (j["id"] for j in jobs if j.get("name") == "eca:apply" and j.get("ref") == "main"),
    None,
)
if not job_id:
    print("no successful eca:apply job on main", file=sys.stderr)
    sys.exit(1)

print(f"pulling artifact from job {job_id}")
download(f"/projects/{UPSTREAM}/jobs/{job_id}/artifacts/tf-outputs.json", "tf-outputs.json")
size = os.path.getsize("tf-outputs.json")
print(f"tf-outputs.json downloaded ({size} bytes)")
