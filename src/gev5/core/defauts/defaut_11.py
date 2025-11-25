import threading
import time
from ..comptage import comptage_11
from ..alarmes import alarme_11

class Defaut_11(threading.Thread):
    # Etat de défaut local à la voie 11
    # 0 = OK, 1 = défaut bas (perte comptage), 2 = défaut haut (parasite) 
    eta_defaut = {11: 0, 110: 0}
    # 0 = pas encore envoyé, 1 = envoyé
    email_send_defaut = {11: 0}

    def __init__(self, limite_inferieure, limite_superieure, D11_ON):
        threading.Thread.__init__(self)
        self.valeur = None
        self.limite_inferieure = limite_inferieure
        self.limite_superieure = limite_superieure
        self.D11_ON = D11_ON

    def run(self):
        while True:
            if self.D11_ON == 1:
                # Scrutation toutes les 60 s
                time.sleep(60)
                # On lit UNIQUEMENT la voie 11
                self.valeur = comptage_11.Frequence_11_Thread.compteur[110]

                # Défaut bas : typique déconnexion détecteur
                if self.valeur < self.limite_inferieure:
                    self.eta_defaut[11] = 1
                    self.eta_defaut[110] = self.valeur
                    if self.email_send_defaut[11] == 0:
                        self.email_send_defaut[11] = 1

                # Défaut haut : pic anormal, mais on ne lève pas si une alarme vraie est en cours sur cette voie
                elif self.valeur > self.limite_superieure and alarme_11.Alarme11.alarme_resultat[11] == 0:
                    self.eta_defaut[11] = 2
                    self.eta_defaut[110] = self.valeur
                    if self.email_send_defaut[11] == 0:
                        self.email_send_defaut[11] = 1

                # Retour à la normale : on remet juste CETTE voie à 0
                else:
                    self.eta_defaut[11] = 0
                    self.email_send_defaut[11] = 0
                    self.eta_defaut[110] = 0

            if self.D11_ON == 0:
                # voie désactivée : on sort
                self.eta_defaut[11] = 0
                break
