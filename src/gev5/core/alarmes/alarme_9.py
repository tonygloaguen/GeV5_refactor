# -*- coding: utf-8 -*-
import threading
import time
import etat_cellule_1, etat_cellule_2
import acquittement
import interface

# Canal-specific imports
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import comptage_9
import courbe_9

class Alarme9(threading.Thread):
    # états publics (index principal 9, miroir 90)
    alarme_resultat = {9: 0, 90: 0}
    mesure = {9: 0}
    suiv = {9: 0}
    val_max = {9: 0}
    recal = {9: 0}
    val_deb_mes = {9: 0}
    max_pos = {9: 0}
    pdf_gen = {9: 0}
    email_send_alarm = {9: 0}
    etat_acq_modbus = {9: 0}
    etat_point_chaud = {9: 0}

    somme_det = 0
    suiv_block = 0

    HOT_INHIBIT_S = 5.0

    def __init__(self, multiple, seuil2, D9_ON, Mode_sans_cellules, somme_det, suiv_block):
        threading.Thread.__init__(self)
        self.multiple = multiple
        self.seuil_haut = seuil2
        self.D_ON = D9_ON
        self.mss = Mode_sans_cellules
        try:
            self.somme_det = max(0, int(somme_det))
        except Exception:
            self.somme_det = 0
        self.suiv_block = suiv_block

        self.valeur = 0
        self.suiveur = 0
        self.suiveur_2 = 0
        self.t_suiv = 0
        self.liste = []
        self.liste_defaut = []

        self.last_zero_time = time.time()
        self.waiting_for_stable_one = False

        self._prev_somme_def = 0
        self._hot_inhibit_until = 0.0

    def run(self):
        time.sleep(2)
        while self.D_ON:
            try:
                self.valeur = comptage_9.Frequence_9_Thread.compteur[9]
            except Exception:
                self.valeur = 0

            if self.suiveur == 0 and self.valeur > 0:
                self.suiveur = self.valeur * self.multiple
                self.suiv[9] = self.suiveur

            self.update_defauts()

            # ---- Lecture cellules (1 = libre, 0 = obstrué) ----
            c1 = int(etat_cellule_1.InputWatcher.cellules.get(1, 1))
            c2 = int(etat_cellule_2.InputWatcher.cellules.get(2, 1))
            self.liste = [c1, c2]

            # Lecture acquittement
            try:
                self.acq = int(getattr(acquittement.InputWatcher, 'eta_acq', {1:0}).get(1, 0))
            except Exception:
                self.acq = 0

            # anti-rebond init val_max
            if self.mesure[9] == 0 and not self.waiting_for_stable_one:
                self.last_zero_time = time.time()
                self.waiting_for_stable_one = True
            if self.mesure[9] == 1 and self.waiting_for_stable_one:
                if time.time() - self.last_zero_time >= 1.0:
                    self.val_max[9] = self.valeur
                self.waiting_for_stable_one = False

            if self.should_reset_alarme():
                self.reset_alarm()
                continue

            if self.mesure[9] in [1, 2] and self.valeur > self.val_max[9]:
                self.val_max[9] = int(self.valeur)

            # Escalade N2
            if (self.valeur > self.seuil_haut
                and self.alarme_resultat[9] in (0, 1)
                and self.somme_def == 0):
                self.trigger_alarm_2()

            if self.is_in_valid_range() and self.valeur != 0:
                self.handle_suiv()

            time.sleep(0.1)

    def update_defauts(self):
        self.liste_defaut = [
            defaut_1.Defaut_1.eta_defaut[1], defaut_2.Defaut_2.eta_defaut[2], defaut_3.Defaut_3.eta_defaut[3],
            defaut_4.Defaut_4.eta_defaut[4], defaut_5.Defaut_5.eta_defaut[5], defaut_6.Defaut_6.eta_defaut[6],
            defaut_7.Defaut_7.eta_defaut[7], defaut_8.Defaut_8.eta_defaut[8], defaut_9.Defaut_9.eta_defaut[9],
            defaut_10.Defaut_10.eta_defaut[10], defaut_11.Defaut_11.eta_defaut[11], defaut_12.Defaut_12.eta_defaut[12]
        ]
        self.somme_def = sum(self.liste_defaut)

        if self._prev_somme_def > 0 and self.somme_def == 0:
            self._hot_inhibit_until = time.time() + self.HOT_INHIBIT_S
            self.etat_point_chaud[9] = 0
            if self.valeur > 0:
                self.suiveur = self.suiv[9] = self.valeur * self.multiple
                self.recal[9] = 1
                self.t_suiv = 0

        self._prev_somme_def = self.somme_def

    def _defects_ratio_ok(self):
        return (self.somme_det == 0) or (self.somme_def / max(self.somme_det, 1) <= 0.25)

    def should_reset_alarme(self):
        return (self.acq == 1 or self.etat_acq_modbus[9] == 1) and (self.alarme_resultat[9] in [1, 2])

    def reset_alarm(self):
        self.alarme_resultat[9] = 0
        self.alarme_resultat[90] = 0
        self.t_suiv = 0
        self._alarm_inhibit_until = time.time() + 3.0
        if self.mss == 1:
            self.mesure[9] = 0
            self.pdf_gen[9] = 1
            self.email_send_alarm[9] = 0

    def is_in_valid_range(self):
        try:
            v = getattr(comptage_9.Frequence_9_Thread, 'variance', {})
            if isinstance(v, dict):
                x = v.get(9, 1.0)
            else:
                x = v[9]
        except Exception:
            x = 1.0
        return 0.85 < x < 1.15

    def handle_suiv(self):
        if 0 not in self.liste and self.alarme_resultat[9] == 0:
            self.t_suiv += 1
            if self.t_suiv == 300 or self.suiveur == 0:
                self.update_suiveur()
            self.check_measurement()
        elif 0 in self.liste and self._defects_ratio_ok() and self.acq == 0:
            self.update_suiv_list()

    def update_suiveur(self):
        if self.alarme_resultat[9] != 0:
            return

        if time.time() < self._hot_inhibit_until:
            self.etat_point_chaud[9] = 0
            self.suiveur = self.suiv[9] = self.valeur * self.multiple
            self.t_suiv = 0
            return

        try:
            LD = getattr(comptage_9.Frequence_9_Thread, 'LD', {})
            if isinstance(LD, dict):
                ldv = LD.get(9, 0)
            else:
                ldv = LD[9]
        except Exception:
            ldv = 0

        if ldv < self.valeur and self.suiveur != 0:
            self.etat_point_chaud[9] = 1
            if not self.suiv_block:
                self.suiveur = self.suiv[9] = self.valeur * self.multiple
        else:
            self.etat_point_chaud[9] = 0
            self.suiveur = self.suiv[9] = self.valeur * self.multiple

        self.t_suiv = 0

    def check_measurement(self):
        if self.mesure[9] in [1, 2]:
            self.mesure[9] = 0
            self.recal[9] = 0
            self.pdf_gen[9] = 1
            self.email_send_alarm[9] = 0

    def update_suiv_list(self):
        cellule_active = 0 in self.liste

        if self.alarme_resultat[9] != 0:
            return

        if not cellule_active:
            self.t_suiv += 1
            if self.t_suiv >= 300 or self.suiveur == 0:
                if time.time() < self._hot_inhibit_until:
                    self.etat_point_chaud[9] = 0
                self.suiveur = self.valeur * self.multiple
                self.suiv[9] = self.suiveur
                self.t_suiv = 0
        else:
            self.t_suiv = 0

        if self.val_max[9] < self.valeur:
            self.val_max[9] = int(self.valeur)

        if self.should_start_measurement():
            self.start_measurement()

    def should_start_measurement(self):
        return (0 in self.liste and self._defects_ratio_ok() and self.acq == 0 and self.alarme_resultat[9] == 0)

    def start_measurement(self):
        if self.mesure[9] == 0:
            self.t_t_w = time.time() + 2
            self.mesure[9] = 1
        if self.t_t_w > time.time():
            self.suiveur_2 = self.valeur * self.multiple
        self.val_deb_mes[9] = self.valeur
        self.suiv[9] = self.suiveur
        if self.suiveur_2 < self.suiveur:
            self.recal[9] = 1
            self.suiveur = self.suiveur_2 = self.suiv[9]
        if self.valeur > self.seuil_haut and self.alarme_resultat[9] == 0:
            self.trigger_alarm_2()
        if self.valeur > self.suiveur and self.alarme_resultat[9] == 0:
            self.trigger_alarm()

    def trigger_alarm_2(self):
        if self.mesure.get(9, 0) == 0 or (hasattr(self, 't_t_w') and time.time() < self.t_t_w):
            return
        if self.alarme_resultat.get(9, 0) < 2:
            self.alarme_resultat[9] = 2
        if self.alarme_resultat.get(90, 0) < 2:
            self.alarme_resultat[90] = 2
        self.mesure[9] = 2
        self.email_send_alarm[9] = 1

    def trigger_alarm(self):
        if self.mesure.get(9, 0) == 0 or (hasattr(self, 't_t_w') and time.time() < self.t_t_w):
            return
        if self.alarme_resultat.get(9, 0) < 1:
            self.alarme_resultat[9] = 1
        if self.alarme_resultat.get(90, 0) < 1:
            self.alarme_resultat[90] = 1
        self.mesure[9] = 2
        self.email_send_alarm[9] = 1
