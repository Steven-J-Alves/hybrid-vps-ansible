#!/usr/bin/env python3
"""Flatten tf-outputs.json (Terraform output -json format) into a plain
key=value JSON that ansible-playbook -e '@extra-vars.json' can consume,
adding tailscale_auth_key from the environment.
"""
import json
import os

d = json.load(open("tf-outputs.json"))
flat = {k: v["value"] for k, v in d.items()}
flat["tailscale_auth_key"] = os.environ["TAILSCALE_AUTH_KEY"]
json.dump(flat, open("extra-vars.json", "w"), indent=2)
print("extra vars keys:", list(flat.keys()))
