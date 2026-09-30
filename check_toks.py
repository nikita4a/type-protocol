import json
import urllib.request

toks = [t.strip() for t in open('C:/Users/User/Downloads/gh_tokens.txt', encoding='utf-8', errors='replace') if t.strip().startswith('ghp_')]
print('tokens:', len(toks))
valid = []
for tok in toks[:12]:
    req = urllib.request.Request(
        'https://api.github.com/user',
        headers={'Authorization': 'Bearer ' + tok, 'User-Agent': 'research'},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            u = json.load(r)
            print('VALID:', u['login'], '| scopes available')
            valid.append((u['login'], tok))
            if len(valid) >= 2:
                break
    except Exception as e:
        print('dead:', str(e)[:50])
json.dump(valid, open('C:/Users/User/tmp/typerev/valid_toks.json', 'w'))
print('saved', len(valid))
