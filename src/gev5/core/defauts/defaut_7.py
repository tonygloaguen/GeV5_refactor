import threading
import time
from ..comptage import comptage_7
from ..alarmes import alarme_7

class Defaut_7(threading.Thread):
    # Etat de défaut local à la voie 7
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {7: 0, 70: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {7: 0}

    def __init__(self, limite_inferieure, limite_superieure, D7_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D7_ON = D7_ON

    def run(self):
        while True:
            if self.D7_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 7
                self.valeur = comptage_7.Frequence_7_Thread.compteur[70]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[7] = 1
                    self.eta_defaut[70] = self.valeur
                    if self.email_send_defaut[7] == 0:
                        self.email_send_defaut[7] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_7.Alarme7.alarme_resultat[7] == 0:
                    self.eta_defaut[7] = 2
                    self.eta_defaut[70] = self.valeur
                    if self.email_send_defaut[7] == 0:
                        self.email_send_defaut[7] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[7] = 0
                    self.email_send_defaut[7] = 0
                    self.eta_defaut[70] = 0

            if self.D7_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[7] = 0
                break
