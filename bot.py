import os
import re
import random
import requests

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

BOT_TOKEN = os.environ["BOT_TOKEN"]
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

def send_dm(user_id, message, username="unknown"):
    dm = requests.post(
        "https://discord.com/api/v10/users/@me/channels",
        headers=headers,
        json={"recipient_id": user_id}
    )
    if dm.status_code != 200:
        print(f"❌ Failed to open DM with {username} ({user_id}): {dm.status_code} {dm.text}")
        return
    dm_channel_id = dm.json()["id"]
    send = requests.post(
        f"https://discord.com/api/v10/channels/{dm_channel_id}/messages",
        headers=headers,
        json={"content": message}
    )
    if send.status_code == 200:
        print(f"✅ DM sent to {username} ({user_id})")
    else:
        print(f"❌ Failed to send DM to {username} ({user_id}): {send.status_code} {send.text}")

for msg in messages:
    match = re.search(r"on an? (\d+) day streak", msg["content"], re.IGNORECASE)
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

        failed_match = re.search(r"X/6[^<]*(<@\d+>(?:[^<]*<@\d+>)*)", msg["content"])
        if failed_match:
            failed_ids = re.findall(r"<@(\d+)>", failed_match.group(1))
            mentions_by_id = {u["id"]: u["username"] for u in msg.get("mentions", [])}
            for user_id in failed_ids:
                username = mentions_by_id.get(user_id, "unknown")
                send_dm(user_id, random.choice(FAIL_MESSAGES), username)

        break
else:
    print("No streak message found in the last 20 messages.")
