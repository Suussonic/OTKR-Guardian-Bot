# Instance unique du bot, partagée par tous les modules d'événements et de commandes
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True  # Nécessaire pour suivre les changements de rôles des membres

bot = commands.Bot(command_prefix="!", intents=intents)
