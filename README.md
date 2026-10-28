# Twitch Creator Finder

Builds a lead list of live Twitch creators for a given game, language and audience size using the **official Twitch Helix API**. Used for creator and coach partnership outreach, where the goal is finding mid-size streamers who actually play the game you care about.

> **About this repository:** the original Twitch lead workflow was built inside a company outreach system and is not published. This is a short, standalone rewrite of the core idea.

## What it does

- Looks up the game, pages through live streams filtered by one or more languages (`en`, `ar`, `tr`, ...).
- Keeps creators within a viewer range (skip tiny and celebrity channels).
- Fetches each creator's bio in batches of 100 and extracts **publicly listed** business emails and Discord invites.
- Handles rate limits by waiting for the reset window.
- Saves a CSV sorted by viewers: login, name, URL, language, viewers, stream title, bio, contacts.

Uses an app access token only: no user login, no scraping, no private data.

## Run

```bash
export TWITCH_CLIENT_ID=...       # from dev.twitch.tv/console
export TWITCH_CLIENT_SECRET=...
python finder.py --game VALORANT --lang ar en --min-viewers 20 --max-viewers 2000 --out leads.csv
python -m pytest -q               # offline tests for filtering and contact extraction
```

Contact details found in bios should only be used in line with Twitch's terms and local email rules (opt-out, no bulk spam).

## Tech stack

Python 3 (standard library only) · Twitch Helix API · pytest

---

© 2026 yunalhoshi. All rights reserved. See [NOTICE](NOTICE).
