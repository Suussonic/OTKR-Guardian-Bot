# Notifie les administrateurs enregistrés lorsque le bot est expulsé d'un serveur
import discord

from core.client import bot
from core.storage import server_data


@bot.event
async def on_guild_remove(guild: discord.Guild):
    server_id = str(guild.id)
    admin_ids = server_data.get(server_id, {}).get("alert_admins", [])

    for admin_id in admin_ids:
        try:
            admin = await bot.fetch_user(int(admin_id))
            if admin is not None:
                await admin.send(f"🚨 Le bot a été expulsé du serveur {guild.name}.")
            else:
                print(f"⚠️ Impossible de trouver l'utilisateur {admin_id}.")
        except discord.Forbidden:
            print(f"⚠️ Impossible d'envoyer un MP à {admin_id} (DM désactivés ou bot bloqué).")
        except discord.HTTPException as error:
            print(f"⚠️ Erreur HTTP en envoyant un MP à {admin_id}: {error}")
        except Exception as error:
            print(f"⚠️ Erreur inattendue avec {admin_id}: {error}")
