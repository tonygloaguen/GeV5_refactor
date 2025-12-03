ARM_DELAY_S = 5  # anti faux départ
# -*- coding: utf-8 -*-
import time
import random
from math import sqrt
import threading
from collections import deque
import requests

# Modules
import simulateur
import defaut_11
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12

class Frequence_11_Thread(threading.Thread):
    compteur = {11: 0, 110: 0}
    variance = {11: 0}
    LD = {11: 0}

    def __init__(self, sampling, D11_ON, base_url, sim):
        threading.Thread.__init__(self)
        self.frequence = 0
        self.sampling = sampling
        self.fifo = deque(maxlen=int(10 * sampling))
        self.fifo_stat = deque(maxlen=int(36000 * sampling))
        self.compteur_old = 0
        self.D11_ON = D11_ON
        self.base_url = base_url
        self.sim = sim

    def increaserev_11(self, channel):
        self.frequence += 1
        return self.frequence
    
    def correction_formula(self, impulses):
        if impulses <= 950:
            return impulses
        else:
            a0 = 0.0000000000001089
            a1 = -0.000000001664
            a2 = 0.00002223
            a3 = 1.156
            a4 = -0.092
            return a0*impulses**4 + a1*impulses**3 + a2*impulses**2 + a3*impulses + a4

    def run(self):
        while True:
            if self.D11_ON == 1:
                time.sleep(0.1)
                # Essaye de récupérer la fréquence depuis l'API du hub distant
                if self.sim == 0:
                    try:
                        self.frequence = int(self.fetch_and_process_data(self.base_url))
                    except Exception:
                        self.frequence = 0
                else:
                    self.frequence = random.randint(950, 1050) * simulateur.Application.multiplier[0]

                # Blocage du comptage si génération PDF en cours
                if all(alarme.pdf_gen[i] == 0 for i, alarme in enumerate([
                    alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                    alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                    alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)):

                    frequence_filtree = self.correction_formula(self.frequence)
                    val = frequence_filtree / 0.1

                    self.fifo.append(val)
                    self.fifo_stat.append(val)

                    # moyenne glissante
                    moy = round((sum(self.fifo) / len(self.fifo)), 0)
                    # Toujours garder le canal diagnostique (X0)
                    self.compteur[110] = moy

                    # Si pas de défaut => on expose la valeur, sinon on force à 0
                    if defaut_11.Defaut_11.eta_defaut[11] == 0:
                        self.compteur[11] = moy
                    else:
                        self.compteur[11] = 0

                    # LD (bruit de fond + 8.4 * sqrt)
                    stat = sum(self.fifo_stat) / max(1, len(self.fifo_stat))
                    self.LD[11] = stat + 8.4 * sqrt(stat)
                    
                    # variance protégée
                    if self.compteur[11] != 0:
                        self.variance[11] = self.compteur_old / self.compteur[11]
                    self.compteur_old = self.compteur[11]
                
                self.frequence = 0

            if self.D11_ON == 0:
                self.compteur[11] = -1
                break
            
    def fetch_and_process_data(self, base_url):
        """
        Récupère les données de l'API /data et renvoie la valeur utile du canal.
        On tente d'abord data['comptage'][index-1], sinon on retombe sur la série 'compteur_*' de la BDD.
        """
        resp = requests.get(f"{base_url}/data", timeout=2.5)
        resp.raise_for_status()
        data = resp.json()

        # 1) Essayer la liste 'comptage' directe (index 0-based)
        try:
            val = data.get('comptage', [])[10]
            if isinstance(val, (int, float)) and val is not None:
                return val
        except Exception:
            pass

        # 2) Fallback: utiliser les séries historisées 'compteur_1..4' selon la voie locale sur ce hub
        # Mapping local: sur ce hub, la voie 11 correspond à la série 'compteur_3'.
        key = "compteur_3"
        series = data.get(key, [])
        if isinstance(series, list) and series:
            try:
                return int(series[-1])
            except Exception:
                try:
                    return int(float(series[-1]))
                except Exception:
                    return 0
        return 0
