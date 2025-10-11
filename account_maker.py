#!/usr/bin/env python3
import os
import sys
import tempfile
import getpass
import requests

BASE = "https://jasondarby.com"
NEW_USERS_PATH = "/new_users"
SPOONS_PATH = "/spoons"
TIMEOUT = 15

def main():
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty.", file=sys.stderr)
        sys.exit(1)
    password = getpass.getpass("Password: ")

    creds_content = f"{username}:{password}"
    fd, local_path = tempfile.mkstemp(prefix="new_user_", suffix=".txt")
    os.close(fd)

    try:
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(creds_content)

        # Upload credentials file to /new_users/
        new_users_url = f"{BASE.rstrip('/')}{NEW_USERS_PATH}/{username}.txt"
        with open(local_path, "rb") as fh:
            resp = requests.put(new_users_url, data=fh, headers={"Content-Type": "text/plain"}, timeout=TIMEOUT)

        if not (200 <= resp.status_code < 300):
            print(f"Failed to upload to {new_users_url} (HTTP {resp.status_code}).")
            print("there was a problem creating your account")
            return

        # Attempt WebDAV PUT to /spoons/<username> using password-only auth
        spoons_url = f"{BASE.rstrip('/')}{SPOONS_PATH}/{username}/data.txt"
        try:
            # requests.auth.HTTPBasicAuth takes (user, pass)
            # To send only a password, leave username empty
            webdav_resp = requests.put(spoons_url, data=username + ":" + password, auth=("", password), timeout=TIMEOUT)
            if 200 <= webdav_resp.status_code < 300:
                print("account created successfully")
            else:
                print(f"WebDAV PUT to {spoons_url} returned HTTP {webdav_resp.status_code}.")
                print("there was a problem creating your account")
        except requests.RequestException as e:
            print(f"Error during WebDAV PUT: {e}")
            print("there was a problem creating your account")

    finally:
        try:
            os.remove(local_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
