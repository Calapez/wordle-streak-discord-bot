import os
import re
import random
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Offset added to the parsed streak to account for history before the bot
# existed. Delete this constant (and its usage) if the streak ever resets.
PREVIOUS_CHANNEL_STREAK = 100

FAIL_MESSAGES = [
    "Ei ca burro!",
    "Errrroooooooou!",
    "Estavas a jogar com o monitor desligado? 🫣",
    "Amanhã há mais... 🫂",
    "És pior que o Ramiro, que é repetente.",
    "É lidar...",
    "Wordle não é muito a tua praia... Tu és mais bolos.",
    "Se calhar com 10 tentativas chegavas lá 😬",
    "Se voltas a falhar faço-te a folha 🔪",
    "Já vi seres unicelulares mais inteligentes.",
    "Chamas a isso jogar?",
    "Não sabia que tinhamos um Neandertal no servidor.",
    "Foi honestamente triste de assistir...",
    "Da próxima tenta usar o cérebro.",
    "Amanhã tenta com o dicionário aberto, talvez resulte.",
    "Essa sequência de palpites foi mais triste do que o final do Titanic.",
    "Queres falar sobre o que aconteceu?",
    "Começa a pedir ao ChatGPT para fazer por ti 🤐",
]

DISCORD_API = "https://discord.com/api/v10"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dotenv() -> None:
    """Load variables from a local .env file into the environment (no-op in CI)."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def make_headers(bot_token: str) -> dict[str, str]:
    return {"Authorization": f"Bot {bot_token}"}


def fetch_messages(channel_id: str, headers: dict, limit: int = 30) -> list[dict]:
    response = requests.get(
        f"{DISCORD_API}/channels/{channel_id}/messages",
        params={"limit": limit},
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def rename_channel(channel_id: str, new_name: str, headers: dict) -> None:
    response = requests.patch(
        f"{DISCORD_API}/channels/{channel_id}",
        headers=headers,
        json={"name": new_name},
    )
    if response.status_code == 200:
        print(f"✅ Channel renamed to: {new_name}")
    else:
        print(f"❌ Failed to rename channel: {response.status_code} {response.text}")


def send_dm(user_id: str, message: str, headers: dict, username: str = "unknown") -> None:
    dm_response = requests.post(
        f"{DISCORD_API}/users/@me/channels",
        headers=headers,
        json={"recipient_id": user_id},
    )
    if dm_response.status_code != 200:
        print(f"❌ Failed to open DM with {username} ({user_id}): {dm_response.status_code} {dm_response.text}")
        return

    dm_channel_id = dm_response.json()["id"]
    send_response = requests.post(
        f"{DISCORD_API}/channels/{dm_channel_id}/messages",
        headers=headers,
        json={"content": message},
    )
    if send_response.status_code == 200:
        print(f"✅ DM sent to {username} ({user_id})")
    else:
        print(f"❌ Failed to send DM to {username} ({user_id}): {send_response.status_code} {send_response.text}")


def dm_failed_players(msg: dict, headers: dict) -> None:
    """Send a random roast DM to every player who got X/6 in this message."""
    failed_match = re.search(r"X/6[^<]*(<@\d+>(?:[^<]*<@\d+>)*)", msg["content"])
    if not failed_match:
        return

    failed_ids = re.findall(r"<@(\d+)>", failed_match.group(1))
    mentions_by_id = {u["id"]: u["username"] for u in msg.get("mentions", [])}
    for user_id in failed_ids:
        username = mentions_by_id.get(user_id, "unknown")
        send_dm(user_id, random.choice(FAIL_MESSAGES), headers, username)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    load_dotenv()

    bot_token = os.environ["BOT_TOKEN"]
    channel_id = os.environ["CHANNEL_ID"]
    headers = make_headers(bot_token)

    messages = fetch_messages(channel_id, headers)

    for msg in messages:
        author = msg.get("author", {}).get("username", "")
        if "wordle" not in author.lower():
            continue

        match = re.search(r"on an? (\d+) day streak", msg["content"], re.IGNORECASE)
        if not match:
            continue

        streak = int(match.group(1)) + PREVIOUS_CHANNEL_STREAK
        print(f"Found streak: {streak} (raw={match.group(1)}, offset={PREVIOUS_CHANNEL_STREAK})")

        rename_channel(channel_id, f"wordle-{streak}-daystreak", headers)
        dm_failed_players(msg, headers)
        break
    else:
        print("No streak message found in the last 30 messages.")


if __name__ == "__main__":
    main()
