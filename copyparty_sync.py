# copyparty_sync.py
import base64
import time
import hashlib
import requests
from datetime import datetime
from copyparty_config import (
    COPYPARTY_BASE_URL, COPYPARTY_DAV_PREFIX,
    COPYPARTY_USERNAME, COPYPARTY_PASSWORD,
    COPYPARTY_USER_FOLDER, COPYPARTY_TIMEOUT_S,
)

def _dav_url(*parts):
    base = COPYPARTY_BASE_URL.rstrip("/")
    dav  = (COPYPARTY_DAV_PREFIX or "").rstrip("/")
    path = "/".join(str(p).strip("/") for p in parts if p is not None)
    return f"{base}{('/' + dav) if dav else ''}/{path}"

def _auth_headers():
    token = base64.b64encode(f"{COPYPARTY_USERNAME or ''}:{COPYPARTY_PASSWORD or ''}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _fresh_get(url: str, timeout: float):
    headers = _auth_headers()
    headers["Cache-Control"] = "no-cache"
    url_cb = f"{url}?_cb={int(time.time() * 1000)}"
    r = requests.get(url_cb, headers=headers, timeout=timeout)
    return r.status_code, r.content

def _ensure_user_folder():
    if not COPYPARTY_USER_FOLDER:
        return
    for parts in [("spoons",), ("spoons", COPYPARTY_USER_FOLDER)]:
        url = _dav_url(*parts)
        try:
            r = requests.request("MKCOL", url, headers=_auth_headers(), timeout=COPYPARTY_TIMEOUT_S)
            if r.status_code not in (201, 405):
                print(f"[copyparty] MKCOL {url} -> {r.status_code} {r.text[:200]}")
        except Exception as e:
            print(f"[copyparty] MKCOL failed {url}: {e}")

def _cleanup_old_versions():
    if not COPYPARTY_USER_FOLDER:
        return
    url_dir = _dav_url("spoons", COPYPARTY_USER_FOLDER).rstrip("/") + "/"
    try:
        r = requests.request(
            "PROPFIND", url_dir,
            headers={**_auth_headers(), "Depth": "1", "Content-Type": "text/xml"},
            data='''<?xml version="1.0" encoding="utf-8" ?>
<D:propfind xmlns:D="DAV:"><D:prop><D:href/></D:prop></D:propfind>''',
            timeout=COPYPARTY_TIMEOUT_S,
        )
        if r.status_code not in (200, 207):
            return
        from xml.etree import ElementTree as ET
        ns = {"D": "DAV:"}
        hrefs = [el.text or "" for el in ET.fromstring(r.text).findall(".//D:response/D:href", ns)]
        targets = [h for h in hrefs if h.endswith(".json") and "data.json-" in h]
        for h in targets:
            target = h if h.startswith("http") else (url_dir.rstrip("/") + "/" + h.strip("/").split("/")[-1])
            try:
                dr = requests.delete(target, headers=_auth_headers(), timeout=COPYPARTY_TIMEOUT_S)
                if dr.status_code not in (200, 204):
                    pass
            except Exception:
                pass
    except Exception:
        pass

def upload_data_json():
    """Delete remote data.json, PUT local one, cache-busted verify, then tidy sidecars."""
    if not COPYPARTY_USER_FOLDER:
        return
    _ensure_user_folder()
    url = _dav_url("spoons", COPYPARTY_USER_FOLDER, "data.json")

    try:
        local_hash = _sha256_file("data.json")
    except FileNotFoundError:
        print("[copyparty] no local data.json to upload")
        return
    except Exception as e:
        print(f"[copyparty] cannot hash local data.json: {e}")
        return

    # DELETE (ignore 404), then PUT
    try:
        try:
            dr = requests.delete(url, headers=_auth_headers(), timeout=COPYPARTY_TIMEOUT_S)
            if dr.status_code not in (200, 204, 404):
                print(f"[copyparty] pre-delete returned {dr.status_code}: {dr.text[:200]}")
        except Exception as e:
            print(f"[copyparty] pre-delete error (ignored): {e}")

        with open("data.json", "rb") as fp:
            hdr = _auth_headers(); hdr["Content-Type"] = "application/json"
            r = requests.put(url, data=fp, headers=hdr, timeout=COPYPARTY_TIMEOUT_S)
        if r.status_code not in (200, 201, 204):
            print(f"[copyparty] upload failed {r.status_code}: {r.text[:200]}")
            return
        print(f"[copyparty] upload ok -> {url}")

        # cache-busted read-back verify
        st, body = _fresh_get(url, COPYPARTY_TIMEOUT_S)
        if st != 200:
            time.sleep(0.5)
            st, body = _fresh_get(url, COPYPARTY_TIMEOUT_S)
        if st == 200:
            if _sha256_bytes(body) != local_hash:
                time.sleep(0.6)
                st2, body2 = _fresh_get(url, COPYPARTY_TIMEOUT_S)
                if st2 == 200 and _sha256_bytes(body2) == local_hash:
                    print("[copyparty] verify ok after retry")
                else:
                    print("[copyparty] WARNING: verify mismatch; remote appears stale")
            else:
                print("[copyparty] verify ok")
        else:
            print(f"[copyparty] verify GET failed with {st}")

        _cleanup_old_versions()
    except Exception as e:
        print(f"[copyparty] upload error: {e}")

def download_data_json_if_present():
    if not COPYPARTY_USER_FOLDER:
        return False
    url = _dav_url("spoons", COPYPARTY_USER_FOLDER, "data.json")
    try:
        r = requests.get(url, headers=_auth_headers(), timeout=COPYPARTY_TIMEOUT_S, stream=True)
        if r.status_code == 200:
            with open("data.json", "wb") as fp:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk: fp.write(chunk)
            print("[copyparty] downloaded remote data.json")
            return True
        elif r.status_code in (401, 403, 404):
            print(f"[copyparty] remote not available ({r.status_code})")
        else:
            print(f"[copyparty] download failed {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[copyparty] download error: {e}")
    return False
