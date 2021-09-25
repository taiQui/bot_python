# Bot discord CDSI ![logo python](https://shields.io/badge/Python-Python?logo=python&style=for-the-badge&logoColor=yellow&color=blue)


Bot pour le discord des CDSI Valenciennes.

## Features :

- **!edt** Emploi du temps
- **!rmstat** Statistique pour root me
- **!ctftime** Liste des CTF à venir
- **!htb** Liste les machines HTB actives
- **!hn** Affiche les premières news du site hackernews
- **!timer** Timer pour les pâtes :)
- **!help** Pour encore plus de commandes !

# Installation 
## Fichier config
Pour démarrer le bot vous devez créer un fichier `.token` à la racine du projet. Ce fichier va contenir toutes les informations importantes pour le bot les tokens d'api : Discord, HackTheBox. Les login et mots de passe pour l'emploi du temps ne sont pas obligatoires.
```json
// .token 
{
    "M1-FI" : {
            "username" : "username",
            "password" : "password"
          },
    "M2-FI" : {
            "username" : "username",
            "password" : "password"
          },
    "M1-FA" : {
            "username" : "username",
            "password" : "password"
          },
    "M2-FA" : {
            "username" : "username",
            "password" : "password!"
          },
    "token" : "__Token_Bot_Discord__",
    "htb_api" : "__Clé_API_HTB__"
}
```
## Installation des packages
Vous devez aussi installer les packages nécessaires au bon fonctionnement du bot avec la commande ci-dessous :
```bash
pip install -r requirements.txt
``` 
Pour un bon fonctionnement vous aurez peut-être des ajustements à faire.

## Premier lancement
Pour lancer le bot il suffit d'exécuter la commande :
```bash
python3 bot.py
```

## Hébergement
Si vous souhaitez héberger le bot il y a déjà quelques outils (un [script](host/bot_python.sh) de lancement et un [service systemd](host/discord.service)) dans le répertoire [host](host). Il vous reste juste à modifier les path dans le fichier [dicord.service](host/discord.service) et l'activer au démarrage de votre serveur.

# Contributions
Les contributions pour le bot sont les bienvenues !

## TODO :
- [ ] Refacto
- [ ] Mettre à jour le fichier requirements.txt
- [ ] Patch scrapper EPIC
- [ ] Patch auto EDT
- [ ] ban/unban commande