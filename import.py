#!/usr/bin/env python

import hashlib
import json
import os
import requests

from datetime import datetime


def load_rdf():
    rdf = ""
    with open(os.path.join("dataset", "setlist.rdf")) as f:
        for line in f.readlines():
            rdf += f"""\t\t{line}\n"""
    return rdf


def clear():
    print("clearing database...")
    op = {"drop_all": True}
    r = requests.post("http://localhost:8080/alter", data=json.dumps(op))
    if r.status_code == 200:
        print(f"[*] {r.json()['data']['message']}")
    else:
        print("[!] {}".format(r.status_code))


def upload_schema():
    schema = ""
    with open("dgraph.schema") as f:
        for line in f.readlines():
            schema += line

    headers = {
        "Content-Type": "application/rdf"
    }
    print("updating schema...")
    r = requests.post("http://localhost:8080/alter", headers=headers, data=schema)
    if r.status_code == 200:
        print(f"[*] {r.json()['data']['message']}")
    else:
        print("[!] {}".format(r.status_code))


def upload_data(rdf):
    mutation = f"""{{
        set {{
            {rdf}
        }}
    }}"""
    headers = {
        "Content-Type": "application/rdf"
    }
    print("uploading setlist...")
    r = requests.post("http://localhost:8080/mutate?commitNow=true", headers=headers, data=mutation)
    if r.status_code == 200:
        print(f"[*] {r.json()['data']['message']}")
    else:
        print("[!] {}".format(r.status_code))


clear()
upload_schema()
upload_data(load_rdf())
