import threading
import time
from . import comptage_1
from . import alarme_1

class Defaut_1(threading.Thread):
    # Etat de défaut local à la voie 1
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {1: 0, 10: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {1: 0}

    def __init__(self, limite_inferieure, limite_superieure, D1_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D1_ON = D1_ON

    def run(self):
        while True:
            if self.D1_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 1
                self.valeur = comptage_1.Frequence_1_Thread.compteur[10]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[1] = 1
                    self.eta_defaut[10] = self.valeur
                    if self.email_send_defaut[1] == 0:
                        self.email_send_defaut[1] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_1.Alarme1.alarme_resultat[1] == 0:
                    self.eta_defaut[1] = 2
                    self.eta_defaut[10] = self.valeur
                    if self.email_send_defaut[1] == 0:
                        self.email_send_defaut[1] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[1] = 0
                    self.email_send_defaut[1] = 0
                    self.eta_defaut[10] = 0

            if self.D1_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[1] = 0
                break
