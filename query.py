#!/usr/bin/env python

from termcolor import colored

import json
import os
import requests


def clear():
    return lambda: os.system("clear")


def query_by_song(song):
    return f"""{{
  var(func: eq(song, "{song}")) {{
    ~playedSong {{
      v1 as uid
    }}
  }}
  setlist(func: uid(v1)) {{
    date
    venue: atVenue {{
      name: venue
    }}
 }}
}}"""


def query_by_location(location):
    return f"""{{
  var(func: anyofterms(location, "{location}")) {{
    ~isLocatedIn {{
      v1 as uid
    }}
  }}
  var(func: uid(v1)) {{
    ~atVenue {{
      v2 as uid
    }}
  }}
  songs(func: uid(v2), orderasc: date) {{
    songs: playedSong {{
        song
    }}
  }}
}}"""


def top_n_songs(n):
    return f"""{{
  var(func: type(song)) {{
    v1 as uid
    playcount as count(~playedSong)
  }}
  topSongs(func: uid(v1), orderdesc: val(playcount), first: {n}) {{
    song
    count: val(playcount)
  }}
}}"""


def top_n_encores(n):
    return f"""{{
  var(func: type(song)) {{
    v1 as uid
    playcount as count(~playedEncore)
  }}
  topEncores(func: uid(v1), orderdesc: val(playcount), first: {n}) {{
    song
    count: val(playcount)
  }}
}}"""


def top_n_venues(n):
    return f"""{{
  var(func: type(venue)) {{
    v1 as uid
    concerts as count(~atVenue)
  }}
  topVenues(func: uid(v1), orderdesc: val(concerts), first: {n}) {{
    venue
    count: val(concerts)
  }}
}}"""


def query_by_location_and_date(location, date):
    return f"""{{
  var(func: allofterms(location, "{location}")) {{
    ~isLocatedIn {{
      v1 as uid
    }}
  }}
  var(func: uid(v1)) {{
    ~atVenue @filter(ge(date, "{date}")) {{
      v2 as uid
    }}
  }}
  songs(func: uid(v2), orderasc: date) {{
    songs: playedSong {{
        song
    }}
  }}
}}"""


def query_internation_shows():
    return f"""{{
  var(func: regexp(location, /.*, X.*/)) {{
    ~isLocatedIn {{
      v1 as uid
    }}
  }}
  var(func: uid(v1)) {{
    ~atVenue {{
      v2 as uid
    }}
  }}
  var(func: uid(v2)) {{
    atVenue {{
      isLocatedIn {{
        v3 as uid
      }}
    }}
  }}
  locations(func: uid(v3), orderasc: location) {{
    name: location
  }}
}}"""


def query_data(q):
    headers = {
        "Content-Type": "application/graphql+-"
    }
    print(colored("query --> \n{}".format(q), "white"))
    r = requests.post("http://localhost:8080/query?timeout=20s&debug=true&ro=true&be=true", headers=headers, data=q)
    if r.status_code == 200:
        input()
        print(colored("result -->", "white"))
        print(colored(f"{json.dumps(r.json()['data'], indent=2, sort_keys=True)}", "green"))
    else:
        print(colored(f"{r.text}", "red"))


clear()()
print(colored("Which Concerts Included 'Me and My Uncle'?", "cyan"))
query_data(query_by_song("Me and My Uncle"))

input()
clear()()
print(colored("Which Songs Were Performed At the Civic Center?", "cyan"))
query_data(query_by_location("providence"))

input()
clear()()
print(colored("What Were the Top 5 Songs?", "cyan"))
query_data(top_n_songs(5))

input()
clear()()
print(colored("What Were the Top 5 Encores?", "cyan"))
query_data(top_n_encores(5))

input()
clear()()
print(colored("What Were the Top 5 Venues?", "cyan"))
query_data(top_n_venues(5))

input()
clear()()
print(colored("Which Songs Were Performed In Boston in 1994?", "cyan"))
query_data(query_by_location_and_date("boston", "1994"))

input()
clear()()
print(colored("Which International Locations Did They Play At?", "cyan"))
query_data(query_internation_shows())
