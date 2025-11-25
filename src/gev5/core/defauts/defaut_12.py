import threading
import time
from ..comptage import comptage_12
from ..alarmes import alarme_12

class Defaut_12(threading.Thread):
    # Etat de défaut local à la voie 12
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {12: 0, 120: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {12: 0}

    def __init__(self, limite_inferieure, limite_superieure, D12_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D12_ON = D12_ON

    def run(self):
        while True:
            if self.D12_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 12
                self.valeur = comptage_12.Frequence_12_Thread.compteur[120]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[12] = 1
                    self.eta_defaut[120] = self.valeur
                    if self.email_send_defaut[12] == 0:
                        self.email_send_defaut[12] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_12.Alarme12.alarme_resultat[12] == 0:
                    self.eta_defaut[12] = 2
                    self.eta_defaut[120] = self.valeur
                    if self.email_send_defaut[12] == 0:
                        self.email_send_defaut[12] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[12] = 0
                    self.email_send_defaut[12] = 0
                    self.eta_defaut[120] = 0

            if self.D12_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[12] = 0
                break
