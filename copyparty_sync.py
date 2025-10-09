# copyparty_sync.py
import base64, time, hashlib, requests, re, os, json

_orig_request = requests.Session.request

def _debug_request(self, method, url, **kwargs):
    print(f"[copyparty][HTTP] {method.upper()} {url}")
    r = _orig_request(self, method, url, **kwargs)
    print(f"[copyparty][HTTP] -> {r.status_code}")
    return r

requests.Session.request = _debug_request

CONFIG_JSON_PATH = "copyparty_config.json"

_DEFAULT_CFG = {
    "COPYPARTY_BASE_URL": "https://jasondarby.com",
    "COPYPARTY_USERNAME": "",
    "COPYPARTY_PASSWORD": "",
    "COPYPARTY_DAV_PREFIX": "",
    "COPYPARTY_TIMEOUT_S": 10,
}

# ---------- config IO ----------
def _load_cfg() -> dict:
    try:
        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if not isinstance(cfg, dict):
                raise ValueError("config root not an object")
    except Exception:
        cfg = dict(_DEFAULT_CFG)
    for k, v in _DEFAULT_CFG.items():
        cfg.setdefault(k, v)
    return cfg

def _save_cfg(cfg: dict) -> bool:
    try:
        with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[copyparty] failed writing {CONFIG_JSON_PATH}: {e}")
        return False

# ---------- simple stream encryption (password-based) ----------
MAGIC = b"SPOONSV1"  # file tag + version
NONCE_LEN = 16

def _kdf(password: str, username: str) -> bytes:
    # Derive a 32-byte key from password + username (salt) using stdlib PBKDF2
    salt = (username or "spoons").encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", (password or "").encode("utf-8"), salt, 100_000, dklen=32)

def _keystream(key: bytes, nonce: bytes, nbytes: int) -> bytes:
    out = bytearray()
    ctr = 0
    while len(out) < nbytes:
        block = hashlib.sha256(key + nonce + ctr.to_bytes(8, "big")).digest()
        need = min(nbytes - len(out), len(block))
        out.extend(block[:need])
        ctr += 1
    return bytes(out)

def _encrypt_with_password(plaintext: bytes, username: str, password: str) -> bytes:
    key = _kdf(password, username)
    nonce = os.urandom(NONCE_LEN)
    ks = _keystream(key, nonce, len(plaintext))
    ct = bytes(a ^ b for a, b in zip(plaintext, ks))
    return MAGIC + nonce + ct

def _maybe_decrypt_download(blob: bytes, username: str, password: str) -> bytes:
    # Encrypted?
    if blob.startswith(MAGIC) and len(blob) >= len(MAGIC) + NONCE_LEN:
        nonce = blob[len(MAGIC):len(MAGIC)+NONCE_LEN]
        ct = blob[len(MAGIC)+NONCE_LEN:]
        key = _kdf(password, username)
        ks = _keystream(key, nonce, len(ct))
        pt = bytes(a ^ b for a, b in zip(ct, ks))
        return pt
    # Plain JSON fallback (legacy uploads)
    return blob

# ---------- small utils ----------
def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def _fresh_get(url: str, timeout: float):
    headers = _auth_headers()
    headers["Cache-Control"] = "no-cache"
    url_cb = f"{url}?_cb={int(time.time() * 1000)}"
    r = requests.get(url_cb, headers=headers, timeout=timeout)
    return r.status_code, r.content

def _dav_url(*parts):
    cfg = _load_cfg()
    base = (cfg.get("COPYPARTY_BASE_URL") or "").rstrip("/")
    dav  = (cfg.get("COPYPARTY_DAV_PREFIX") or "").rstrip("/")
    path = "/".join(str(p).strip("/") for p in parts if p is not None)
    return f"{base}{('/' + dav) if dav else ''}/{path}"

