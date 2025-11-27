import threading
import time
import etat_cellule_1, etat_cellule_2
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6
import alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12


class ListWatcher(threading.Thread):
    vitesse = {1: "Vitesse N.A.", 10: "Pas de détection de sens"}

    def __init__(self, distance_cellules, Mode_sans_cellules):
        threading.Thread.__init__(self)
        self.distance_cellules = distance_cellules
        self.mss = Mode_sans_cellules
        self.time_cellule1 = None
        self.time_cellule2 = None
        self.last_cellule1 = 0
        self.last_cellule2 = 0
        self.derniere_mesure = 0

    def calculer_vitesse(self):
        t1 = self.time_cellule1
        t2 = self.time_cellule2
        diff_time = abs(t2 - t1)
        if diff_time == 0:
            return "Vitesse N.A."
        vitesse_m_s = self.distance_cellules / diff_time
        vitesse_kmh = vitesse_m_s * 3.6
        return "Defaut vitesse" if vitesse_kmh > 10 else round(vitesse_kmh, 1)

    def get_alarm_list(self):
        raw = [
            alarme_1.Alarme1.mesure[1], alarme_2.Alarme2.mesure[2], alarme_3.Alarme3.mesure[3],
            alarme_4.Alarme4.mesure[4], alarme_5.Alarme5.mesure[5], alarme_6.Alarme6.mesure[6],
            alarme_7.Alarme7.mesure[7], alarme_8.Alarme8.mesure[8], alarme_9.Alarme9.mesure[9],
            alarme_10.Alarme10.mesure[10], alarme_11.Alarme11.mesure[11], alarme_12.Alarme12.mesure[12]
        ]
        return [val for val in raw if isinstance(val, int)]

    def run(self):
        while True:
            if self.mss == 1:
                self.vitesse[1] = "Vitesse N.A."
                break

            c1 = etat_cellule_1.InputWatcher.cellules[1]
            c2 = etat_cellule_2.InputWatcher.cellules[2]
            now = time.perf_counter()

            # Détection front montant cellule 1
            if c1 == 1 and self.last_cellule1 == 0 and not self.time_cellule1:
                self.time_cellule1 = now

            # Détection front montant cellule 2
            if c2 == 1 and self.last_cellule2 == 0 and not self.time_cellule2:
                self.time_cellule2 = now

            # Mise à jour états précédents
            self.last_cellule1 = c1
            self.last_cellule2 = c2

            # Cas de mesure de passage (2 fronts captés)
            if self.time_cellule1 and self.time_cellule2:
                delta = abs(self.time_cellule1 - self.time_cellule2)

                # Trop court = probablement rebond
                if delta < 0.03:
                    self.time_cellule1 = self.time_cellule2 = None
                    continue

                # Si alarme active, on ignore
                if any(val == 2 for val in self.get_alarm_list()):
                    self.time_cellule1 = self.time_cellule2 = None
                    continue

                # Détection du sens
                if self.time_cellule1 < self.time_cellule2:
                    sens = "1 -> 2"
                else:
                    sens = "2 -> 1"

                self.vitesse[10] = sens
                self.vitesse[1] = self.calculer_vitesse()
                self.derniere_mesure = now

                self.time_cellule1 = None
                self.time_cellule2 = None
                # time.sleep(1)

            # Cellule 1 seule active trop longtemps
            elif self.time_cellule1 and not self.time_cellule2:
                if now - self.time_cellule1 > 5 and self.time_cellule1 > self.derniere_mesure:
                    self.vitesse[1] = "Pas de vitesse mesurée"
                    self.vitesse[10] = "Pas de détection de sens"
                    self.time_cellule1 = None

            # Cellule 2 seule active trop longtemps
            elif self.time_cellule2 and not self.time_cellule1:
                if now - self.time_cellule2 > 5 and self.time_cellule2 > self.derniere_mesure:
                    self.vitesse[1] = "Pas de vitesse mesurée"
                    self.vitesse[10] = "Pas de détection de sens"
                    self.time_cellule2 = None

            time.sleep(0.01)
