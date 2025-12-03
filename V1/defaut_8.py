import threading
import time
from ..comptage import comptage_8
from ..alarmes import alarme_8

class Defaut_8(threading.Thread):
    # Etat de défaut local à la voie 8
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {8: 0, 80: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {8: 0}

    def __init__(self, limite_inferieure, limite_superieure, D8_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D8_ON = D8_ON

    def run(self):
        while True:
            if self.D8_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 8
                self.valeur = comptage_8.Frequence_8_Thread.compteur[80]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[8] = 1
                    self.eta_defaut[80] = self.valeur
                    if self.email_send_defaut[8] == 0:
                        self.email_send_defaut[8] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_8.Alarme8.alarme_resultat[8] == 0:
                    self.eta_defaut[8] = 2
                    self.eta_defaut[80] = self.valeur
                    if self.email_send_defaut[8] == 0:
                        self.email_send_defaut[8] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[8] = 0
                    self.email_send_defaut[8] = 0
                    self.eta_defaut[80] = 0

            if self.D8_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[8] = 0
                break
