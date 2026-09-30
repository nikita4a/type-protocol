import json
import urllib.request

toks = [t.strip() for t in open('C:/Users/User/Downloads/gh_tokens.txt', encoding='utf-8', errors='replace') if t.strip().startswith('ghp_')]
valid = []
for tok in toks:
    req = urllib.request.Request(
        'https://api.github.com/user',
        headers={'Authorization': 'Bearer ' + tok, 'User-Agent': 'research'},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            u = json.load(r)
            valid.append({"login": u["login"], "token": tok})
    except Exception:
        pass
print("total valid:", len(valid), "of", len(toks))
for v in valid[:5]:
    print("VALID:", v["login"])
json.dump(valid, open("C:/Users/User/tmp/typerev/valid_toks.json", "w"))
