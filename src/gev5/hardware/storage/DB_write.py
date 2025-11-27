import threading
import time
import datetime
import sqlite3
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import vitesse_chargement, acquittement

class DataRecorder(threading.Thread):
    """
    Writer robuste:
      - déclenche sur FIN stable (front descendant) OU sur TIMEOUT après START.
      - connexion SQLite persistante (WAL), pas de sleep bloquant.
    """
    DB_PATH = "/home/pi/Partage/Base_donnees/Db_GeV5.db"

    # réglages
    TICK_S          = 0.05    # 50 ms
    END_STABLE_S    = 0.05    # stabilité fin de passage (descente) 80 ms
    START_TIMEOUT_S = 5.0    # si pas de fin détectée après départ, on force l'écriture
    REFRAC_S        = 0.50    # réfractaire après écriture (évite les doubles)

    def __init__(self):
        super().__init__(daemon=True)
        self._active_prev     = False
        self._inactive_since  = None
        self._last_start_ts   = None
        self._last_write_ts   = 0.0
        self.comment_point_chaud = "N.A."

        # Connexion persistante SQLite
        self.conn = sqlite3.connect(self.DB_PATH, timeout=5.0, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA busy_timeout=3000;")
        self.cur = self.conn.cursor()
        self._ensure_table()
        print("[DB] Writer prêt (WAL).")

    def _ensure_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Db_GeV5 (
            id INTEGER PRIMARY KEY,
            bdf1 INT, bdf2 INT, bdf3 INT, bdf4 INT, bdf5 INT, bdf6 INT,
            bdf7 INT, bdf8 INT, bdf9 INT, bdf10 INT, bdf11 INT, bdf12 INT,
            seuil1 INT, seuil2 INT, seuil3 INT, seuil4 INT, seuil5 INT, seuil6 INT,
            seuil7 INT, seuil8 INT, seuil9 INT, seuil10 INT, seuil11 INT, seuil12 INT,
            Der_pass1 INT, Der_pass2 INT, Der_pass3 INT, Der_pass4 INT, Der_pass5 INT, Der_pass6 INT,
            Der_pass7 INT, Der_pass8 INT, Der_pass9 INT, Der_pass10 INT, Der_pass11 INT, Der_pass12 INT,
            Alarm1 INT, Alarm2 INT, Alarm3 INT, Alarm4 INT, Alarm5 INT, Alarm6 INT,
            Alarm7 INT, Alarm8 INT, Alarm9 INT, Alarm10 INT, Alarm11 INT, Alarm12 INT,
            Defaut1 INT, Defaut2 INT, Defaut3 INT, Defaut4 INT, Defaut5 INT, Defaut6 INT,
            Defaut7 INT, Defaut8 INT, Defaut9 INT, Defaut10 INT, Defaut11 INT, Defaut12 INT,
            Vitesse INT,
            Horodatage DATETIME,
            Commentaires TEXT
        )
        """)
        self.conn.commit()

    @staticmethod
    def _mesures():
        # états "mesure" des 12 voies (1/2 pendant passage selon ta logique)
        list_mesure = [
            alarme_1.Alarme1.mesure[1],   alarme_2.Alarme2.mesure[2],
            alarme_3.Alarme3.mesure[3],   alarme_4.Alarme4.mesure[4],
            alarme_5.Alarme5.mesure[5],   alarme_6.Alarme6.mesure[6],
            alarme_7.Alarme7.mesure[7],   alarme_8.Alarme8.mesure[8],
            alarme_9.Alarme9.mesure[9],   alarme_10.Alarme10.mesure[10],
            alarme_11.Alarme11.mesure[11], alarme_12.Alarme12.mesure[12],
        ]
        eta_point_chaud = [
            alarme_1.Alarme1.etat_point_chaud[1],  alarme_2.Alarme2.etat_point_chaud[2],
            alarme_3.Alarme3.etat_point_chaud[3],  alarme_4.Alarme4.etat_point_chaud[4],
            alarme_5.Alarme5.etat_point_chaud[5],  alarme_6.Alarme6.etat_point_chaud[6],
            alarme_7.Alarme7.etat_point_chaud[7],  alarme_8.Alarme8.etat_point_chaud[8],
            alarme_9.Alarme9.etat_point_chaud[9],  alarme_10.Alarme10.etat_point_chaud[10],
            alarme_11.Alarme11.etat_point_chaud[11], alarme_12.Alarme12.etat_point_chaud[12],
        ]
        return list_mesure, eta_point_chaud

    def _snapshot_values(self):
        return (
            alarme_1.Alarme1.val_deb_mes[1],  alarme_2.Alarme2.val_deb_mes[2],
            alarme_3.Alarme3.val_deb_mes[3],  alarme_4.Alarme4.val_deb_mes[4],
            alarme_5.Alarme5.val_deb_mes[5],  alarme_6.Alarme6.val_deb_mes[6],
            alarme_7.Alarme7.val_deb_mes[7],  alarme_8.Alarme8.val_deb_mes[8],
            alarme_9.Alarme9.val_deb_mes[9],  alarme_10.Alarme10.val_deb_mes[10],
            alarme_11.Alarme11.val_deb_mes[11], alarme_12.Alarme12.val_deb_mes[12],
            alarme_1.Alarme1.suiv[1],  alarme_2.Alarme2.suiv[2],  alarme_3.Alarme3.suiv[3],  alarme_4.Alarme4.suiv[4],
            alarme_5.Alarme5.suiv[5],  alarme_6.Alarme6.suiv[6],  alarme_7.Alarme7.suiv[7],  alarme_8.Alarme8.suiv[8],
            alarme_9.Alarme9.suiv[9],  alarme_10.Alarme10.suiv[10], alarme_11.Alarme11.suiv[11], alarme_12.Alarme12.suiv[12],
            alarme_1.Alarme1.val_max[1],  alarme_2.Alarme2.val_max[2],  alarme_3.Alarme3.val_max[3],  alarme_4.Alarme4.val_max[4],
            alarme_5.Alarme5.val_max[5],  alarme_6.Alarme6.val_max[6],  alarme_7.Alarme7.val_max[7],  alarme_8.Alarme8.val_max[8],
            alarme_9.Alarme9.val_max[9],  alarme_10.Alarme10.val_max[10], alarme_11.Alarme11.val_max[11], alarme_12.Alarme12.val_max[12],
            alarme_1.Alarme1.alarme_resultat[10],  alarme_2.Alarme2.alarme_resultat[20],
            alarme_3.Alarme3.alarme_resultat[30],  alarme_4.Alarme4.alarme_resultat[40],
            alarme_5.Alarme5.alarme_resultat[50],  alarme_6.Alarme6.alarme_resultat[60],
            alarme_7.Alarme7.alarme_resultat[70],  alarme_8.Alarme8.alarme_resultat[80],
            alarme_9.Alarme9.alarme_resultat[90],  alarme_10.Alarme10.alarme_resultat[100],
            alarme_11.Alarme11.alarme_resultat[110], alarme_12.Alarme12.alarme_resultat[120],
            defaut_1.Defaut_1.eta_defaut[1], defaut_2.Defaut_2.eta_defaut[2], defaut_3.Defaut_3.eta_defaut[3], defaut_4.Defaut_4.eta_defaut[4],
            defaut_5.Defaut_5.eta_defaut[5], defaut_6.Defaut_6.eta_defaut[6], defaut_7.Defaut_7.eta_defaut[7], defaut_8.Defaut_8.eta_defaut[8],
            defaut_9.Defaut_9.eta_defaut[9], defaut_10.Defaut_10.eta_defaut[10], defaut_11.Defaut_11.eta_defaut[11], defaut_12.Defaut_12.eta_defaut[12],
            vitesse_chargement.ListWatcher.vitesse[1],
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "{} / {}".format(acquittement.InputWatcher.eta_acq[2], self.comment_point_chaud),
        )

    def _write_row(self, reason: str):
        sql = """
        INSERT INTO Db_GeV5 (
            bdf1,bdf2,bdf3,bdf4,bdf5,bdf6,bdf7,bdf8,bdf9,bdf10,bdf11,bdf12,
            seuil1,seuil2,seuil3,seuil4,seuil5,seuil6,seuil7,seuil8,seuil9,seuil10,seuil11,seuil12,
            Der_pass1,Der_pass2,Der_pass3,Der_pass4,Der_pass5,Der_pass6,Der_pass7,Der_pass8,Der_pass9,Der_pass10,Der_pass11,Der_pass12,
            Alarm1,Alarm2,Alarm3,Alarm4,Alarm5,Alarm6,Alarm7,Alarm8,Alarm9,Alarm10,Alarm11,Alarm12,
            Defaut1,Defaut2,Defaut3,Defaut4,Defaut5,Defaut6,Defaut7,Defaut8,Defaut9,Defaut10,Defaut11,Defaut12,
            Vitesse, Horodatage, Commentaires
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        self.cur.execute(sql, self._snapshot_values())
        self.conn.commit()
        self._last_write_ts = time.time()
        print(f"[DB] Écrit ({reason}).")

    def run(self):
        print("[DB] Thread writer démarré.")
        while True:
            list_mesure, eta_pc = self._mesures()
            if 1 in eta_pc:
                self.comment_point_chaud = "Anomalie bdf avant mesure"

            # "actif" si n'importe quelle voie est en état 1 ou 2
            active = any(x in (1, 2) for x in list_mesure)

            now = time.time()

            # Front montant -> départ
            if active and not self._active_prev:
                print("[DB] Passage détecté (start).")
                self._inactive_since = None
                self._last_start_ts = now

            # Front descendant -> fin candidate
            if (not active) and self._active_prev:
                if self._inactive_since is None:
                    self._inactive_since = now
                elif (now - self._inactive_since) >= self.END_STABLE_S:
                    # FIN stable -> write immédiat
                    if (now - self._last_write_ts) >= self.REFRAC_S:
                        try:
                            self._write_row("fin de passage")
                        except Exception as e:
                            print("[DB][ERR] Écriture:", e)
                        finally:
                            self.comment_point_chaud = "N.A."
                            self._inactive_since = None
                            self._last_start_ts = None

            # Timeout après départ -> write forcé
            if self._last_start_ts is not None and (now - self._last_start_ts) >= self.START_TIMEOUT_S:
                if (now - self._last_write_ts) >= self.REFRAC_S:
                    try:
                        self._write_row("timeout après start")
                    except Exception as e:
                        print("[DB][ERR] Écriture (timeout):", e)
                    finally:
                        self.comment_point_chaud = "N.A."
                        self._inactive_since = None
                        self._last_start_ts = None

            self._active_prev = active
            time.sleep(self.TICK_S)
