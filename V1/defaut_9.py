import threading
import time
from ..comptage import comptage_9
from ..alarmes import alarme_9

class Defaut_9(threading.Thread):
    # Etat de défaut local à la voie 9
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {9: 0, 90: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {9: 0}

    def __init__(self, limite_inferieure, limite_superieure, D9_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D9_ON = D9_ON

    def run(self):
        while True:
            if self.D9_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 9
                self.valeur = comptage_9.Frequence_9_Thread.compteur[90]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[9] = 1
                    self.eta_defaut[90] = self.valeur
                    if self.email_send_defaut[9] == 0:
                        self.email_send_defaut[9] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_9.Alarme9.alarme_resultat[9] == 0:
                    self.eta_defaut[9] = 2
                    self.eta_defaut[90] = self.valeur
                    if self.email_send_defaut[9] == 0:
                        self.email_send_defaut[9] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[9] = 0
                    self.email_send_defaut[9] = 0
                    self.eta_defaut[90] = 0

            if self.D9_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[9] = 0
                break
