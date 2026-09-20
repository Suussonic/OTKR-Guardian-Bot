# /choosechannel : définit le salon unique où les commandes du bot sont autorisées
import discord
from discord import app_commands

from core.client import bot
from core.storage import save_data, server_data


@bot.tree.command(name="choosechannel", description="Définit le salon autorisé pour les commandes du bot.")
@app_commands.checks.has_permissions(administrator=True)
async def choosechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    server_id = str(interaction.guild.id)
    authorized_channel_id = server_data.get(server_id, {}).get("authorized_channel")

    if authorized_channel_id and interaction.channel.id != int(authorized_channel_id):
        await interaction.response.send_message(
            f"❌ Cette commande ne peut être utilisée que dans le salon autorisé : <#{authorized_channel_id}>."
        )
        return

    server_config = server_data.setdefault(server_id, {"banned_roles": {}})
    server_config["authorized_channel"] = str(channel.id)

    save_data(server_data)
    await interaction.response.send_message(f"✅ Le salon autorisé a été défini sur {channel.mention}.")


@choosechannel.error
async def choosechannel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.")
