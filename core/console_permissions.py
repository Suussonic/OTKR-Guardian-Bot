# Console interactive : liste et modifie les permissions Discord d'un rôle choisi
import discord

from core.client import bot


def _find_guild(server_id: str):
    if not server_id.isdigit():
        print(f"❌ ID de serveur invalide : {server_id}")
        return None
    guild = bot.get_guild(int(server_id))
    if guild is None:
        print(f"❌ Serveur introuvable pour l'ID : {server_id}")
    return guild


def _find_role(guild: discord.Guild, role_id: str):
    if not role_id.isdigit():
        print(f"❌ ID de rôle invalide : {role_id}")
        return None
    role = guild.get_role(int(role_id))
    if role is None:
        print(f"❌ Rôle introuvable pour l'ID : {role_id}")
    return role


def _print_role_permissions(args: list[str]):
    if len(args) < 2:
        print("⚠️ Utilisation : roleperms <server_id> <role_id>")
        return
    guild = _find_guild(args[0])
    if guild is None:
        return
    role = _find_role(guild, args[1])
    if role is None:
        return

    print(f"\n🔑 Permissions du rôle {role.name} (ID: {role.id}) :")
    for name, value in sorted(role.permissions):
        etat = "✅" if value else "❌"
        print(f"  {etat} {name}")


async def _set_role_permission(args: list[str]):
    if len(args) < 4:
        print("⚠️ Utilisation : setperm <server_id> <role_id> <permission> <on|off>")
        return
    guild = _find_guild(args[0])
    if guild is None:
        return
    role = _find_role(guild, args[1])
    if role is None:
        return

    permission_name = args[2].lower()
    state = args[3].lower()
    if state not in ("on", "off"):
        print("❌ L'état doit être 'on' ou 'off'.")
        return

    permissions = role.permissions
    if not hasattr(permissions, permission_name):
        print(f"❌ Permission inconnue : {permission_name}. Tapez 'roleperms <server_id> <role_id>' pour voir la liste.")
        return

    setattr(permissions, permission_name, state == "on")
    await role.edit(permissions=permissions)
    action = "activée" if state == "on" else "désactivée"
    print(f"✅ Permission '{permission_name}' {action} pour le rôle {role.name} sur {guild.name}.")