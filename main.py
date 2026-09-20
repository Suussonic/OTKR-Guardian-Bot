# Point d'entrée du bot OTKR Guardian
from core.client import bot
from core.config import DISCORD_TOKEN

# Enregistre les événements du bot
import events.ready  # noqa: F401
import events.member_update  # noqa: F401
import events.guild_remove  # noqa: F401

# Enregistre les commandes slash du bot
import commands.channel  # noqa: F401
import commands.alerts  # noqa: F401
import commands.role_ban  # noqa: F401
import commands.role_deban  # noqa: F401
import commands.role_ban_global  # noqa: F401
import commands.role_deban_global  # noqa: F401
import commands.role_exempt  # noqa: F401

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
