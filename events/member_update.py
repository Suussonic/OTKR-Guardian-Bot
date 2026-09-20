# Réapplique automatiquement les restrictions de rôles dès qu'un membre est modifié
import discord

from core.client import bot
from core.storage import server_data


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    server_id = str(after.guild.id)
    user_id = str(after.id)
    server_config = server_data.get(server_id)

    if not server_config:
        return

    # Les membres exemptés conservent tous leurs rôles, même bannis
    if user_id in server_config.get("exempted_users", {}):
        return

    banned_role_ids = server_config.get("banned_roles", {}).get(user_id, [])
    banned_role_ids += server_config.get("global_banned_roles", [])

    removed_roles = []
    for role_id in banned_role_ids:
        role = discord.utils.get(after.guild.roles, id=int(role_id))
        if role and role in after.roles and role not in before.roles:
            await after.remove_roles(role)
            removed_roles.append(role.name)

    if removed_roles:
        print(f"🔴 {after.name} a reçu des rôles interdits : {', '.join(removed_roles)} (supprimés)")
