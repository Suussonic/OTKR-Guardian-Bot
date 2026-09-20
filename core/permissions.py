# Vérifications d'autorisation partagées par les commandes du bot
import discord

from core.storage import server_data


async def is_authorized_channel(interaction: discord.Interaction) -> bool:
    """Vérifie que la commande est utilisée dans le salon défini par /choosechannel."""
    server_id = str(interaction.guild.id)
    authorized_channel_id = server_data.get(server_id, {}).get("authorized_channel")

    if not authorized_channel_id or interaction.channel.id != int(authorized_channel_id):
        await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans le salon autorisé.")
        return False
    return True
