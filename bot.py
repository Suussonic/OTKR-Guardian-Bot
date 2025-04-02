import discord  # Importation de la bibliothèque Discord
import os  # Importation du module OS pour interagir avec le système d'exploitation
import json  # Importation du module JSON pour gérer les fichiers JSON
from discord.ext import commands  # Importation des commandes d'extension Discord
from discord import app_commands
from discord.ui import View, Select
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
    authorized_channel_id = roles_to_remove.get(server_id, {}).get("authorized_channel")

    # Vérifie si un salon autorisé est déjà défini
    if authorized_channel_id and interaction.channel.id != int(authorized_channel_id):
        await interaction.response.send_message(
            f"❌ Cette commande ne peut être utilisée que dans le salon autorisé : <#{authorized_channel_id}>."
        )
        return

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

##########################################################################################################################################################################################

@bot.tree.command(name="alertadmin", description="Définit les administrateurs à notifier en cas d'expulsion du bot.")
@app_commands.checks.has_permissions(administrator=True)
async def alertadmin(interaction: discord.Interaction, members: discord.Member):
    if not await check_channel(interaction):
        return  # Stoppe l'exécution si le salon n'est pas autorisé
    
    server_id = str(interaction.guild.id)

    if server_id not in roles_to_remove:
        roles_to_remove[server_id] = {"alert_admins": []}

    # Ajoute l'ID du membre à la liste des admins alertés
    admin_id = str(members.id)
    if admin_id not in roles_to_remove[server_id]["alert_admins"]:
        roles_to_remove[server_id]["alert_admins"].append(admin_id)

    save_data(roles_to_remove)  # Sauvegarde les changements

    await interaction.response.send_message(
        f"✅ {members.mention} sera notifié si le bot est expulsé du serveur."
    )


##########################################################################################################################################################################################


# Bannir un rôle pour un membre du serveur
class RoleBanMemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in guild.members if not member.bot]
        super().__init__(placeholder="Sélectionnez les membres", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = RoleBanRoleSelectView(interaction.guild, self.values)
        await interaction.followup.send("🔽 Sélectionnez les rôles à bannir :", view=view)#, ephemeral=True)

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
            if server_id not in roles_to_remove:
                roles_to_remove[server_id] = {"banned_roles": {}}
            if user_id not in roles_to_remove[server_id]["banned_roles"]:
                roles_to_remove[server_id]["banned_roles"][user_id] = []
            for role_id in self.values:
                if role_id not in roles_to_remove[server_id]["banned_roles"][user_id]:
                    roles_to_remove[server_id]["banned_roles"][user_id].append(role_id)
                    banned_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(roles_to_remove)
        await interaction.response.send_message(f"🔴 Rôles bannis : {', '.join(banned_roles)} pour les membres sélectionnés.")#, ephemeral=True)

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
    if not await check_channel(interaction):
        return  # Stoppe l'exécution si le salon n'est pas autorisé

    view = RoleBanMemberView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les membres :", view=view)


##########################################################################################################################################################################################

# Débannir un rôle d'un membre
class RoleDebanMemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [
            discord.SelectOption(label=member.display_name, value=str(member.id)) 
            for member in guild.members if not member.bot
        ]
        super().__init__(placeholder="Sélectionnez les membres", min_values=1, max_values=min(len(options), 25), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = RoleDebanRoleSelectView(interaction.guild, self.values)
        await interaction.followup.send("🔽 Sélectionnez les rôles à débannir :", view=view)

class RoleDebanRoleSelect(Select):
    def __init__(self, guild: discord.Guild, selected_members: list):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id)) 
            for role in guild.roles if not role.is_default()
        ]
        super().__init__(placeholder="Sélectionnez les rôles à débannir", min_values=1, max_values=min(len(options), 25), options=options)
        self.selected_members = selected_members

    async def callback(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        removed_roles = []

        for member_id in self.selected_members:
            user_id = str(member_id)
            if server_id in roles_to_remove and user_id in roles_to_remove[server_id]["banned_roles"]:
                for role_id in self.values:
                    if role_id in roles_to_remove[server_id]["banned_roles"][user_id]:
                        roles_to_remove[server_id]["banned_roles"][user_id].remove(role_id)
                        removed_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(roles_to_remove)
        message = f"✅ Rôles débannis : {', '.join(removed_roles)} pour les membres sélectionnés." if removed_roles else "❌ Aucun rôle à débannir."
        await interaction.response.send_message(message)

class RoleDebanRoleSelectView(View):
    def __init__(self, guild: discord.Guild, selected_members: list):
        super().__init__()
        self.add_item(RoleDebanRoleSelect(guild, selected_members))

class RoleDebanMemberView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(RoleDebanMemberSelect(guild))

@bot.tree.command(name="roledeban", description="Débannit plusieurs rôles pour plusieurs membres.")
async def roledeban(interaction: discord.Interaction):
    if not await check_channel(interaction):
        return

    view = RoleDebanMemberView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les membres :", view=view)



##########################################################################################################################################################################################

class AllRoleBanSelect(Select):
    def __init__(self, roles: list[discord.Role], server_id: str):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles
        ]

        super().__init__(placeholder="Sélectionnez les rôles à bannir globalement", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)

        if server_id not in roles_to_remove:
            roles_to_remove[server_id] = {"global_banned_roles": []}

        banned_roles = []
        for role_id in self.values:
            if role_id not in roles_to_remove[server_id]["global_banned_roles"]:
                roles_to_remove[server_id]["global_banned_roles"].append(role_id)
                banned_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(roles_to_remove)

        await interaction.response.send_message(f"🔴 Rôles bannis globalement : {', '.join(banned_roles)}.")#, ephemeral=True)

