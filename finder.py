"""Find live Twitch creators for a game through the official Helix API and save them as a lead list.

Usage:
  python finder.py --game "Counter-Strike" --lang en --min-viewers 20 --max-viewers 2000
  python finder.py --game VALORANT --lang ar tr --out leads.csv

Needs TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET (app access token, no user login).
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.twitch.tv/helix"
CONTACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|discord\.gg/\w+", re.I)


def http(method, url, headers=None, data=None):
    req = urllib.request.Request(url, method=method, headers=headers or {},
                                 data=urllib.parse.urlencode(data).encode() if data else None)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:  # rate limit: wait until the window resets
                reset = float(e.headers.get("Ratelimit-Reset", time.time() + 2))
                time.sleep(max(1, reset - time.time()))
                continue
            raise


def token(cid, secret):
    return http("POST", "https://id.twitch.tv/oauth2/token",
                data={"client_id": cid, "client_secret": secret, "grant_type": "client_credentials"})["access_token"]


def get(path, params, auth):
    return http("GET", f"{API}/{path}?{urllib.parse.urlencode(params, doseq=True)}", headers=auth)


def live_streams(game_id, langs, auth, limit):
    cursor, out = None, []
    while len(out) < limit:
        params = {"game_id": game_id, "first": 100, "language": langs}
        if cursor:
            params["after"] = cursor
        page = get("streams", params, auth)
        out += page["data"]
        cursor = page.get("pagination", {}).get("cursor")
        if not cursor or not page["data"]:
            break
    return out[:limit]


def contacts(text):
    return sorted(set(m.group(0).rstrip(".") for m in CONTACT.finditer(text or "")))


def to_rows(streams, users, min_v, max_v):
    rows = []
    for s in streams:
        if not (min_v <= s["viewer_count"] <= max_v):
            continue
        u = users.get(s["user_id"], {})
        rows.append({
            "login": s["user_login"], "name": s["user_name"], "url": f"https://twitch.tv/{s['user_login']}",
            "language": s["language"], "viewers": s["viewer_count"], "title": s["title"],
            "bio": (u.get("description") or "").replace("\n", " "),
            "contacts_in_bio": " ".join(contacts(u.get("description"))),
        })
    return sorted(rows, key=lambda r: -r["viewers"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--lang", nargs="+", default=["en"])
    ap.add_argument("--min-viewers", type=int, default=10)
    ap.add_argument("--max-viewers", type=int, default=5000)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--out", default="twitch_leads.csv")
    a = ap.parse_args()

    cid, secret = os.getenv("TWITCH_CLIENT_ID"), os.getenv("TWITCH_CLIENT_SECRET")
    if not cid or not secret:
        sys.exit("Set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET (see .env.example).")
    auth = {"Client-Id": cid, "Authorization": f"Bearer {token(cid, secret)}"}

    games = get("games", {"name": a.game}, auth)["data"]
    if not games:
        sys.exit(f"Game not found: {a.game}")
    streams = live_streams(games[0]["id"], a.lang, auth, a.limit)

    users = {}
    ids = [s["user_id"] for s in streams]
    for i in range(0, len(ids), 100):  # users endpoint takes up to 100 ids per call
        for u in get("users", {"id": ids[i:i + 100]}, auth)["data"]:
            users[u["id"]] = u

    rows = to_rows(streams, users, a.min_viewers, a.max_viewers)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["login"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} creators saved to {a.out} ({len(streams)} live streams checked)")


if __name__ == "__main__":
    main()
