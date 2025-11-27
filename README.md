🚀 GEV5 – Nouvelle Architecture Python

Système de contrôle et d’analyse radiologique – Version refactorisée

Ce dépôt contient la nouvelle architecture logicielle complète du système GEV5.
isoler les responsabilités métier (comptage, alarmes, défauts, courbes, etc.)
isoler hardware / web / config
supprimer la dépendance au script legacy

Il s’agit d’un refactor profond visant à :
- Structurer proprement l’ancien code monolithique (GeV5_Moteur.py)
- Isoler les responsabilités métier (comptage, alarmes, défauts, courbes, etc.)
- Créer un moteur modulaire, maintenable, testable
- Fusionner progressivement les 12 modules dupliqués (par voie)
- Isoler hardware / web / config
- Supprimer toute dépendance au code legacy


📦 gev5
├── boot
│   ├── loader.py
│   ├── starter.py
│   └── __init__.py
├── core
│   ├── acquittement
│   │   ├── acquittement.py
│   │   └── __init__.py
│   ├── alarmes
│   │   ├── alarme_1.py ... alarme_12.py
│   │   └── __init__.py
│   ├── comptage
│   │   ├── comptage_1.py ... comptage_12.py
│   │   └── __init__.py
│   ├── courbes
│   │   ├── courbe_1.py ... courbe_12.py
│   │   └── __init__.py
│   ├── defauts
│   │   ├── defaut_1.py ... defaut_12.py
│   │   └── __init__.py
│   ├── simulation
│   │   ├── simulateur.py
│   │   └── __init__.py
│   ├── vitesse
│   │   └── __init__.py
│   └── __init__.py
├── hardware
│   ├── modem
│   │   ├── Modem_SMS
│   │   │   └── switch_to_modem.sh
│   │   ├── envoi_sms.py
│   │   ├── test_SMS.py
│   │   └── test_SMS_2.py
│   ├── storage
│   │   ├── collect_bdf.py
│   │   ├── db_patch.py
│   │   ├── DB_write.py
│   │   ├── email.py
│   │   ├── Envoi_email.py
│   │   ├── rapport_pdf.py
│   │   ├── reinit_credent.py
│   │   └── reinit_params.py
│   ├── system
│   │   └── Thread_Watchdog.py
│   ├── Check_open_cell.py
│   ├── Chkdisk.py
│   ├── Driver_F2C.py
│   ├── etat_cellule_1.py
│   ├── etat_cellule_2.py
│   ├── evx_f2c.py
│   ├── eVx_interface.py
│   ├── interface.py
│   ├── io_broker.py
│   ├── modbus_interface.py
│   ├── network_config.py
│   ├── prise_photo.py
│   ├── relais.py
│   ├── Svr_Unipi.py
│   ├── test_ANPR.py
│   ├── test_camera.py
│   ├── USB_control.py
│   ├── vitesse_chargement.py
│   └── __init__.py
├── tests
│   ├── alarm_bus.py
│   ├── auto_tester.py
│   ├── email_tester.py
│   ├── test.py
│   ├── test_in.py
│   └── test_ws.py
├── tools
│   ├── any_dsk_srv.py
│   ├── patch_alarme_all.py
│   └── sitecustomize.py
├── utils
│   ├── config.py
│   ├── logging.py
│   └── __init__.py
├── web
│   ├── routes
│   │   └── api.py
│   ├── app.py
│   ├── legacy_api.py
│   └── __init__.py
├── main.py
└── __init__.py
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

✔ Réalisé
1. Hardware regroupé

Tous les modules matériels (Unipi, EVOK, Modbus, eVx, F2C, USB, disque, caméra, ANPR…) sont désormais organisés dans le dossier `hardware/`.

2. Flask extrait et structuré

L’application web est structurée dans `/web/app.py` et les routes dans `/web/routes/`.
La gestion des traductions est assurée via `static/lang`.

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