class AllRoleBanView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(AllRoleBanSelect(guild.roles, str(guild.id)))

@bot.tree.command(name="allroleban", description="Bannit plusieurs rôles globalement via une sélection.")
async def allroleban(interaction: discord.Interaction):
    if not await check_channel(interaction):
        return

    view = AllRoleBanView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les rôles à bannir globalement :", view=view)



##########################################################################################################################################################################################
        
class AllRoleDebanSelect(Select):
    def __init__(self, roles: list[discord.Role], server_id: str):
        global_banned_roles = roles_to_remove.get(server_id, {}).get("global_banned_roles", [])

        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles if str(role.id) in global_banned_roles
        ]

        if not options:
            options = [discord.SelectOption(label="Aucun rôle banni globalement", value="none", default=True, description="Aucun rôle à débannir")]

        super().__init__(placeholder="Sélectionnez les rôles à débannir globalement", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        if "none" in self.values:
            await interaction.response.send_message("⚠️ Aucun rôle à débannir globalement.", ephemeral=True)
            return

        server_id = str(interaction.guild.id)

        removed_roles = []
        for role_id in self.values:
            if role_id in roles_to_remove[server_id]["global_banned_roles"]:
                roles_to_remove[server_id]["global_banned_roles"].remove(role_id)
                removed_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(roles_to_remove)

        await interaction.response.send_message(f"✅ Rôles débannis globalement : {', '.join(removed_roles)}.")#, ephemeral=True)

class AllRoleDebanView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(AllRoleDebanSelect(guild.roles, str(guild.id)))

@bot.tree.command(name="allroledeban", description="Débannit plusieurs rôles globalement via une sélection.")
async def allroledeban(interaction: discord.Interaction):
    if not await check_channel(interaction):
        return

    view = AllRoleDebanView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les rôles à débannir globalement :", view=view)


##########################################################################################################################################################################################
    
class ExemptMemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in guild.members if not member.bot]
        super().__init__(placeholder="Sélectionnez les membres à exempter", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = ExemptRoleSelectView(interaction.guild, self.values)
        await interaction.followup.send("🔽 Sélectionnez les rôles à exempter :", view=view)#, ephemeral=True)

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
            if server_id not in roles_to_remove:
                roles_to_remove[server_id] = {"exempted_users": {}}
            if user_id not in roles_to_remove[server_id]["exempted_users"]:
                roles_to_remove[server_id]["exempted_users"][user_id] = []
            for role_id in self.values:
                if role_id not in roles_to_remove[server_id]["exempted_users"][user_id]:
                    roles_to_remove[server_id]["exempted_users"][user_id].append(role_id)
                    exempted_roles.append(discord.utils.get(interaction.guild.roles, id=int(role_id)).name)

        save_data(roles_to_remove)
        await interaction.response.send_message(f"✅ Exemptions ajoutées : {', '.join(exempted_roles)} pour les membres sélectionnés.")#, ephemeral=True)

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
    if not await check_channel(interaction):
        return

    view = ExemptMemberView(interaction.guild)
    await interaction.response.send_message("🔽 Sélectionnez les membres à exempter :", view=view)


##########################################################################################################################################################################################

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    server_id = str(after.guild.id)
    user_id = str(after.id)

    if server_id not in roles_to_remove:
        return

    removed_roles = []

    # Vérifie si l'utilisateur est exempté
    if "exempted_users" in roles_to_remove[server_id] and user_id in roles_to_remove[server_id]["exempted_users"]:
        return  # Ne pas lui retirer les rôles bannis globalement

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
        
@bot.event
async def on_guild_remove(guild: discord.Guild):
    server_id = str(guild.id)

    if server_id in roles_to_remove and "alert_admins" in roles_to_remove[server_id]:
        admin_ids = roles_to_remove[server_id]["alert_admins"]

        for admin_id in admin_ids:
            try:
                admin = await bot.fetch_user(int(admin_id))  # Assurez-vous d'utiliser await ici
                if admin is not None:
                    await admin.send(f"🚨 Le bot a été expulsé du serveur {guild.name}.")
                else:
                    print(f"⚠️ Impossible de trouver l'utilisateur {admin_id}.")
            except discord.Forbidden:
                print(f"⚠️ Impossible d'envoyer un MP à {admin_id} (DM désactivés ou bot bloqué).")
            except discord.HTTPException as e:
                print(f"⚠️ Erreur HTTP en envoyant un MP à {admin_id}: {e}")
            except Exception as e:
                print(f"⚠️ Erreur inattendue avec {admin_id}: {e}")


bot.run(os.getenv('DISCORD_TOKEN'))  # Démarre le bot avec le token stocké dans les variables d'environnement
