# /roleban : interdit un ou plusieurs rôles pour des membres précis
import discord
from discord.ui import Select, View

from core.client import bot
from core.permissions import is_authorized_channel
from core.storage import save_data, server_data


class RoleBanMemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in guild.members if not member.bot]
        super().__init__(placeholder="Sélectionnez les membres", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = RoleBanRoleSelectView(interaction.guild, self.values)
        await interaction.followup.send("🔽 Sélectionnez les rôles à bannir :", view=view)


class RoleBanRoleSelect(Select):
    def __init__(self, guild: discord.Guild, selected_members: list):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in guild.roles]
        super().__init__(placeholder="Sélectionnez les rôles à bannir", min_values=1, max_values=len(options), options=options)
        self.selected_members = selected_members

    async def callback(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        banned_roles = []

        for member_id in self.selected_members:
            user_id = str(member_id)
            user_banned_roles = server_data.setdefault(server_id, {}).setdefault("banned_roles", {}).setdefault(user_id, [])
            for role_id in self.values:
                if role_id not in user_banned_roles:
                    user_banned_roles.append(role_id)
                    banned_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(server_data)
        await interaction.response.send_message(f"🔴 Rôles bannis : {', '.join(banned_roles)} pour les membres sélectionnés.")


class RoleBanRoleSelectView(View):
    def __init__(self, guild: discord.Guild, selected_members: list):
        super().__init__()
        self.add_item(RoleBanRoleSelect(guild, selected_members))


class RoleBanMemberView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(RoleBanMemberSelect(guild))


@bot.tree.command(name="roleban", description="Bannit plusieurs rôles pour plusieurs membres.")
async def roleban(interaction: discord.Interaction):
    if not await is_authorized_channel(interaction):
        return

    view = RoleBanMemberView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les membres :", view=view)
