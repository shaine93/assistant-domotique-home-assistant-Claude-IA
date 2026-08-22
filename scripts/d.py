import json, urllib.request

with open("/home/lolufe/assistant/config.json", encoding="utf-8") as f:
    cfg = json.load(f)

ha_url = cfg["ha_url"].rstrip("/")
ha_token = cfg["ha_token"]

def call(method, path, body=None):
    req = urllib.request.Request(
        ha_url + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + ha_token, "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

status, body = call("GET", "/api/hassio/addons")
print("GET /api/hassio/addons ->", status)
print(body[:4000])
