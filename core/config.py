# Charge les variables d'environnement (.env) utilisées par le bot
import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_CHANNEL_ID = int(os.getenv("SALON_TOKEN"))
