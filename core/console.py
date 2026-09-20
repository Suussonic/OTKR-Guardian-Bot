# Console interactive : permet de piloter le bot depuis le terminal pendant qu'il tourne
import asyncio

from core.client import bot

HELP_TEXT = (
    "\n📖 Commandes disponibles :\n"
    "  servers                                    - Liste les serveurs connectés\n"
    "  roles <server_id>                          - Liste les rôles d'un serveur\n"
    "  users <server_id>                          - Liste les membres d'un serveur\n"
    "  giverole <server_id> <user_id> <role_id>   - Donne un rôle à un membre\n"
    "  help                                        - Affiche cette aide\n"
    "  exit                                        - Ferme la console (le bot continue de tourner)\n"
)


def _find_guild(server_id: str):
    if not server_id.isdigit():
        print(f"❌ ID de serveur invalide : {server_id}")
        return None
    guild = bot.get_guild(int(server_id))
    if guild is None:
        print(f"❌ Serveur introuvable pour l'ID : {server_id}")
    return guild


def _print_servers():
    guilds = bot.guilds
    if not guilds:
        print("⚠️ Aucun serveur connecté.")
        return
    print(f"\n📡 Serveurs connectés ({len(guilds)}) :")
    for guild in guilds:
        print(f"  - {guild.name} (ID: {guild.id}) — {guild.member_count} membres")


def _print_roles(args: list[str]):
    if not args:
        print("⚠️ Utilisation : roles <server_id>")
        return
    guild = _find_guild(args[0])
    if guild is None:
        return
    print(f"\n🎭 Rôles du serveur {guild.name} ({len(guild.roles)}) :")
    for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
        print(f"  - {role.name} (ID: {role.id}) — {len(role.members)} membres")


def _print_members(args: list[str]):
    if not args:
        print("⚠️ Utilisation : users <server_id>")
        return
    guild = _find_guild(args[0])
    if guild is None:
        return
    print(f"\n👥 Membres du serveur {guild.name} ({len(guild.members)}) :")
    for member in guild.members:
        role_names = ", ".join(role.name for role in member.roles if role != guild.default_role)
        member_type = "bot" if member.bot else "humain"
        print(f"  - {member.display_name} (ID: {member.id}) [{member_type}] — Rôles : {role_names or 'Aucun'}")


async def _give_role(args: list[str]):
    if len(args) < 3:
        print("⚠️ Utilisation : giverole <server_id> <user_id> <role_id>")
        return
    guild = _find_guild(args[0])
    if guild is None:
        return
    if not args[1].isdigit() or not args[2].isdigit():
        print("❌ user_id et role_id doivent être des identifiants numériques.")
        return

    member = guild.get_member(int(args[1]))
    if member is None:
        print(f"❌ Membre introuvable pour l'ID : {args[1]}")
        return
    role = guild.get_role(int(args[2]))
    if role is None:
        print(f"❌ Rôle introuvable pour l'ID : {args[2]}")
        return
    if role in member.roles:
        print(f"⚠️ {member.display_name} possède déjà le rôle {role.name}.")
        return

    await member.add_roles(role)
    print(f"✅ Rôle '{role.name}' donné à {member.display_name} sur {guild.name}.")


async def run_console() -> None:
    """Boucle principale de la console : lit et exécute les commandes tapées dans le terminal."""
    print(HELP_TEXT)
    while True:
        try:
            line = await asyncio.to_thread(input, ">>> ")
        except (EOFError, KeyboardInterrupt):
            break

        parts = line.strip().split()
        if not parts:
            continue
        command, args = parts[0].lower(), parts[1:]

        try:
            if command in ("help", "?"):
                print(HELP_TEXT)
            elif command in ("servers", "guilds"):
                _print_servers()
            elif command == "roles":
                _print_roles(args)
            elif command in ("users", "members"):
                _print_members(args)
            elif command == "giverole":
                await _give_role(args)
            elif command in ("exit", "quit"):
                print("👋 Fermeture de la console (le bot continue de tourner).")
                break
            else:
                print(f"❌ Commande inconnue : {command}. Tapez 'help' pour la liste des commandes.")
        except Exception as error:
            print(f"❌ Erreur : {error}")
