# /allroleban : interdit un ou plusieurs rôles pour tout le serveur
import discord
from discord.ui import Select, View

from core.client import bot
from core.permissions import is_authorized_channel
from core.storage import save_data, server_data


class AllRoleBanSelect(Select):
    def __init__(self, roles: list[discord.Role]):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
        super().__init__(placeholder="Sélectionnez les rôles à bannir globalement", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        global_banned_roles = server_data.setdefault(server_id, {}).setdefault("global_banned_roles", [])

        banned_roles = []
        for role_id in self.values:
            if role_id not in global_banned_roles:
                global_banned_roles.append(role_id)
                banned_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(server_data)
        await interaction.response.send_message(f"🔴 Rôles bannis globalement : {', '.join(banned_roles)}.")


class AllRoleBanView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(AllRoleBanSelect(guild.roles))


@bot.tree.command(name="allroleban", description="Bannit plusieurs rôles globalement via une sélection.")
async def allroleban(interaction: discord.Interaction):
    if not await is_authorized_channel(interaction):
        return

    view = AllRoleBanView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les rôles à bannir globalement :", view=view)
