import threading
import time
from ..comptage import comptage_4
from ..alarmes import alarme_4

class Defaut_4(threading.Thread):
    # Etat de défaut local à la voie 4
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {4: 0, 40: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {4: 0}

    def __init__(self, limite_inferieure, limite_superieure, D4_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D4_ON = D4_ON

    def run(self):
        while True:
            if self.D4_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 4
                self.valeur = comptage_4.Frequence_4_Thread.compteur[40]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[4] = 1
                    self.eta_defaut[40] = self.valeur
                    if self.email_send_defaut[4] == 0:
                        self.email_send_defaut[4] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_4.Alarme4.alarme_resultat[4] == 0:
                    self.eta_defaut[4] = 2
                    self.eta_defaut[40] = self.valeur
                    if self.email_send_defaut[4] == 0:
                        self.email_send_defaut[4] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[4] = 0
                    self.email_send_defaut[4] = 0
                    self.eta_defaut[40] = 0

            if self.D4_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[4] = 0
                break
