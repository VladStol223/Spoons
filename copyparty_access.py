# copyparty_access.py
# Minimal, defensive Copyparty access (register / username check / upload / download)
import os, json, time, base64, hashlib, uuid, getpass
from datetime import datetime
import requests

# -----------------------------
# Configuration & sanitization
# -----------------------------
CONFIG_PATH = os.path.join("spoons", "copyparty_config.json")

# DEV: set a hardcoded password during development; set to None to disable
DEV_HARDCODED_PASSWORD = "poopinmabutt"   # ← set to None later when you want env/prompt

DEFAULT_CFG = {
    "base_url": "https://jasondarby.com",
    "dav_prefix": "",
    "timeout_s": 10,
    "verify_tls": True,
    "remote_root": "spoons",
    "username": None
}

COMMON_TLDS = [".com", ".org", ".net", ".io", ".dev", ".app", ".co", ".us", ".uk", ".ca", ".de", ".ai"]

def _ensure_file():
    d = os.path.dirname(CONFIG_PATH)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    if not os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(DEFAULT_CFG, indent=2))

def _load_cfg():
    _ensure_file()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_cfg(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(cfg, indent=2))

def _sanitize_base_url(raw: str) -> str:
    """Clamp to 'scheme://host' and strip any junk after the host.
       Also trim any garbage after a known TLD (e.g., '.comE' → '.com')."""
    raw = (raw or "").strip()
    if not raw:
        return ""

    # ensure scheme
    if not raw.startswith("http://") and not raw.startswith("https://"):
        raw = "https://" + raw

    # split scheme and the rest
    scheme, rest = raw.split("://", 1)
    # take only host (drop any path)
    host = rest.split("/", 1)[0]

    # clamp host to a known TLD if present
    lowered = host.lower()
    for tld in COMMON_TLDS:
        if tld in lowered:
            # keep everything up to the first occurrence of that TLD
            base, _sep, _tail = lowered.partition(tld)
            # rebuild host with original casing up to that point + tld
            # (use indices from lowered to slice original 'host')
            cut_index = lowered.index(tld) + len(tld)
            host = host[:cut_index]
            break

    # final output is scheme://host (no trailing slash)
    return f"{scheme}://{host}".rstrip("/")

_cfg = _load_cfg()
RAW_BASE_URL = _cfg.get("base_url") or ""
BASE_URL = _sanitize_base_url(RAW_BASE_URL)
DAV_PREFIX = (_cfg.get("dav_prefix") or "").strip("/")
TIMEOUT_S = int(_cfg.get("timeout_s", 10))
VERIFY_TLS = bool(_cfg.get("verify_tls", True))
REMOTE_ROOT = (_cfg.get("remote_root") or "spoons").strip("/")
USERNAME = _cfg.get("username")  # may be None pre-register

if BASE_URL != (RAW_BASE_URL or "").strip().rstrip("/"):
    print(f"[copyparty] WARNING: sanitized base_url from {RAW_BASE_URL!r} to {BASE_URL!r}")

# -----------------------------
# Auth helpers
# -----------------------------
def _get_password():
    # Priority: DEV hardcoded → env var → prompt
    if DEV_HARDCODED_PASSWORD:
        return DEV_HARDCODED_PASSWORD
    pw = os.environ.get("SPOONS_COPYPARTY_PASSWORD")
    if pw:
        return pw.strip()
    try:
        return getpass.getpass("Copyparty password: ").strip()
    except Exception:
        # last resort visible input (if running without TTY, return empty)
        try:
            return input("Copyparty password (visible): ").strip()
        except Exception:
            return ""

