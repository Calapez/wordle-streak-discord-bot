import os
import re
import requests

BOT_TOKEN  = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
PREVIOUS_CHANNEL_STREAK = 100 # Delete this logic if the streak ever dies.

headers = {
    "Authorization": f"Bot {BOT_TOKEN}"
}

# Fetch the last 20 messages in the channel
response = requests.get(
    f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=30",
    headers=headers
)

messages = response.json()

for msg in messages:
    match = re.search(r"on a (\d+) day streak", msg["content"], re.IGNORECASE)
    if match:
        streak = int(match.group(1)) + PREVIOUS_CHANNEL_STREAK
        new_name = f"wordle-{streak}-daystreak"
        patch = requests.patch(
            f"https://discord.com/api/v10/channels/{CHANNEL_ID}",
            headers=headers,
            json={"name": new_name}
        )
        if patch.status_code == 200:
            print(f"✅ Channel renamed to: {new_name}")
        else:
            print(f"❌ Failed to rename: {patch.status_code} {patch.text}")
        break
else:
    print("No streak message found in the last 20 messages.")
