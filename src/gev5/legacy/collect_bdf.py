import threading
import time
import sqlite3
import comptage_1, comptage_2, comptage_3, comptage_4, comptage_5, comptage_6, comptage_7, comptage_8, comptage_9, comptage_10, comptage_11, comptage_12

class DataCollector(threading.Thread):
    def __init__(self, interval=30, db_path='/home/pi/Partage/Base_donnees/Bruit_de_fond.db'):
        threading.Thread.__init__(self)
        self.interval = interval
        self.db_path = db_path
        self.db_init = 0

    def run(self):
        self.init_db()
        while True:
            if self.db_init == 1: # Pour que la base ne stocke pas 0 au démarrage
                self.collect_data()
            self.db_init = 1
            time.sleep(self.interval)

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compteurs (
                    timestamp TEXT,
                    compteur_1 REAL,
                    compteur_2 REAL,
                    compteur_3 REAL,
                    compteur_4 REAL,
                    compteur_5 REAL,
                    compteur_6 REAL,
                    compteur_7 REAL,
                    compteur_8 REAL,
                    compteur_9 REAL,                     
                    compteur_10 REAL, 
                    compteur_11 REAL, 
                    compteur_12 REAL
                )
            ''')
            conn.commit()

    def collect_data(self):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        data = [timestamp]
        data.append(comptage_1.Frequence_1_Thread.compteur[1])
        data.append(comptage_2.Frequence_2_Thread.compteur[2])
        data.append(comptage_3.Frequence_3_Thread.compteur[3])
        data.append(comptage_4.Frequence_4_Thread.compteur[4])
        data.append(comptage_5.Frequence_5_Thread.compteur[5])
        data.append(comptage_6.Frequence_6_Thread.compteur[6])
        data.append(comptage_7.Frequence_7_Thread.compteur[7])
        data.append(comptage_8.Frequence_8_Thread.compteur[8])
        data.append(comptage_9.Frequence_9_Thread.compteur[9]) 
        data.append(comptage_10.Frequence_10_Thread.compteur[10]) 
        data.append(comptage_11.Frequence_11_Thread.compteur[11]) 
        data.append(comptage_12.Frequence_12_Thread.compteur[12])
        try:
            self.store_data(data)
        except:
            print("La base n'existe plus ou est corrompue")

    def store_data(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO compteurs (timestamp, compteur_1, compteur_2, compteur_3, compteur_4, compteur_5, compteur_6, compteur_7, compteur_8, compteur_9, compteur_10, compteur_11, compteur_12)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()

