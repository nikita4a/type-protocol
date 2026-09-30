import json
import random
import string
import sys
import urllib.request

sys.path.insert(0, ".")
import type_client

CTX = type_client._CTX


def mailtm(path, body=None, method="POST"):
    req = urllib.request.Request(
        "https://api.mail.tm" + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return json.load(r)


domains = mailtm("/domains", method="GET")
domains = domains["hydra:member"] if isinstance(domains, dict) else domains
domain = [d["domain"] for d in domains if d.get("isActive", True)][0]
local = "gw" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
address = local + "@" + domain
password = "Tp" + "".join(random.choices(string.ascii_letters + string.digits, k=12)) + "!9"
mailtm("/accounts", {"address": address, "password": password})
jwt = mailtm("/token", {"address": address, "password": password})["token"]
json.dump({"address": address, "password": password, "jwt": jwt}, open("mailbox.json", "w"))
print("mailbox:", address)
