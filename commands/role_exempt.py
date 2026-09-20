# /exemptrole : exempte des membres des interdictions de rôles (personnelles et globales)
import discord
from discord.ui import Select, View

from core.client import bot
from core.permissions import is_authorized_channel
from core.storage import save_data, server_data


class ExemptMemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in guild.members if not member.bot]
        super().__init__(placeholder="Sélectionnez les membres à exempter", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = ExemptRoleSelectView(interaction.guild, self.values)
        await interaction.followup.send("🔽 Sélectionnez les rôles à exempter :", view=view)


class ExemptRoleSelect(Select):
    def __init__(self, guild: discord.Guild, selected_members: list):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in guild.roles]
        super().__init__(placeholder="Sélectionnez les rôles à exempter", min_values=1, max_values=len(options), options=options)
        self.selected_members = selected_members

    async def callback(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        exempted_roles = []

        for member_id in self.selected_members:
            user_id = str(member_id)
            user_exempted_roles = server_data.setdefault(server_id, {}).setdefault("exempted_users", {}).setdefault(user_id, [])
            for role_id in self.values:
                if role_id not in user_exempted_roles:
                    user_exempted_roles.append(role_id)
                    exempted_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(server_data)
        await interaction.response.send_message(f"✅ Exemptions ajoutées : {', '.join(exempted_roles)} pour les membres sélectionnés.")


class ExemptRoleSelectView(View):
    def __init__(self, guild: discord.Guild, selected_members: list):
        super().__init__()
        self.add_item(ExemptRoleSelect(guild, selected_members))


class ExemptMemberView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(ExemptMemberSelect(guild))


@bot.tree.command(name="exemptrole", description="Exempte plusieurs membres des restrictions de rôle.")
async def exemptrole(interaction: discord.Interaction):
    if not await is_authorized_channel(interaction):
        return

    view = ExemptMemberView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les membres à exempter :", view=view)
