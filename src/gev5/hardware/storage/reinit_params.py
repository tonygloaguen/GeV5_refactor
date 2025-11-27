import sqlite3

# Chemin de la base de données
db_path = '/home/pi/Partage/Base_donnees/Parametres.db'

# Connexion à la base de données
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Création de la table des paramètres
c.execute('''CREATE TABLE IF NOT EXISTS Parametres (
                nom TEXT,
                valeur TEXT
            )''')

# Insertion des paramètres
params = [
    ("Nom_portique", "Portique eV5"),
    ("sample_time", "0.5"),
    ("distance_cellules", "0.5"),
    ("Mode_sans_cellules", "0"),
    ("multiple", "1.5"),
    ("seuil2", "10000"),
    ("low", "300"),
    ("high", "20000"),
    ("camera", "0"),
    ("modbus", "0"),
    ("eVx", "0"),
    ("mod_SMS", "0"),
    ("date_prochaine_visite", "01/07/2030"),
    ("D1_ON", "1"),
    ("D2_ON", "1"),
    ("D3_ON", "0"),
    ("D4_ON", "0"),
    ("D5_ON", "0"),
    ("D6_ON", "0"),
    ("D7_ON", "0"),
    ("D8_ON", "0"),
    ("D9_ON", "0"),
    ("D10_ON", "0"),
    ("D11_ON", "0"),
    ("D12_ON", "0"),

    ("D1_nom", "Détecteur 1"),
    ("D2_nom", "Détecteur 2"),
    ("D3_nom", "Détecteur 3"),
    ("D4_nom", "Détecteur 4"),
    ("D5_nom", "Détecteur 5"),
    ("D6_nom", "Détecteur 6"),
    ("D7_nom", "Détecteur 7"),
    ("D8_nom", "Détecteur 8"),
    ("D9_nom", "Détecteur 9"),
    ("D10_nom", "Détecteur 10"),
    ("D11_nom", "Détecteur 11"),
    ("D12_nom", "Détecteur 12"),
    ("Rem_IP", "--"),
    ("Rem_IP_2", "--"), 
    ("RTSP", "--"),
    ("IP", "--"),
    ("smtp_server", "--"),
    ("port", "25"),
    ("login", "None"),
    ("password", "None"),
    ("sender", "GeV5@berthold.com"),
    ("recipients", "--"),
    ("SMS", "--,--"),
    ("PIN_1" , "26"),
    ("PIN_2" , "16"),
    ("PIN_3" , "6"),
    ("PIN_4" , "18"),
    ("SIM" , "0"),
    ("suiv_block", "1"),
    ("language", "fr")
]

# Insertion des paramètres dans la base de données
c.executemany('INSERT INTO Parametres (nom, valeur) VALUES (?, ?)', params)

# Sauvegarde (commit) et fermeture de la connexion
conn.commit()
conn.close()