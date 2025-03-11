import discord  # Importation de la bibliothèque Discord
import os  # Importation du module OS pour interagir avec le système d'exploitation
import json  # Importation du module JSON pour gérer les fichiers JSON
from discord.ext import commands  # Importation des commandes d'extension Discord
from discord import app_commands  # Importation des commandes d'application Discord
from dotenv import load_dotenv  # Importation de dotenv pour charger les variables d'environnement

load_dotenv()  # Chargement des variables d'environnement depuis un fichier .env
AUTHORIZED_CHANNEL_ID = int(os.getenv("SALON_TOKEN"))  # Convertit en entier

# Fichier JSON pour stocker les rôles interdits
data_file = "roles_to_remove.json"

# Fonction pour charger les données à partir du fichier JSON
def load_data():
    if not os.path.exists(data_file):  # Vérifie si le fichier JSON existe
        return {}  # Retourne un dictionnaire vide si le fichier n'existe pas
    with open(data_file, "r", encoding="utf-8") as file:  # Ouvre le fichier en mode lecture
        return json.load(file)  # Charge et retourne les données JSON

# Fonction pour sauvegarder les données dans le fichier JSON
def save_data(data):
    with open(data_file, "w", encoding="utf-8") as file:  # Ouvre le fichier en mode écriture
        json.dump(data, file, indent=4)  # Écrit les données JSON dans le fichier avec une indentation

# Charger les rôles interdits dans une variable globale
roles_to_remove = load_data()

intents = discord.Intents.default()  # Active les intentions par défaut du bot
intents.members = True  # Active la détection des mises à jour des membres
bot = commands.Bot(command_prefix="!", intents=intents)  # Création du bot avec un préfixe "!"

