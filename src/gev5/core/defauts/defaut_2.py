import threading
import time
from ..comptage import comptage_2
from ..alarmes import alarme_2

class Defaut_2(threading.Thread):
    # Etat de défaut local à la voie 2
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {2: 0, 20: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {2: 0}

    def __init__(self, limite_inferieure, limite_superieure, D2_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D2_ON = D2_ON

    def run(self):
        while True:
            if self.D2_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 2
                self.valeur = comptage_2.Frequence_2_Thread.compteur[20]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[2] = 1
                    self.eta_defaut[20] = self.valeur
                    if self.email_send_defaut[2] == 0:
                        self.email_send_defaut[2] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_2.Alarme2.alarme_resultat[2] == 0:
                    self.eta_defaut[2] = 2
                    self.eta_defaut[20] = self.valeur
                    if self.email_send_defaut[2] == 0:
                        self.email_send_defaut[2] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[2] = 0
                    self.email_send_defaut[2] = 0
                    self.eta_defaut[20] = 0

            if self.D2_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[2] = 0
                break
