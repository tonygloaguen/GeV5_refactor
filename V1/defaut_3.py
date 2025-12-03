import threading
import time
from ..comptage import comptage_3
from ..alarmes import alarme_3

class Defaut_3(threading.Thread):
    # Etat de défaut local à la voie 3
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {3: 0, 30: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {3: 0}

    def __init__(self, limite_inferieure, limite_superieure, D3_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D3_ON = D3_ON

    def run(self):
        while True:
            if self.D3_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 3
                self.valeur = comptage_3.Frequence_3_Thread.compteur[30]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[3] = 1
                    self.eta_defaut[30] = self.valeur
                    if self.email_send_defaut[3] == 0:
                        self.email_send_defaut[3] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_3.Alarme3.alarme_resultat[3] == 0:
                    self.eta_defaut[3] = 2
                    self.eta_defaut[30] = self.valeur
                    if self.email_send_defaut[3] == 0:
                        self.email_send_defaut[3] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[3] = 0
                    self.email_send_defaut[3] = 0
                    self.eta_defaut[30] = 0

            if self.D3_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[3] = 0
                break
