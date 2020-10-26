#!/usr/bin/env python

import hashlib
import json
import os
import re
import requests

from datetime import datetime


def convert_rdf():
    re_venue = re.compile("VENUE\\s+>>>>\\s+(.*)")
    re_loc = re.compile("LOCATION\\s+>>>>\\s+(.*)")
    re_date = re.compile("DATE\\s+>>>>\\s+(.*)")
    re_song = re.compile("SONG\\s+>>>>\\s+(.*)")
    re_encore = re.compile("ENCORE\\s+>>>>\\s+(.*)")

    rdf = ""
    with open(os.path.join("dataset", "setlist.txt")) as f:
        for line in f.readlines():
            if re_venue.search(line):
                venue = re_venue.search(line)
                venue_id = hashlib.sha256(str(venue.group(1)).encode("UTF-8")).hexdigest()
                rdf += f"""\t\t<_:{venue_id}> <dgraph.type> "venue" .\n"""
                rdf += f"""\t\t<_:{venue_id}> <venue> "{venue.group(1)}" .\n"""
            elif re_loc.search(line):
                loc = re_loc.search(line)
                loc_id = hashlib.sha256(str(loc.group(1)).encode("UTF-8")).hexdigest()
                rdf += f"""\t\t<_:{loc_id}> <dgraph.type> "location" .\n"""
                rdf += f"""\t\t<_:{loc_id}> <location> "{loc.group(1)}" .\n"""
                rdf += f"""\t\t<_:{venue_id}> <isLocatedIn> <_:{loc_id}> .\n"""
            elif re_date.search(line):
                date = re_date.search(line)
                value = datetime.strptime(str(date.group(1)), "%m/%d/%y")
                date_id = hashlib.sha256(str(date.group(1)).encode("UTF-8")).hexdigest()
                rdf += f"""\t\t<_:{date_id}> <dgraph.type> "setlist" .\n"""
                rdf += f"""\t\t<_:{date_id}> <date> "{value.strftime("%Y-%m-%dT%H:%M:%S.%f%z")}" .\n"""
                rdf += f"""\t\t<_:{date_id}> <atVenue> <_:{venue_id}> .\n"""
            elif re_song.search(line):
                song = re_song.search(line)
                song_id = hashlib.sha256(str(song.group(1)).encode("UTF-8")).hexdigest()
                rdf += f"""\t\t<_:{song_id}> <dgraph.type> "song" .\n"""
                rdf += f"""\t\t<_:{song_id}> <song> "{song.group(1)}" .\n"""
                rdf += f"""\t\t<_:{date_id}> <playedSong> <_:{song_id}> .\n"""
            elif re_encore.search(line):
                encore = re_encore.search(line)
                encore_id = hashlib.sha256(str(encore.group(1)).encode("UTF-8")).hexdigest()
                rdf += f"""\t\t<_:{encore_id}> <dgraph.type> "song" .\n"""
                rdf += f"""\t\t<_:{encore_id}> <song> "{encore.group(1)}" .\n"""
                rdf += f"""\t\t<_:{date_id}> <playedEncore> <_:{encore_id}> .\n"""
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
upload_data(convert_rdf())
