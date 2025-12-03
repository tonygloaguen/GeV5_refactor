import threading
import time
from ..comptage import comptage_5
from ..alarmes import alarme_5

class Defaut_5(threading.Thread):
    # Etat de défaut local à la voie 5
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {5: 0, 50: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {5: 0}

    def __init__(self, limite_inferieure, limite_superieure, D5_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D5_ON = D5_ON

    def run(self):
        while True:
            if self.D5_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 5
                self.valeur = comptage_5.Frequence_5_Thread.compteur[50]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[5] = 1
                    self.eta_defaut[50] = self.valeur
                    if self.email_send_defaut[5] == 0:
                        self.email_send_defaut[5] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_5.Alarme5.alarme_resultat[5] == 0:
                    self.eta_defaut[5] = 2
                    self.eta_defaut[50] = self.valeur
                    if self.email_send_defaut[5] == 0:
                        self.email_send_defaut[5] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[5] = 0
                    self.email_send_defaut[5] = 0
                    self.eta_defaut[50] = 0

            if self.D5_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[5] = 0
                break
