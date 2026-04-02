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

The entire bot is `bot.py` — a ~35-line script with no classes or functions:

1. Fetches the last 30 messages from a Discord channel via the REST API (`GET /channels/{id}/messages`)
2. Scans messages for the pattern `"on a N day streak"` (case-insensitive)
3. Adds `PREVIOUS_CHANNEL_STREAK` (hardcoded offset to account for pre-bot history) to the parsed number
4. Renames the channel via `PATCH /channels/{id}` with the new name `wordle-{total}-daystreak`

**Required environment variables / GitHub secrets:**
- `BOT_TOKEN` — Discord bot token (needs `MANAGE_CHANNELS` permission)
- `CHANNEL_ID` — ID of the Discord channel to monitor and rename

**GitHub Actions:** `.github/workflows/rename_channel.yml` runs `bot.py` on a schedule (`0 * * * *`) and supports `workflow_dispatch` for manual runs.

## Key implementation note

`PREVIOUS_CHANNEL_STREAK = 100` in `bot.py` is an offset added to the parsed streak number to account for the streak count before the bot existed. The comment says "Delete this logic if the streak ever dies."
