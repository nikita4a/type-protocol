import base64
import json
import urllib.error
import urllib.parse
import urllib.request

import ssl

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

state = json.load(open("C:/Users/User/.type/credentials/default.json", encoding="utf-8"))
assertion = state["assertion"]
token_endpoint = state["tokenEndpoint"]
resource = state["resource"]
print("kind:", state["kind"], "| resource field:", resource)

# decode JWT header+payload
for part, label in ((0, "header"), (1, "payload")):
    seg = assertion.split(".")[part]
    seg += "=" * (-len(seg) % 4)
    print(f"jwt {label}:", json.dumps(json.loads(base64.urlsafe_b64decode(seg)))[:600])


def try_exchange(label, extra):
    form = {"assertion": assertion, "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer"}
    form.update(extra)
    req = urllib.request.Request(
        token_endpoint,
        data=urllib.parse.urlencode(form).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            body = json.load(r)
            short = {k: (v[:24] + "…" if isinstance(v, str) and len(v) > 24 else v) for k, v in body.items()}
            print(label, "-> 200 OK", short)
            return body
    except urllib.error.HTTPError as e:
        print(label, "-> HTTP", e.code, e.read().decode()[:160])
        return None


try_exchange("A: no resource", {})
try_exchange("B: resource=issuer", {"resource": state["issuer"]})
try_exchange("C: resource as-is", {"resource": resource})
