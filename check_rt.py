import json

s = json.load(open("C:/Users/User/.type/credentials/default.json", encoding="utf-8"))
rt = s.get("refreshToken")
print("type:", type(rt).__name__)
if isinstance(rt, str):
    print("str, len", len(rt), "head:", rt[:30])
elif isinstance(rt, dict):
    print("dict keys:", list(rt.keys()), "value:", str(rt.get("value"))[:30])