async def check_channel(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    authorized_channel_id = roles_to_remove.get(server_id, {}).get("authorized_channel")
    
    if not authorized_channel_id or interaction.channel.id != int(authorized_channel_id):
        await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans le salon autorisé.")
        return False
    return True

@bot.event
async def on_ready():  # Événement déclenché lorsque le bot est prêt
    print(f"✅ Bot connecté en tant que {bot.user}")  # Affiche un message dans la console
    try:
        await bot.tree.sync()  # Synchronise les commandes slash du bot
        print("✅ Commandes synchronisées")  # Affiche un message de confirmation
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")  # Affiche une erreur en cas d'échec

# Classe pour créer un menu de sélection de rôles
class RoleSelect(discord.ui.Select):
    def __init__(self, member: discord.Member):  # Initialisation avec un membre
        roles = [
            role for role in member.roles  # Liste des rôles du membre
            if role != member.guild.default_role and role < member.guild.me.top_role  # Exclut le rôle par défaut et les rôles supérieurs à celui du bot
        ]
        options = [
            discord.SelectOption(label=role.name, value=str(role.id)) for role in roles  # Crée une option pour chaque rôle du membre
        ]
        if not options:  # Vérifie s'il n'y a aucun rôle sélectionnable
            options = [discord.SelectOption(label="Aucun rôle disponible", value="none", default=True, description="Aucun rôle supprimable")]

        super().__init__(placeholder="Sélectionnez les rôles à retirer", min_values=1, max_values=len(options), options=options)  # Définit les paramètres du menu déroulant
        self.member = member  # Stocke le membre

    async def callback(self, interaction: discord.Interaction):  # Fonction exécutée lorsque l'utilisateur fait une sélection
        if "none" in self.values:  # Vérifie si l'utilisateur a sélectionné "Aucun rôle disponible"
            await interaction.response.send_message("Aucun rôle à retirer.", ephemeral=True)  # Envoie un message temporaire
            return
        
        removed_roles = []  # Liste des rôles supprimés
        for role_id in self.values:  # Parcourt les rôles sélectionnés
            role = discord.utils.get(self.member.guild.roles, id=int(role_id))  # Récupère l'objet rôle
            if role in self.member.roles:  # Vérifie si le membre possède le rôle
                await self.member.remove_roles(role)  # Retire le rôle du membre
                removed_roles.append(role.name)  # Ajoute le rôle à la liste des rôles supprimés

                # 📌 Enregistrer le rôle comme interdit
                user_id = str(self.member.id)
                if user_id not in roles_to_remove:
                    roles_to_remove[user_id] = []
                if role_id not in roles_to_remove[user_id]:
                    roles_to_remove[user_id].append(role_id)  # Ajoute le rôle à la liste des rôles interdits
                save_data(roles_to_remove)  # Sauvegarde les rôles interdits

        if removed_roles:  # Vérifie si des rôles ont été supprimés
            await interaction.response.send_message(
                f"🔴 Rôles supprimés : {', '.join(removed_roles)} pour {self.member.mention}."#, ephemeral=True)  # Envoie un message de confirmation
            )
        else:
            await interaction.response.send_message("Aucun rôle n'a été retiré.")#, ephemeral=True)  # Envoie un message si aucun rôle n'a été supprimé

class RoleSelectView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.add_item(RoleSelect(member))  # Ajoute l'élément RoleSelect à la vue
        
@bot.tree.command(name="choosechannel", description="Définit le salon autorisé pour les commandes du bot.")
@app_commands.checks.has_permissions(administrator=True)
async def choosechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    server_id = str(interaction.guild.id)
    
    if server_id not in roles_to_remove:
        roles_to_remove[server_id] = {"authorized_channel": str(channel.id), "banned_roles": {}}
    else:
        roles_to_remove[server_id]["authorized_channel"] = str(channel.id)
    
    save_data(roles_to_remove)
    await interaction.response.send_message(f"✅ Le salon autorisé a été défini sur {channel.mention}.")

@choosechannel.error
async def choosechannel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.")#, ephemeral=True)

# Bannir un rôle pour un membre du serveur
@bot.tree.command(name="roleban", description="Bannit un rôle pour un membre du serveur.")
@app_commands.describe(member="Membre du serveur", role="Rôle à bannir")
async def roleban(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await check_channel(interaction):
        return
    
    server_id = str(interaction.guild.id)
    user_id = str(member.id)
    role_id = str(role.id)
    
    if server_id not in roles_to_remove:
        roles_to_remove[server_id] = {"authorized_channel": "", "banned_roles": {}}
    if user_id not in roles_to_remove[server_id]["banned_roles"]:
        roles_to_remove[server_id]["banned_roles"][user_id] = []
    if role_id not in roles_to_remove[server_id]["banned_roles"][user_id]:
        roles_to_remove[server_id]["banned_roles"][user_id].append(role_id)
    
    save_data(roles_to_remove)
    await interaction.response.send_message(f"🔴 Le rôle {role.name} a été interdit pour {member.mention}.")

# Débannir un rôle d'un membre
@bot.tree.command(name="roledeban", description="Supprime un rôle banni d'un membre.")
@app_commands.describe(member="Membre du serveur", role="Rôle à débannir")
async def roledeban(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await check_channel(interaction):
        return
    
    server_id = str(interaction.guild.id)
    user_id = str(member.id)
    role_id = str(role.id)
    
    if server_id in roles_to_remove and user_id in roles_to_remove[server_id]["banned_roles"]:
        if role_id in roles_to_remove[server_id]["banned_roles"][user_id]:
            roles_to_remove[server_id]["banned_roles"][user_id].remove(role_id)
            if not roles_to_remove[server_id]["banned_roles"][user_id]:
                del roles_to_remove[server_id]["banned_roles"][user_id]
            save_data(roles_to_remove)
            await interaction.response.send_message(f"✅ Le rôle {role.name} a été débanni pour {member.mention}.")
            return
    
    await interaction.response.send_message(f"❌ {member.mention} n'a pas ce rôle en tant que rôle interdit.")


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    server_id = str(after.guild.id)
    user_id = str(after.id)

    if server_id not in roles_to_remove:
        return

    removed_roles = []

    # Vérifier les rôles interdits spécifiques à l'utilisateur
    if "banned_roles" in roles_to_remove[server_id]:
        if user_id in roles_to_remove[server_id]["banned_roles"]:
            for role_id in roles_to_remove[server_id]["banned_roles"][user_id]:
                role = discord.utils.get(after.guild.roles, id=int(role_id))
                if role and role in after.roles and role not in before.roles:
                    await after.remove_roles(role)
                    removed_roles.append(role.name)

    # Vérifier les rôles interdits globalement pour tous les nouveaux membres
    if "global_banned_roles" in roles_to_remove[server_id]:
        for role_id in roles_to_remove[server_id]["global_banned_roles"]:
            role = discord.utils.get(after.guild.roles, id=int(role_id))
            if role and role in after.roles and role not in before.roles:
                await after.remove_roles(role)
                removed_roles.append(role.name)

    if removed_roles:
        print(f"🔴 {after.name} a reçu des rôles interdits : {', '.join(removed_roles)} (supprimés)")
        try:
            await after.send(f"🚨 Attention {after.mention}, les rôles suivants sont interdits sur ce serveur et ont été retirés automatiquement : {', '.join(removed_roles)}.")
        except:
            print(f"Impossible d'envoyer un MP à {after.name}.")


bot.run(os.getenv('DISCORD_TOKEN'))  # Démarre le bot avec le token stocké dans les variables d'environnement