def _auth_headers():
    token = base64.b64encode(f"{USERNAME or ''}:{_get_password() or ''}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}

def _dav_url(*parts):
    path = "/".join(str(p).strip("/") for p in parts if p is not None)
    return f"{BASE_URL}{('/' + DAV_PREFIX) if DAV_PREFIX else ''}/{path}"

# -----------------------------
# Small HTTP helpers
# -----------------------------
def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _mkcol(url: str):
    if not url.endswith("/"):
        url = url + "/"
    try:
        r = requests.request("MKCOL", url, headers=_auth_headers(), timeout=TIMEOUT_S, verify=VERIFY_TLS)
        if r.status_code not in (201, 405):
            print(f"[copyparty] MKCOL {url} -> {r.status_code} {(r.text or '')[:160]}")
        return r.status_code in (201, 405)
    except Exception as e:
        print(f"[copyparty] MKCOL error {url}: {e}")
        return False

def _ensure_dirs(*remote_dirs):
    acc = []
    for d in remote_dirs:
        acc.append(d)
        _mkcol(_dav_url(*acc))

def _fresh_get(url: str):
    headers = _auth_headers()
    headers["Cache-Control"] = "no-cache"
    url_cb = f"{url}?_cb={int(time.time()*1000)}"
    return requests.get(url_cb, headers=headers, timeout=TIMEOUT_S, verify=VERIFY_TLS)

# -----------------------------
# Index ops
# -----------------------------
def _remote_index_url():
    return _dav_url(REMOTE_ROOT, "users", "index", "usernames.json")

def fetch_user_index() -> dict:
    try:
        r = _fresh_get(_remote_index_url())
        if r.status_code == 200:
            try:
                return json.loads(r.text)
            except Exception:
                return {}
        elif r.status_code in (404, 401, 403):
            return {}
        return {}
    except Exception:
        return {}

def write_user_index(idx: dict) -> bool:
    try:
        _ensure_dirs(REMOTE_ROOT, "users", "index")
        data = json.dumps(idx, separators=(",", ":")).encode("utf-8")
        r = requests.put(_remote_index_url(), data=data,
                         headers={**_auth_headers(), "Content-Type": "application/json"},
                         timeout=TIMEOUT_S, verify=VERIFY_TLS)
        ok = r.status_code in (200, 201, 204)
        if not ok:
            print(f"[copyparty] PUT index {r.status_code}: {(r.text or '')[:200]}")
        return ok
    except Exception as e:
        print(f"[copyparty] write index error: {e}")
        return False

# -----------------------------
# User provision & public API
# -----------------------------
def _new_user_id() -> str:
    return uuid.uuid4().hex

def _remote_user_data_url(user_id: str):
    return _dav_url(REMOTE_ROOT, "users", "by-id", user_id, "data.json")

def _remote_user_meta_url(user_id: str):
    return _dav_url(REMOTE_ROOT, "users", "by-id", user_id, "meta.json")

def provision_user_remote(username: str, local_data_path: str) -> str:
    user_id = _new_user_id()
    # ensure dirs: /spoons/users/by-id/<user_id>/
    _ensure_dirs(REMOTE_ROOT, "users", "by-id", user_id)

    # meta.json
    meta = {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "status": "active"
    }
    try:
        r = requests.put(_remote_user_meta_url(user_id),
                         data=json.dumps(meta, separators=(",", ":")).encode("utf-8"),
                         headers={**_auth_headers(), "Content-Type": "application/json"},
                         timeout=TIMEOUT_S, verify=VERIFY_TLS)
        ok_meta = r.status_code in (200, 201, 204)
        if not ok_meta:
            print(f"[copyparty] PUT meta {r.status_code}: {(r.text or '')[:200]}")
    except Exception as e:
        print(f"[copyparty] PUT meta error: {e}")
        ok_meta = False

    # data.json (local or {})
    body = b"{}"
    if os.path.isfile(local_data_path):
        try:
            with open(local_data_path, "rb") as fp:
                body = fp.read()
        except Exception:
            body = b"{}"

    try:
        r2 = requests.put(_remote_user_data_url(user_id),
                          data=body,
                          headers={**_auth_headers(), "Content-Type": "application/json"},
                          timeout=TIMEOUT_S, verify=VERIFY_TLS)
        ok_data = r2.status_code in (200, 201, 204)
        if not ok_data:
            print(f"[copyparty] PUT data {r2.status_code}: {(r2.text or '')[:200]}")
    except Exception as e:
        print(f"[copyparty] PUT data error: {e}")
        ok_data = False

    if not (ok_meta and ok_data):
        print("[copyparty] provision failed; aborting user creation")
        return ""

    # index update
    idx = fetch_user_index()
    idx[str(username).lower()] = user_id
    if not write_user_index(idx):
        return ""
    return user_id

# --- public helpers used by main.py ---
def username_taken(username: str) -> bool:
    idx = fetch_user_index()
    return str(username).lower() in idx

def register_and_write_username(username: str, local_data_path: str) -> str:
    uid = provision_user_remote(username, local_data_path)
    if not uid:
        return ""
    cfg = _load_cfg()
    cfg["username"] = username
    _save_cfg(cfg)
    return uid

def download_data_json_if_present(local_data_path: str) -> bool:
    cfg = _load_cfg()
    username = (cfg.get("username") or "").lower()
    if not username:
        return False
    idx = fetch_user_index()
    uid = idx.get(username)
    if not uid:
        return False
    url = _remote_user_data_url(uid)
    try:
        r = requests.get(url, headers=_auth_headers(), timeout=TIMEOUT_S, verify=VERIFY_TLS, stream=True)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(local_data_path) or ".", exist_ok=True)
            with open(local_data_path, "wb") as fp:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        fp.write(chunk)
            print("[copyparty] downloaded remote data.json")
            return True
        else:
            print(f"[copyparty] download status {r.status_code}: {(r.text or '')[:160]}")
            return False
    except Exception as e:
        print(f"[copyparty] download error: {e}")
        return False

