# 🛡️ Bot Discord OTKR Guardian

Ce bot Discord a vue le jour pour pouvoir gérer principallement les roles des utilisateur compliqué.

## 📜 Sommaire
- [Prérequis](#⚙️-prérequis)
- [Création du Bot](#🤖-création-du-bot)
- [.env](#🔒-env)
- [Lancement du Bot](#🚀-lancement-du-bot)

# ⚙️ Prérequis

1. Pour pouvoir utiliser le Bot, il vous faudra python d'installer sur votre machine que vous pourrais retrouver ici :

      https://www.python.org/downloads/

2. Vous pouvez créer un environnement virtuelle python, cet étape est obstionnelle :

      Créer un environnement virtuelle :
    ```bash
   python -m venv "nom de l'environnement"
   ```

      Rentrer dans l'environnement :
    ```bash
   ./"nom de l'environnement"/Scripts/activate
   ```

      Sortir de l'environnement :
    ```bash
   deactivate
   ```

4. Installation de la dépendance Discord qui permet de pourvoir intéragir avec discord :

      ```bash
   pip install discord.py
   ```
   
6. Installation de la dépendance dotenv qui permet de pourvoir récupérer les informations du fichier .env :

      ```bash
   pip install python-dotenv
   ```
   
# 🤖 Création du Bot

Tout d'abord votre Bot Discord doit être sur la plateforme Discord Dev :

  https://discord.com/developers/applications

1. Aprés avoir créer votre Bot, vous devrez récupérer le Token pour pour pouvoir par la suite le connecter a votre programme :

      Pour ce faire dans la partie settings aller dans Bot puis cliquer sur bouton Reset Token et copier le Token

2. Sur la même page dans la partie Privileged Gateway Intents, vous devrez cocher Presence Intent, Server Members Intent et Message Content Intent, cela permettra de voir la présence du Bot...

3. Toujours dans setting mais cette fois ci dans la catégorie Installation, dans les scopes aprés application.commands, vous devrez rajouter le terme "bot", un nouveau champs apparaitra et vous permettra de donner les permissions qui seront demander à l'ajout du Bot dans un serveur.

4. Plus haut dans Installation Contexts, vous aller décocher la case User Install pour qu'ainsi l'ajout du Bot se fasse uniquement dans des serveurs, ici appelé Guild.

5. Vous trouverais juste en dessous une url, cette url vous permettra d'ajouter le bot dans un serveur, pour ce faire copier le et coller sur une nouvelle page Web.

# 🔒 .env

Dans le même dossier que votre code python, il vous faudra ajouter un fichier .env qui contiendra en lui les donnée sensible, ici le Token du Bot. Pour ce projet vous allez rentrer :

```bash
   DISCORD_TOKEN="Votre token, attention a ne pas mettre de guillement ou d'espace apres le signe ="
   ```

# 🚀 Lancement du Bot

Pour lancer le bot aller devoir entrer cette commande dans le terminal :

   ```bash
 python "nom du fichier python".py
 ```
