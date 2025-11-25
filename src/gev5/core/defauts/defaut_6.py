import threading
import time
from ..comptage import comptage_6
from ..alarmes import alarme_6

class Defaut_6(threading.Thread):
    # Etat de défaut local à la voie 6
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {6: 0, 60: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {6: 0}

    def __init__(self, limite_inferieure, limite_superieure, D6_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D6_ON = D6_ON

    def run(self):
        while True:
            if self.D6_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 6
                self.valeur = comptage_6.Frequence_6_Thread.compteur[60]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[6] = 1
                    self.eta_defaut[60] = self.valeur
                    if self.email_send_defaut[6] == 0:
                        self.email_send_defaut[6] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_6.Alarme6.alarme_resultat[6] == 0:
                    self.eta_defaut[6] = 2
                    self.eta_defaut[60] = self.valeur
                    if self.email_send_defaut[6] == 0:
                        self.email_send_defaut[6] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[6] = 0
                    self.email_send_defaut[6] = 0
                    self.eta_defaut[60] = 0

            if self.D6_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[6] = 0
                break