def upload_data_json(local_data_path: str):
    cfg = _load_cfg()
    username = (cfg.get("username") or "").lower()
    if not username:
        print("[copyparty] no username set; skipping upload")
        return
    idx = fetch_user_index()
    uid = idx.get(username)
    if not uid:
        print("[copyparty] no user in index; skipping upload")
        return
    url = _remote_user_data_url(uid)
    try:
        try:
            requests.delete(url, headers=_auth_headers(), timeout=TIMEOUT_S, verify=VERIFY_TLS)
        except Exception:
            pass
        with open(local_data_path, "rb") as fp:
            r = requests.put(url, data=fp, headers={**_auth_headers(), "Content-Type": "application/json"},
                             timeout=TIMEOUT_S, verify=VERIFY_TLS)
        if r.status_code not in (200, 201, 204):
            print(f"[copyparty] upload failed {r.status_code}: {(r.text or '')[:200]}")
            return
        print(f"[copyparty] upload ok -> {url}")
        rb = _fresh_get(url)
        if rb.status_code == 200:
            try:
                if _sha256_bytes(rb.content) == _sha256_file(local_data_path):
                    print("[copyparty] verify ok")
                else:
                    print("[copyparty] WARNING: verify mismatch; remote appears stale")
            except Exception:
                pass
    except FileNotFoundError:
        print("[copyparty] no local data.json to upload")
    except Exception as e:
        print(f"[copyparty] upload error: {e}")

# --- optional: quick diagnostics when run directly ---
def diagnose():
    print("=== copyparty_access diagnostics ===")
    print("config file:", os.path.abspath(CONFIG_PATH))
    print("raw base_url:", repr(RAW_BASE_URL))
    print("sanitized   :", repr(BASE_URL))
    print("dav_prefix  :", repr(DAV_PREFIX))
    print("remote_root :", repr(REMOTE_ROOT))
    print("verify_tls  :", VERIFY_TLS)
    print("timeout_s   :", TIMEOUT_S)
    # try a few sanity calls
    try:
        r = requests.get(f"{BASE_URL}/", headers=_auth_headers(), timeout=TIMEOUT_S, verify=VERIFY_TLS)
        print("GET BASE ->", r.status_code)
    except Exception as e:
        print("GET BASE EXC:", e)
    try:
        url = _dav_url(REMOTE_ROOT)
        if not url.endswith("/"): url += "/"
        r = requests.request("MKCOL", url, headers=_auth_headers(), timeout=TIMEOUT_S, verify=VERIFY_TLS)
        print("MKCOL root ->", r.status_code)
    except Exception as e:
        print("MKCOL EXC:", e)
    print("=== end diagnostics ===")

if __name__ == "__main__":
    diagnose()
