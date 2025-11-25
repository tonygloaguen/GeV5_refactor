🚀 GEV5 – Nouvelle Architecture Python

Système de contrôle et d’analyse radiologique – Version refactorisée

Ce dépôt contient la nouvelle architecture logicielle complète du système GEV5.
Il s’agit d’un refactor profond visant à :

structurer proprement un ancien code monolithique (GeV5_Moteur.py)

isoler les responsabilités métier (comptage, alarmes, défauts, courbes, etc.)

créer un moteur modulaire, maintenable, testable

préparer une fusion progressive des 12 modules dupliqués (par voie)

isoler hardware / web / config

supprimer la dépendance au script legacy

📁 Architecture du projet
GEV5/
├── run.py                      # Point d'entrée principal
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce document
├── .gitignore
│
├── src/
│   └── gev5/
│       ├── main.py             # Démarrage officiel du moteur
│       │
│       ├── boot/
│       │   ├── loader.py       # Charge Parametres.db → SystemConfig
│       │   └── starter.py      # Orchestrateur du système
│       │
│       ├── core/               # Nouvelle logique métier propre
│       │   ├── comptage/
│       │   │   └── __init__.py (start_comptage)
│       │   ├── alarmes/
│       │   │   └── __init__.py (start_alarmes)
│       │   ├── defauts/
│       │   │   └── __init__.py (start_defauts)
│       │   └── courbes/
│       │       └── __init__.py (start_courbes)
│       │
│       ├── hardware/           # (à venir) Unipi, EVOK, capteurs, comms
│       ├── web/                # (à venir) Flask & API REST
│       ├── utils/
│       │   ├── config.py       # SystemConfig
│       │   └── logging.py      # Logger unifié
│       │
│       └── legacy/             # Code historique pré-refactor
│           ├── comptage_1.py … comptage_12.py
│           ├── alarme_1.py … alarme_12.py
│           ├── defaut_1.py … defaut_12.py
│           ├── courbe_1.py … courbe_12.py
│           └── GeV5_Moteur.py  # Conservé en référence
│
├── templates/                  # HTML – Interface Web (Flask)
├── static/                     # CSS / JS / images / sons / modèles YOLO
├── images/
├── temp/
└── tests/                      # Tests unitaires

▶️ Lancer le système
1. Créer l’environnement virtuel
python -m venv .venv


Activer :

Windows
.venv\Scripts\activate

Linux / Raspberry Pi
source .venv/bin/activate


Installer les dépendances :

pip install -r requirements.txt

2. Lancer GEV5 (nouvelle architecture)

Méthode officielle :

python run.py


Ou :

python -m src.gev5.main

3. Arrêter définitivement l’ancien moteur

Le fichier legacy/GeV5_Moteur.py est seulement conservé pour référence.
Il n’est plus utilisé comme point d’entrée.

Si un service systemd existait, remplacer l’ancien :

ExecStart=/usr/bin/python3 /home/pi/GEV5/GeV5_Moteur.py


par :

ExecStart=/usr/bin/python3 /home/pi/GEV5/run.py
WorkingDirectory=/home/pi/GEV5

🧠 Philosophie du refactor

La nouvelle architecture repose sur 5 principes clés :

1. Découpler les responsabilités

Chaque brique métier a un dossier dédié :

comptage

alarmes

défauts

courbes

hardware

web

config / utils

2. Centraliser le démarrage

starter.py orchestre tout le système :
comptage → alarmes → défauts → courbes → hardware → web → watchdog → stockage.

3. Maintenir la compatibilité

Les modules historiques restent disponibles via legacy,
ce qui permet un refactor progressif sans risque.

4. Préparer la factorisation

Les 12 clones (par voie) pourront ensuite être remplacés par :

1 classe Comptage paramétrée

1 classe Alarme paramétrée

1 classe Defaut paramétrée

1 classe Courbe paramétrée

5. Isoler hardware et web

Pour pouvoir tester, simuler, et porter le système n’importe où.

🔧 Prochaines étapes du refactor

✔ Défauts déplacés → core/defauts/start_defauts
✔ Courbes déplacées → core/courbes/start_courbes
✔ Comptage déplacé → core/comptage/start_comptage
✔ Alarmes déplacées → core/alarmes/start_alarmes

🚧 À venir
1. Regrouper le hardware

Unipi, EVOK, Modbus, eVx, F2C, USB, disque, caméra, ANPR…

2. Extraire et structurer Flask

/web/app.py

/web/routes/*

gestion des traductions (static/lang)

3. Fusionner les 12 modules par famille

(énorme gain en maintenabilité)

4. Ajouter une batterie de tests
👨‍💻 Développement

Format recommandé pour lancer le projet dans VS Code :

.vscode/settings.json :

{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe"
}


.vscode/launch.json :

{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "GEV5 Engine",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/run.py",
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}

📝 Licence

Projet interne – propriété TG
Usage strictement réservé aux environnements autorisés.

📫 Contact

Pour assistance technique, support, ou évolution du moteur :
Tony Gloaguen