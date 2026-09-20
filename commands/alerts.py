# /alertadmin : enregistre les administrateurs à notifier en cas d'expulsion du bot
import discord
from discord import app_commands

from core.client import bot
from core.permissions import is_authorized_channel
from core.storage import save_data, server_data


@bot.tree.command(name="alertadmin", description="Définit les administrateurs à notifier en cas d'expulsion du bot.")
@app_commands.checks.has_permissions(administrator=True)
async def alertadmin(interaction: discord.Interaction, members: discord.Member):
    if not await is_authorized_channel(interaction):
        return

    server_id = str(interaction.guild.id)
    alert_admins = server_data.setdefault(server_id, {}).setdefault("alert_admins", [])

    admin_id = str(members.id)
    if admin_id not in alert_admins:
        alert_admins.append(admin_id)

    save_data(server_data)
    await interaction.response.send_message(f"✅ {members.mention} sera notifié si le bot est expulsé du serveur.")
