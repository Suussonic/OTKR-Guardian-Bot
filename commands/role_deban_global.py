# /allroledeban : retire des rôles de la liste des interdictions globales du serveur
import discord
from discord.ui import Select, View

from core.client import bot
from core.permissions import is_authorized_channel
from core.storage import save_data, server_data


class AllRoleDebanSelect(Select):
    def __init__(self, roles: list[discord.Role], server_id: str):
        global_banned_roles = server_data.get(server_id, {}).get("global_banned_roles", [])
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles if str(role.id) in global_banned_roles]

        if not options:
            options = [discord.SelectOption(label="Aucun rôle banni globalement", value="none", default=True, description="Aucun rôle à débannir")]

        super().__init__(placeholder="Sélectionnez les rôles à débannir globalement", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        if "none" in self.values:
            await interaction.response.send_message("⚠️ Aucun rôle à débannir globalement.", ephemeral=True)
            return

        server_id = str(interaction.guild.id)
        global_banned_roles = server_data[server_id]["global_banned_roles"]

        removed_roles = []
        for role_id in self.values:
            if role_id in global_banned_roles:
                global_banned_roles.remove(role_id)
                removed_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(server_data)
        await interaction.response.send_message(f"✅ Rôles débannis globalement : {', '.join(removed_roles)}.")


class AllRoleDebanView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(AllRoleDebanSelect(guild.roles, str(guild.id)))


@bot.tree.command(name="allroledeban", description="Débannit plusieurs rôles globalement via une sélection.")
async def allroledeban(interaction: discord.Interaction):
    if not await is_authorized_channel(interaction):
        return

    view = AllRoleDebanView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les rôles à débannir globalement :", view=view)
