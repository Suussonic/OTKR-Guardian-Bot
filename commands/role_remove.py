# RoleSelect : menu permettant à un membre de se voir retirer certains de ses rôles
# (composant conservé pour une future commande, non encore relié à une commande slash)
import discord


class RoleSelect(discord.ui.Select):
    def __init__(self, member: discord.Member):
        roles = [
            role for role in member.roles
            if role != member.guild.default_role and role < member.guild.me.top_role
        ]
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
        if not options:
            options = [discord.SelectOption(label="Aucun rôle disponible", value="none", default=True, description="Aucun rôle supprimable")]

        super().__init__(placeholder="Sélectionnez les rôles à retirer", min_values=1, max_values=len(options), options=options)
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        if "none" in self.values:
            await interaction.response.send_message("Aucun rôle à retirer.", ephemeral=True)
            return

        removed_roles = []
        for role_id in self.values:
            role = discord.utils.get(self.member.guild.roles, id=int(role_id))
            if role in self.member.roles:
                await self.member.remove_roles(role)
                removed_roles.append(role.name)

        if removed_roles:
            await interaction.response.send_message(f"🔴 Rôles supprimés : {', '.join(removed_roles)} pour {self.member.mention}.")
        else:
            await interaction.response.send_message("Aucun rôle n'a été retiré.")


class RoleSelectView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.add_item(RoleSelect(member))
