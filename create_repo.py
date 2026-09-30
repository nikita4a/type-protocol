import json
import sys
import urllib.error
import urllib.request

pat = json.load(open("C:/Users/User/tmp/typerev/valid_gh.json"))[0]["token"]
req = urllib.request.Request(
    "https://api.github.com/user/repos",
    data=json.dumps(
        {
            "name": "type-protocol",
            "private": True,
            "description": "type.com reverse: browserless protocol signup/refresh/device client (Python, stdlib)",
        }
    ).encode(),
    headers={
        "Authorization": "Bearer " + pat,
        "User-Agent": "research",
        "Accept": "application/vnd.github+json",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
        print("repo created:", body.get("full_name"), "|", body.get("html_url"))
        print("OK " + body.get("full_name", ""))
except urllib.error.HTTPError as e:
    print("create HTTP", e.code, e.read().decode()[:200])
