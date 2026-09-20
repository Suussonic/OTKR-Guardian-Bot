# Synchronise les commandes slash et démarre la console interactive au démarrage du bot
from core.client import bot
from core.console import run_console

_console_started = False  # Évite de relancer la console si on_ready se déclenche plusieurs fois (reconnexion)


@bot.event
async def on_ready():
    global _console_started
    print(f"✅ Bot connecté en tant que {bot.user}")

    try:
        await bot.tree.sync()
        print("✅ Commandes synchronisées")
    except Exception as error:
        print(f"❌ Erreur de synchronisation : {error}")

    if not _console_started:
        _console_started = True
        bot.loop.create_task(run_console())
