# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-script Discord bot that renames a Wordle Discord channel to reflect the current group streak. It runs as a GitHub Actions workflow triggered hourly (and manually).

## Running the bot locally

```bash
pip install requests
BOT_TOKEN=<token> CHANNEL_ID=<channel_id> python bot.py
```

## Architecture

The entire bot is `bot.py` — a ~150-line script with small helper functions and no classes:

1. Fetches the last 30 messages from a Discord channel via the REST API (`GET /channels/{id}/messages`)
2. Scans messages for a Wordle bot author and the pattern `"on a N day streak"` (case-insensitive)
3. Adds `PREVIOUS_CHANNEL_STREAK` (hardcoded offset to account for pre-bot history) to the parsed number
4. Renames the channel via `PATCH /channels/{id}` with the new name `wordle-{total}-daystreak`
5. DMs a random roast message to any players who got `X/6` (failed) in that same message

**Key functions in `bot.py`:**
- `load_dotenv()` — loads a local `.env` file for development (no-op in CI)
- `make_headers()` — builds the `Authorization: Bot …` header dict
- `fetch_messages()` — `GET /channels/{id}/messages`
- `rename_channel()` — `PATCH /channels/{id}`
- `send_dm()` — opens a DM channel then posts a message to it
- `dm_failed_players()` — parses `X/6 <@id>` mentions and calls `send_dm` for each
- `main()` — orchestrates everything

**Required environment variables / GitHub secrets:**
- `BOT_TOKEN` — Discord bot token (needs `MANAGE_CHANNELS` permission)
- `CHANNEL_ID` — ID of the Discord channel to monitor and rename

**GitHub Actions:** `.github/workflows/rename_channel.yml` runs `bot.py` daily at 12:30 UTC (1:30 pm Lisbon) and supports `workflow_dispatch` for manual runs.

## Key implementation note

`PREVIOUS_CHANNEL_STREAK = 100` in `bot.py` is an offset added to the parsed streak number to account for the streak count before the bot existed. The comment says "Delete this logic if the streak ever dies."