def _auth_headers():
    cfg = _load_cfg()
    u = cfg.get("COPYPARTY_USERNAME") or ""
    p = cfg.get("COPYPARTY_PASSWORD") or ""
    token = base64.b64encode(f"{u}:{p}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}

def _ensure_dir(*parts):
    cfg = _load_cfg()
    url = _dav_url(*parts)
    try:
        r = requests.request("MKCOL", url, headers=_auth_headers(), timeout=cfg["COPYPARTY_TIMEOUT_S"])
        if r.status_code not in (201, 405):
            print(f"[copyparty] MKCOL {url} -> {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"[copyparty] MKCOL failed {url}: {e}")

# ---------- public helpers used by UI ----------
def set_credentials(username: str, password: str) -> bool:
    cfg = _load_cfg()
    cfg["COPYPARTY_USERNAME"] = username or ""
    cfg["COPYPARTY_PASSWORD"] = password or ""
    return _save_cfg(cfg)

def set_user_folder(username: str) -> bool:
    cfg = _load_cfg()
    cfg["COPYPARTY_USERNAME"] = username or ""
    return _save_cfg(cfg)

def put_user_json(username: str, password: str) -> bool:
    if not username:
        print("[copyparty] put_user_json: empty username")
        return False
    cfg = _load_cfg()
    _ensure_dir("spoons"); _ensure_dir("spoons", username)
    url = _dav_url("spoons", username, "user.json")
    body = json.dumps({"username": username, "password": password}).encode("utf-8")
    try:
        hdr = _auth_headers(); hdr["Content-Type"] = "application/json"
        r = requests.put(url, data=body, headers=hdr, timeout=cfg["COPYPARTY_TIMEOUT_S"])
        ok = r.status_code in (200, 201, 204)
        if not ok:
            print(f"[copyparty] put_user_json failed {r.status_code}: {r.text[:200]}")
        else:
            print(f"[copyparty] wrote {url}")
        return ok
    except Exception as e:
        print(f"[copyparty] put_user_json error: {e}")
        return False

# ---------- data.json up/down (encrypted at rest on server) ----------
def upload_data_json():
    """
    Reads local ./data.json (plaintext), encrypts with password if present,
    and uploads to /<username>/data.json. Verifies by reading back the same bytes.
    """
    cfg = _load_cfg()
    username = (cfg.get("COPYPARTY_USERNAME") or "").strip()
    password = (cfg.get("COPYPARTY_PASSWORD") or "").strip()
    if not username:
        print("[copyparty] upload_data_json: no username configured")
        return

    url = _dav_url(username, "data.json")
    print(f"[copyparty] uploading to {url}")

    try:
        with open("data.json", "rb") as f:
            plain = f.read()
    except FileNotFoundError:
        print("[copyparty] no local data.json to upload")
        return
    except Exception as e:
        print(f"[copyparty] cannot read local data.json: {e}")
        return

    if password:
        upload_body = _encrypt_with_password(plain, username, password)
        ctype = "application/octet-stream"
        print("[copyparty] uploading ENCRYPTED data.json")
    else:
        upload_body = plain
        ctype = "application/json"
        print("[copyparty] WARNING: no password set; uploading PLAINTEXT")
        # I think we might be solving for an impossible edge case here
        # That is to say copy party should not accept an upload without a password besides account creation
        # so if this does happen you are fucked and idk what to do.
        print(
        """Dear user,

        If you are ever so unfortunate as to find yourself seeing this message, I am sorry.
        How you got into this situation is beyond my understanding, and I can only imagine what horrors await you.
        May God have mercy on your soul."""
        )

    target_hash = _sha256_bytes(upload_body)

    try:
        # delete then put
        try:
            dr = requests.delete(url, headers=_auth_headers(), timeout=cfg["COPYPARTY_TIMEOUT_S"])
            if dr.status_code not in (200, 204, 404):
                print(f"[copyparty] pre-delete returned {dr.status_code}: {dr.text[:200]}")
        except Exception as e:
            print(f"[copyparty] pre-delete error (ignored): {e}")

        hdr = _auth_headers(); hdr["Content-Type"] = ctype
        r = requests.put(url, data=upload_body, headers=hdr, timeout=cfg["COPYPARTY_TIMEOUT_S"])
        if r.status_code not in (200, 201, 204):
            print(f"[copyparty] upload failed {r.status_code}: {r.text[:200]}")
            return
        print(f"[copyparty] upload ok -> {url}")

        # verify bytes
        st, body = _fresh_get(url, cfg["COPYPARTY_TIMEOUT_S"])
        if st != 200:
            time.sleep(0.5)
            st, body = _fresh_get(url, cfg["COPYPARTY_TIMEOUT_S"])
        if st == 200 and _sha256_bytes(body) == target_hash:
            print("[copyparty] Upload integrity verified!")
        elif st == 200:
            time.sleep(0.6)
            st2, body2 = _fresh_get(url, cfg["COPYPARTY_TIMEOUT_S"])
            if st2 == 200 and _sha256_bytes(body2) == target_hash:
                print("[copyparty] verify ok after retry")
            else:
                print("[copyparty] WARNING: verify mismatch; remote appears stale")
        else:
            print(f"[copyparty] verify GET failed with {st}")
    except Exception as e:
        print(f"[copyparty] upload error: {e}")

def download_data_json_if_present():
    """
    Downloads /<username>/data.json.
    If encrypted (MAGIC header), decrypts with password; otherwise accepts plaintext.
    Writes plaintext to local ./data.json.
    Falls back once to /spoons/<username>/data.json for legacy.
    """
    cfg = _load_cfg()
    username = (cfg.get("COPYPARTY_USERNAME") or "").strip()
    password = (cfg.get("COPYPARTY_PASSWORD") or "").strip()
    if not username:
        print("[copyparty] download_data_json_if_present: no username configured")
        return False

    primary = _dav_url(username, "data.json")
    legacy  = _dav_url("spoons", username, "data.json")

    for idx, url in enumerate([primary, legacy]):
        try:
            r = requests.get(url, headers=_auth_headers(), timeout=cfg["COPYPARTY_TIMEOUT_S"])
            if r.status_code == 200:
                blob = r.content
                plain = _maybe_decrypt_download(blob, username, password)

                # sanity-check: must be JSON
                try:
                    json.loads(plain.decode("utf-8"))
                except Exception:
                    # don't trash a good local file if decrypt failed
                    with open("data.json.bad", "wb") as f:
                        f.write(blob)
                    print("[copyparty] ERROR: could not decode downloaded data.json "
                          "(wrong password or corrupt). Saved raw as data.json.bad")
                    return False

                with open("data.json", "wb") as fp:
                    fp.write(plain)
                print(f"[copyparty] downloaded {'encrypted' if blob.startswith(MAGIC) else 'plaintext'} data.json from {url}")
                if idx == 1:
                    print("[copyparty] NOTE: pulled from legacy /spoons/<user>/data.json; future uploads go to /<user>/data.json")
                return True

            if r.status_code in (401, 403, 404):
                continue  # try fallback
            else:
                print(f"[copyparty] download failed {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"[copyparty] download error from {url}: {e}")

    print("[copyparty] remote data.json not found")
    return False

# ---------- new/old account & creds helpers ----------
def _sanitize_stem(stem: str) -> str:
    stem = (stem or "").strip()
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem)
    if "." in stem:
        stem = stem.split(".", 1)[0]
    return stem or "user"

def put_new_user_cred(file_stem: str, username: str, password: str) -> bool:
    if not username:
        print("[copyparty] put_new_user_cred: empty username")
        return False
    cfg = _load_cfg()
    stem = _sanitize_stem(file_stem or username or "user")
    url  = _dav_url("new_users", stem)
    body = f"{username}:{password}".encode("utf-8")
    hdr  = _auth_headers(); hdr["Content-Type"] = "text/plain; charset=utf-8"
    try:
        r = requests.put(url, data=body, headers=hdr, timeout=cfg["COPYPARTY_TIMEOUT_S"])
        if r.status_code in (200, 201, 204):
            print(f"[copyparty] wrote {url}")
            time.sleep(3)  # <-- give backend time to process new user
            return True
        if r.status_code in (404, 409):
            try:
                _ensure_dir("new_users")
            except Exception:
                pass
            r2 = requests.put(url, data=body, headers=hdr, timeout=cfg["COPYPARTY_TIMEOUT_S"])
            ok = r2.status_code in (200, 201, 204)
            if ok:
                print(f"[copyparty] wrote {url}")
                time.sleep(3)  # <-- also delay here after successful retry
            else:
                print(f"[copyparty] put_new_user_cred failed {r2.status_code}: {r2.text[:200]}")
            return ok
        print(f"[copyparty] put_new_user_cred failed {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        print(f"[copyparty] put_new_user_cred error: {e}")
        return False

def get_current_user() -> str:
    return (_load_cfg().get("COPYPARTY_USERNAME") or "").strip()

def verify_credentials_and_access() -> bool:
    cfg = _load_cfg()
    u = (cfg.get("COPYPARTY_USERNAME") or "").strip()
    p = (cfg.get("COPYPARTY_PASSWORD") or "").strip()
    if not (u and p):
        return False
    url = _dav_url(u).rstrip("/") + "/"
    hdr = _auth_headers()
    hdr.update({"Depth": "0", "Content-Type": "text/xml"})
    body = '<?xml version="1.0" encoding="utf-8"?><propfind xmlns="DAV:"><prop><resourcetype/></prop></propfind>'
    try:
        r = requests.request("PROPFIND", url, headers=hdr, data=body, timeout=cfg["COPYPARTY_TIMEOUT_S"])
        return r.status_code in (200, 207)
    except Exception as e:
        print(f"[copyparty] verify_credentials_and_access error: {e}")
        return False

def clear_credentials(remove_active_file: bool = True) -> bool:
    cfg = _load_cfg()
    cfg["COPYPARTY_USERNAME"] = ""
    cfg["COPYPARTY_PASSWORD"] = ""
    ok = _save_cfg(cfg)
    if remove_active_file:
        try:
            os.remove(os.path.join("spoons", "active_user.txt"))
        except Exception:
            pass
    return ok

# --- precise login probe ---

def probe_login_status(username: str, password: str) -> str:
    """
    Return one of: "ok", "wrong_password", "no_such_user",
    "http_<code>", or "network_error".
    Uses a direct PROPFIND against /<username>/ with the given creds.
    """
    if not (username and password):
        return "network_error"

    cfg = _load_cfg()
    url = _dav_url(username).rstrip("/") + "/"

    # Build a one-off Basic header with provided creds (not from saved config)
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    hdr = {
        "Authorization": f"Basic {token}",
        "Depth": "0",
        "Content-Type": "text/xml",
    }
    body = '<?xml version="1.0" encoding="utf-8"?><propfind xmlns="DAV:"><prop><resourcetype/></prop></propfind>'

    try:
        r = requests.request("PROPFIND", url, headers=hdr, data=body, timeout=cfg["COPYPARTY_TIMEOUT_S"])
        sc = r.status_code
        if sc in (200, 207):
            return "ok"
        if sc == 401:
            return "wrong_password"
        if sc == 404:
            return "no_such_user"
        if sc == 403:
            # forbidden usually means auth failed anyway
            return "wrong_password"
        return f"http_{sc}"
    except Exception as e:
        print(f"[copyparty] probe_login_status error: {e}")
        return "network_error"
