# Openclassrooms - Créez une API sécurisée en utilisant Django REST

MVP (Minimal Viable Product) du projet Softdesk.

Son objectif est de developper une application ITS (Issue Tracking System) permettant de remonter et suivre des problèmes techniques.

L'interface API (Application Programming Interface) developpée via le framework Django REST doit notamment comprendre les fonctionnalités suivantes :

Inscription ouverte afin de disposer d'un compte utilisateur et d'un mot de passe\
Accès aux fonctionnalités de l'API uniquement aux utilisateurs connectés\
Fonctionnalités CRUD (Create Read Update Delete) sur les differents objets en base de données (Projets, Problèmes et Commentaires)\



## Installation

* Installer Python 3.11 :
 https://www.python.org/  \
  _Compatibilité avec d'autres versions probable mais non testée_

* Télécharger et extraire le repository suivant depuis github :\
https://github.com/Tod92/Projet10

* Se positionner dans le répértoire où le repository a été extrait :\
  `..\Projet10-main\`

* Créer l'environnement virtuel :\
_Installation de venv requise : pip install venv_\
  `python -m venv env`

* Activer l'environnement virtuel :\
  `..\Projet10-main\env\Scripts\activate`

* Installer les packages Python néçessaire à l'execution du script :\
  `(env)..\Projet10-main\pip install -r requirements.txt`

* Installation terminée. Désactivation de l'environnement virtuel :\
  `deactivate`

## Execution du Serveur API en local :

* L'environnement virtuel doit etre activé :\
  `..\Projet10-main\env\Scripts\activate`

* Executer le script python :\
  `..\Projet10-main\softdesk\python manage.py runserver`

* Depuis votre navigateur web :\
  `http://127.0.0.1:8000`

* Après avoir utilisé le site, penser à désactiver l'environnement virtuel :\
  `deactivate`

## Tests de l'application :

La base de donnée a été peuplée avec les comptes et mots de passe de test suivants :

admin :
user : marge\
password : ILoveOmer

users :
user : bart\
password : LisaEstNulle

user : lisa\
password : BartEstNul



## fonctionnalités :


## Historique

* 19/06/2023 : Finalisation et tests avec population de la base de données
* 06/06/2023 : Demarrage permission
* 25/05/2023 : Bascule ModelViewSet + NestedRouters
* 15/05/2023 : premières requetes postman ok
* 10/05/2023 : integration simple jwt
* 09/05/2023 : init viewsets
* 07/05/2023 : Modèles crées
* 05/05/2023 : Démarrage du projet

## Credits
Projet réalisé par Thomas DERUERE\
Assisté par Idriss BEN GELOUNE (Mentor Openclassrooms)
