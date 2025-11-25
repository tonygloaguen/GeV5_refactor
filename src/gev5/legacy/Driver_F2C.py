import datetime
import time
import socket
import threading
import re

# Imports modules externes pour les valeurs (à conserver selon ton appli)
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import etat_cellule_1, etat_cellule_2
import comptage_1, comptage_2, comptage_3, comptage_4, comptage_5, comptage_6, comptage_7, comptage_8, comptage_9, comptage_10, comptage_11, comptage_12

def format_f2c_value(val):
    s = "{:.4e}".format(val)
    return re.sub(r'e([+-])(\d+)', lambda m: f"e{m.group(1)}{int(m.group(2)):03d}", s)

def get_system_datetime():
    now = datetime.datetime.now()
    return now.strftime("%y%m%d%H%M%S")

def calculate_checksum(trame):
    """Checksum ASCII modulo 256, sur la trame complète sans le checksum ni l’astérisque de fin."""
    somme = sum(ord(c) for c in trame)
    csm = somme % 256
    return f"{csm:02X}"

class F2CThread(threading.Thread):
    def __init__(self, host="0.0.0.0", port=9000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.data = 0

    def recover_values(self):
        self.RegMean = [getattr(globals()[f"comptage_{i+1}"], f"Frequence_{i+1}_Thread").compteur[i+1] for i in range(12)]
        self.RegMax = [getattr(globals()[f"alarme_{i+1}"], f"Alarme{i+1}").val_max[i+1] for i in range(12)]
        self.RegSuiveur = [getattr(globals()[f"alarme_{i+1}"], f"Alarme{i+1}").suiv[i+1] for i in range(12)]
        self.RegLD = [getattr(globals()[f"comptage_{i+1}"], f"Frequence_{i+1}_Thread").LD[i+1] for i in range(12)]
        self.RegAlarmRadio = [getattr(globals()[f"alarme_{i+1}"], f"Alarme{i+1}").alarme_resultat[i+1] for i in range(12)]
        self.RegAlarmTech = [getattr(globals()[f"defaut_{i+1}"], f"Defaut_{i+1}").eta_defaut[i+1] for i in range(12)]
        self.RegInfoCell = [etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]]

    def get_channel_state(self, idx):
        mode = 0
        if self.RegAlarmTech[idx] == 1:
            mode |= 0x01
        elif self.RegAlarmTech[idx] == 2:
            mode |= 0x02
        return f"{mode:08X}"

    def get_channel_mode(self, idx):
        mode = 0
        if self.RegAlarmRadio[idx] == 1:
            mode |= 0x01
        elif self.RegAlarmRadio[idx] == 2:
            mode |= 0x02
        return f"{mode:08X}"

    def get_system_state(self):
        mode = 0
        if self.RegInfoCell[0] == 1:
            mode |= 0x01
        elif self.RegInfoCell[1] == 1:
            mode |= 0x02
        return f"{mode:08X}"

    def simulate_fr21_response(self, mbr):
        idx = int(mbr)
        data = [
            get_system_datetime(),
            self.get_channel_state(idx),
            self.get_channel_mode(idx),
            self.get_system_state(),
            format_f2c_value(self.RegMean[idx]),
            format_f2c_value(self.RegMax[idx]),
            format_f2c_value(self.RegSuiveur[idx]),
            "00002215", "00182221", "00316578",
            format_f2c_value(self.RegLD[idx]),
            format_f2c_value(0), format_f2c_value(0),
            format_f2c_value(0), format_f2c_value(0), format_f2c_value(0),
        ]
        status = ["00:2000", "00:0000", "F0:0000", "00:0000", "00:0000", "00:0000", "00:0000", "00:0000", "00:0000",
                  "00:0000", "00:0000", "00:0000", "00:0000", "00:0000", "00:0000"]
        data += status
        return " ".join(data)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"Serveur F2C actif sur {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                print(f"[CONNECT] {addr}")
                with conn:
                        while True:
                            try:
                                data = conn.recv(1024)
                                if not data:
                                    break  # Client a fermé la connexion
                                data = data.strip().decode()                                
                                self.recover_values()

                                # Réponse spéciale pour « valeurs suivantes » : *0001900101000002FEEF3FFF70* (mbr 01, 02, ... 11)
                                match_suiv = re.match(r"\*0001900101([0-9]{2})0002FEEF3FFF70\*", data)
                                if match_suiv:
                                    mbr = match_suiv.group(1)
                                    trame_sans_checksum = f"*9001000101{mbr}0002*"
                                    checksum = calculate_checksum(trame_sans_checksum)
                                    trame = f"{trame_sans_checksum}{checksum}*\r\n"
                                    conn.sendall(trame.encode())
                                    continue  # On traite pas plus loin

                                # Réponse complète à la première demande pour chaque MBR
                                match_first = re.match(r"\*0001900101([0-9]{2})0001FEEF3FFF70\*", data)
                                if match_first:
                                    mbr = match_first.group(1)
                                    reponse_data = self.simulate_fr21_response(mbr)
                                    trame_sans_checksum = f"*9001000101{mbr}0001FEEF3FFF70{reponse_data}*"
                                    checksum = calculate_checksum(trame_sans_checksum)
                                    trame = f"{trame_sans_checksum}{checksum}*\r\n"
                                    conn.sendall(trame.encode())
                                    continue

                                # Cas par défaut : réponse « NO_REPLY »
                                trame_sans_checksum = "*9001000100000000FEEF3FFF70NO_REPLY*"
                                checksum = calculate_checksum(trame_sans_checksum)
                                trame = f"{trame_sans_checksum}{checksum}*\r\n"
                                conn.sendall(trame.encode())

                            except Exception as e:
                                print(f"[ERROR] {e}")

                # Pause entre deux requêtes
                time.sleep(0.5)

