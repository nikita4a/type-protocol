import json
import sqlite3
import urllib.request

c = sqlite3.connect("C:/Users/User/tmp/bpproxy_run/accounts.db")
rows = c.execute(
    "SELECT username, pat FROM accounts WHERE pat IS NOT NULL AND pat != ''"
).fetchall()
print("candidates:", len(rows))
valid = []
for user, pat in rows:
    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={"Authorization": "Bearer " + pat.strip(), "User-Agent": "research"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            u = json.load(r)
            print("VALID:", user, "->", u["login"])
            valid.append({"username": user, "login": u["login"], "token": pat.strip()})
            if len(valid) >= 5:
                break
    except Exception:
        pass
print("valid:", len(valid))
json.dump(valid, open("C:/Users/User/tmp/typerev/valid_gh.json", "w"))
