# wordle-streak-discord-bot

A Discord bot that tracks a group's daily Wordle streak and renames a channel to reflect it. It also DMs roast messages to anyone who failed that day's Wordle.

## How it works

1. Reads the last 30 messages from a configured Discord channel.
2. Finds the Wordle bot's summary message and parses the current streak from `"on a N day streak"`.
3. Adds a hardcoded offset (`PREVIOUS_CHANNEL_STREAK = 100`) to account for the streak before this bot existed.
4. Renames the channel to `wordle-{total}-daystreak`.
5. DMs a random Portuguese roast to every player listed under `X/6` in that message.

## Setup

### Requirements

- Python 3.10+
- `pip install requests`
- A Discord bot token with the **Manage Channels** permission added to the server

### Environment variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Discord bot token |
| `CHANNEL_ID` | ID of the channel to monitor and rename |

For local development, create a `.env` file:

```
BOT_TOKEN=your-token-here
CHANNEL_ID=your-channel-id-here
```

### Running locally

```bash
pip install requests
python bot.py
```

## GitHub Actions

The workflow at `.github/workflows/rename_channel.yml` runs `bot.py` daily at 12:30 UTC (1:30 pm Lisbon) and supports manual dispatch via `workflow_dispatch`.

Add `BOT_TOKEN` and `CHANNEL_ID` as repository secrets.

## Notes

- `PREVIOUS_CHANNEL_STREAK = 100` in `bot.py` is a one-time offset for pre-bot history. Remove it (and its usage) if the streak ever resets to 0.
