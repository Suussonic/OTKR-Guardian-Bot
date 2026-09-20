# /roledeban : retire l'interdiction de rôles pour des membres précis
import discord
from discord.ui import Select, View

from core.client import bot
from core.permissions import is_authorized_channel
from core.storage import save_data, server_data


class RoleDebanMemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [
            discord.SelectOption(label=member.display_name, value=str(member.id))
            for member in guild.members if not member.bot
        ]
        super().__init__(placeholder="Sélectionnez les membres", min_values=1, max_values=min(len(options), 25), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = RoleDebanRoleSelectView(interaction.guild, self.values)
        await interaction.followup.send("🔽 Sélectionnez les rôles à débannir :", view=view)


class RoleDebanRoleSelect(Select):
    def __init__(self, guild: discord.Guild, selected_members: list):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in guild.roles if not role.is_default()
        ]
        super().__init__(placeholder="Sélectionnez les rôles à débannir", min_values=1, max_values=min(len(options), 25), options=options)
        self.selected_members = selected_members

    async def callback(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        removed_roles = []

        for member_id in self.selected_members:
            user_id = str(member_id)
            user_banned_roles = server_data.get(server_id, {}).get("banned_roles", {}).get(user_id, [])
            for role_id in self.values:
                if role_id in user_banned_roles:
                    user_banned_roles.remove(role_id)
                    removed_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(server_data)
        message = f"✅ Rôles débannis : {', '.join(removed_roles)} pour les membres sélectionnés." if removed_roles else "❌ Aucun rôle à débannir."
        await interaction.response.send_message(message)


class RoleDebanRoleSelectView(View):
    def __init__(self, guild: discord.Guild, selected_members: list):
        super().__init__()
        self.add_item(RoleDebanRoleSelect(guild, selected_members))


class RoleDebanMemberView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(RoleDebanMemberSelect(guild))


@bot.tree.command(name="roledeban", description="Débannit plusieurs rôles pour plusieurs membres.")
async def roledeban(interaction: discord.Interaction):
    if not await is_authorized_channel(interaction):
        return

    view = RoleDebanMemberView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les membres :", view=view)
