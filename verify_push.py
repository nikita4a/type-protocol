import json
import urllib.request

pat = json.load(open("C:/Users/User/tmp/typerev/valid_gh.json"))[0]["token"].strip()
req = urllib.request.Request(
    "https://api.github.com/repos/emberlogic053/type-protocol/git/trees/main",
    headers={"Authorization": "Bearer " + pat, "User-Agent": "research"},
)
with urllib.request.urlopen(req, timeout=30) as r:
    tree = json.load(r)
    print("remote files:", " ".join(x["path"] for x in tree["tree"]))
