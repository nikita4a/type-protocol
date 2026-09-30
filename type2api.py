#!/usr/bin/env python3
"""
type2api.py — OpenAI-compatible gateway over type.com (protocol reverse).

Bootstrap (one human click):
  1. python type_client.py device-login --email <your-email>
  2. Open the printed URL in YOUR browser (Google session) -> "Continue with Google"
  3. Polling catches the token -> saved to ~/.type/credentials/<profile>.json
  4. python type2api.py  -> serves on :8311

Endpoints:
  GET  /v1/models          -> agents from cli/agents/list
  POST /v1/chat/completions -> thread pipeline over oRPC
       (message-send procedure is auto-discovered: the CLI bundle only calls
        read procedures, so this server probes send/create names live and
        logs which the server exposes with the user token)

Zero dependencies (stdlib). Token auto-refreshed via device-refresh grant.
"""
import json
import os
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import type_client  # noqa: E402

PORT = int(os.environ.get("TYPE2API_PORT", "8311"))
PROFILE = os.environ.get("TYPE_PROFILE", "default")
SEND_PROCEDURE_CANDIDATES = [
    "cli/threads/create",
    "cli/messages/create",
    "cli/threads/send",
    "cli/chat/send",
    "cli/agents/run",
    "cli/threads/message",
]


def get_state():
    state = type_client.load_profile()
    if not state or not state.get("accessToken"):
        raise SystemExit("no access token: run `python type_client.py device-login` first")
    if time.time() > state.get("expiresAt", 0):
        cfg = type_client.discover(state.get("server") or type_client.SERVER)
        state = type_client.refresh(cfg, state)
    return state


def orpc(state, procedure, args=None):
    return type_client.orpc_call(state, procedure, args)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/v1/models":
            state = get_state()
            st, agents = orpc(state, "cli/agents/list")
            items = []
            if st == 200 and isinstance(agents, dict):
                raw = agents.get("json") or agents
                for a in (raw.get("agents") or raw.get("data") or []):
                    items.append({"id": f"type-{a.get('handle') or a.get('id')}", "object": "model", "owned_by": "type.com"})
            self._send(200, {"object": "list", "data": items})
        elif self.path == "/health":
            self._send(200, {"ok": True, "profile": PROFILE})
        else:
            self._send(404, {"error": {"message": "not found"}})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._send(404, {"error": {"message": "not found"}})
            return
        length = int(self.headers.get("Content-Length") or 0)
        req = json.loads(self.rfile.read(length) or b"{}")
        messages = req.get("messages") or []
        prompt = messages[-1].get("content", "") if messages else ""
        state = get_state()
        # discover the send procedure once (logged; cache in .type/send_proc.json)
        cache = os.path.join(type_client.CRED_DIR, "send_proc.json")
        proc = None
        if os.path.exists(cache):
            proc = json.load(open(cache)).get("procedure")
        if not proc:
            for cand in SEND_PROCEDURE_CANDIDATES:
                st, body = orpc(state, cand, {"text": prompt})
                if st != 404:
                    proc = cand
                    json.dump({"procedure": proc}, open(cache, "w"))
                    print(f"[type2api] send procedure discovered: {proc} (HTTP {st})")
                    break
        if proc:
            st, body = orpc(state, proc, {"text": prompt, "messages": messages})
            content = (body.get("json") if isinstance(body, dict) else None) or body
            if isinstance(content, dict):
                content = content.get("content") or content.get("text") or json.dumps(content, ensure_ascii=False)
            else:
                content = str(content)
        else:
            st = 501
            content = (
                "type2api: token OK but no send procedure exposed to this scope; "
                "probed " + ", ".join(SEND_PROCEDURE_CANDIDATES) + ". "
                "See README: full message flow runs through local harnesses."
            )
        out = {
            "id": f"chatcmpl-type-{int(time.time()*1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.get("model", "type-default"),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": str(content)},
                    "finish_reason": "stop",
                }
            ],
            "_type_status": st,
        }
        self._send(200 if st == 200 else 200, out)  # OpenAI-compat envelope; status kept in _type_status


def main():
    get_state()  # fail fast if no token
    print(f"type2api on :{PORT} (profile {PROFILE})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
