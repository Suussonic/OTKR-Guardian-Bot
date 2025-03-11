# 🛡️ Bot Discord OTKR Guardian

Ce bot Discord a vu le jour pour pouvoir gérer principalement les rôles des utilisateurs compliqués.

## 📜 Sommaire
- [Prérequis](#⚙️-prérequis)
- [Création du Bot](#🤖-création-du-bot)
- [.env](#🔒-env)
- [Lancement du Bot](#🚀-lancement-du-bot)

# ⚙️ Prérequis

1. Pour pouvoir utiliser le Bot, il vous faudra Python installé sur votre machine que vous pourrez retrouver ici :

      https://www.python.org/downloads/

2. Vous pouvez créer un environnement virtuel Python, cette étape est optionnelle :

      Créer un environnement virtuel :
    ```bash
   python -m venv "nom de l'environnement"
   ```

      Entrer dans l'environnement :
    ```bash
   ."nom de l'environnement"/Scripts/activate
   ```

      Sortir de l'environnement :
    ```bash
   deactivate
   ```

4. Installation de la dépendance Discord qui permet de pouvoir interagir avec Discord :

      ```bash
   pip install discord.py
   ```
   
6. Installation de la dépendance dotenv qui permet de pouvoir récupérer les informations du fichier .env :

      ```bash
   pip install python-dotenv
   ```
   
# 🤖 Création du Bot

Tout d'abord, votre Bot Discord doit être sur la plateforme Discord Dev :

  https://discord.com/developers/applications

1. Après avoir créé votre Bot, vous devrez récupérer le Token pour pouvoir par la suite le connecter à votre programme :

      Pour ce faire, dans la partie settings, allez dans Bot puis cliquez sur le bouton Reset Token et copiez le Token.

2. Sur la même page, dans la partie Privileged Gateway Intents, vous devrez cocher Presence Intent, Server Members Intent et Message Content Intent. Cela permettra de voir la présence du Bot...

3. Toujours dans settings, mais cette fois-ci dans la catégorie Installation, dans les scopes après application.commands, vous devrez rajouter le terme "bot". Un nouveau champ apparaîtra et vous permettra de donner les permissions qui seront demandées à l'ajout du Bot dans un serveur.

4. Plus haut dans Installation Contexts, vous allez décocher la case User Install pour qu'ainsi l'ajout du Bot se fasse uniquement dans des serveurs, ici appelés Guilds.

5. Vous trouverez juste en dessous une URL, cette URL vous permettra d'ajouter le bot dans un serveur. Pour ce faire, copiez-la et collez-la sur une nouvelle page Web.

# 🔒 .env

Dans le même dossier que votre code Python, il vous faudra ajouter un fichier .env qui contiendra en lui les données sensibles, ici le Token du Bot et l'identifiant du salon ou vous voulez que les commandes soit utilisé. Pour ce projet, vous allez entrer :

```bash
   DISCORD_TOKEN="Votre token, attention à ne pas mettre de guillemets ou d'espace après le signe ="
   SALON_TOKEN="Votre token, attention à ne pas mettre de guillemets ou d'espace après le signe ="
```

# 🚀 Lancement du Bot

Pour lancer le bot, vous allez devoir entrer cette commande dans le terminal :

   ```bash
 python "nom du fichier python".py
 ```
