import threading
import time
from ..comptage import comptage_10
from ..alarmes import alarme_10

class Defaut_10(threading.Thread):
    # Etat de défaut local à la voie 10
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {10: 0, 100: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {10: 0}

    def __init__(self, limite_inferieure, limite_superieure, D10_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D10_ON = D10_ON

    def run(self):
        while True:
            if self.D10_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 10
                self.valeur = comptage_10.Frequence_10_Thread.compteur[100]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[10] = 1
                    self.eta_defaut[100] = self.valeur
                    if self.email_send_defaut[10] == 0:
                        self.email_send_defaut[10] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_10.Alarme10.alarme_resultat[10] == 0:
                    self.eta_defaut[10] = 2
                    self.eta_defaut[100] = self.valeur
                    if self.email_send_defaut[10] == 0:
                        self.email_send_defaut[10] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[10] = 0
                    self.email_send_defaut[10] = 0
                    self.eta_defaut[100] = 0

            if self.D10_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[10] = 0
                break
