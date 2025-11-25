# -*- coding: utf-8 -*-
import threading
import time
import comptage_1
import etat_cellule_1, etat_cellule_2
import acquittement
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import interface
import courbe_1

class Alarme1(threading.Thread):
    # états publics (index principal 1, miroir 10)
    alarme_resultat = {1: 0, 10: 0}
    mesure = {1: 0}
    suiv = {1: 0}
    val_max = {1: 0}
    recal = {1: 0}
    val_deb_mes = {1: 0}
    max_pos = {1: 0}
    pdf_gen = {1: 0}
    email_send_alarm = {1: 0}
    etat_acq_modbus = {1: 0}
    etat_point_chaud = {1: 0}
    etat_passage = {1: 0}       # <<< 0=pas de passage (VERT), 1=passage (BLEU)

    somme_det = 0
    suiv_block = 0

    HOT_INHIBIT_S = 5.0

    def __init__(self, multiple, seuil2, D1_ON, Mode_sans_cellules, somme_det, suiv_block):
        threading.Thread.__init__(self)
        self.multiple = multiple
        self.seuil_haut = seuil2
        self.D1_ON = D1_ON
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

        self._deb_latched = False   # <<< latch du début de mesure

    # ──────────────────────────────────────────────────────────────────────────
    def run(self):
        time.sleep(2)
        while self.D1_ON:
            self.valeur = comptage_1.Frequence_1_Thread.compteur[1]

            # init suiveur au besoin
            if self.suiveur == 0 and self.valeur > 0:
                self.suiveur = self.valeur * self.multiple
                self.suiv[1] = self.suiveur

            self.update_defauts()

            # ---- Lecture cellules (1 = libre, 0 = obstrué) ----
            c1 = int(etat_cellule_1.InputWatcher.cellules.get(1, 1))
            c2 = int(etat_cellule_2.InputWatcher.cellules.get(2, 1))
            self.liste = [c1, c2]
            self.etat_passage[1] = 1 if 0 in self.liste else 0   # <<< utilisé par l'UI

            # Lecture acquittement (sécurisée)
            try:
                self.acq = int(getattr(acquittement.InputWatcher, 'eta_acq', {1:0}).get(1, 0))
            except Exception:
                self.acq = 0

            # anti-rebond init val_max
            if self.mesure[1] == 0 and not self.waiting_for_stable_one:
                self.last_zero_time = time.time()
                self.waiting_for_stable_one = True
            if self.mesure[1] == 1 and self.waiting_for_stable_one:
                if time.time() - self.last_zero_time >= 1.0:
                    self.val_max[1] = self.valeur
                self.waiting_for_stable_one = False

            if self.should_reset_alarme():
                self.reset_alarm()
                continue

            if self.mesure[1] in [1, 2] and self.valeur > self.val_max[1]:
                self.val_max[1] = int(self.valeur)

            # Escalade N2
            if (self.valeur > self.seuil_haut
                and self.alarme_resultat[1] in (0, 1)
                and self.somme_def == 0):
                self.trigger_alarm_2()

            if self.is_in_valid_range() and self.valeur != 0:
                self.handle_suiv()

            time.sleep(0.1)

    # ──────────────────────────────────────────────────────────────────────────
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
            self.etat_point_chaud[1] = 0
            if self.valeur > 0:
                self.suiveur = self.suiv[1] = self.valeur * self.multiple
                self.recal[1] = 1
                self.t_suiv = 0

        self._prev_somme_def = self.somme_def

    def _defects_ratio_ok(self):
        return (self.somme_det == 0) or (self.somme_def / max(self.somme_det, 1) <= 0.25)

    # ──────────────────────────────────────────────────────────────────────────
    def should_reset_alarme(self):
        return (self.acq == 1 or self.etat_acq_modbus[1] == 1) and (self.alarme_resultat[1] in [1, 2])

    def reset_alarm(self):
        self.alarme_resultat[1] = 0
        self.alarme_resultat[10] = 0
        self.t_suiv = 0
        self._alarm_inhibit_until = time.time() + 3.0
        self._deb_latched = False      # <<< reset latch
        if self.mss == 1:
            self.mesure[1] = 0
            self.pdf_gen[1] = 1
            self.email_send_alarm[1] = 0

    def is_in_valid_range(self):
        return 0.85 < comptage_1.Frequence_1_Thread.variance.get(1, 1.0) < 1.15

    # ──────────────────────────────────────────────────────────────────────────
    def handle_suiv(self):
        if 0 not in self.liste and self.alarme_resultat[1] == 0:
            self.t_suiv += 1
            if self.t_suiv == 300 or self.suiveur == 0:
                self.update_suiveur()
            self.check_measurement()
        elif 0 in self.liste and self._defects_ratio_ok() and self.acq == 0:  # <<< aligné sur Alarme2
            self.update_suiv_list()

    def update_suiveur(self):
        if self.alarme_resultat[1] != 0:
            return

        if time.time() < self._hot_inhibit_until:
            self.etat_point_chaud[1] = 0
            self.suiveur = self.suiv[1] = self.valeur * self.multiple
            self.t_suiv = 0
            return

        if comptage_1.Frequence_1_Thread.LD[1] < self.valeur and self.suiveur != 0:
            self.etat_point_chaud[1] = 1
            if not self.suiv_block:
                self.suiveur = self.suiv[1] = self.valeur * self.multiple
        else:
            self.etat_point_chaud[1] = 0
            self.suiveur = self.suiv[1] = self.valeur * self.multiple

        self.t_suiv = 0

    def check_measurement(self):
        if self.mesure[1] in [1, 2]:
            self.mesure[1] = 0
            self._deb_latched = False     # <<< reset latch fin de mesure
            self.recal[1] = 0
            self.pdf_gen[1] = 1
            self.email_send_alarm[1] = 0

    def update_suiv_list(self):
        cellule_active = 0 in self.liste

        if self.alarme_resultat[1] != 0:
            return

        if not cellule_active:
            self.t_suiv += 1
            if self.t_suiv >= 300 or self.suiveur == 0:
                if time.time() < self._hot_inhibit_until:
                    self.etat_point_chaud[1] = 0
                self.suiveur = self.valeur * self.multiple
                self.suiv[1] = self.suiveur
                self.t_suiv = 0
        else:
            self.t_suiv = 0

        if self.val_max[1] < self.valeur:
            self.val_max[1] = int(self.valeur)

        if self.should_start_measurement():
            self.start_measurement()

    def should_start_measurement(self):
        # <<< aligné sur Alarme2 : départ quand cellule active, ratio défaut OK, pas d'acquittement en cours, pas d'alarme
        return (0 in self.liste and self._defects_ratio_ok() and self.acq == 0 and self.alarme_resultat[1] == 0)

    def start_measurement(self):
        # Armement + début de mesure
        if self.mesure[1] == 0:
            self.t_t_w = time.time() + 2
            self.mesure[1] = 1
            self._deb_latched = False   # <<< (ré)arme le latch

        if self.t_t_w > time.time():
            self.suiveur_2 = self.valeur * self.multiple

        # LATCH : ne fixe val_deb_mes qu'une seule fois, sur la 1ère valeur non nulle
        if not self._deb_latched and self.valeur > 0:
            self.val_deb_mes[1] = int(self.valeur)
            self._deb_latched = True    # <<< évite bdf1=0

        self.suiv[1] = self.suiveur
        if self.suiveur_2 < self.suiveur:
            self.recal[1] = 1
            self.suiveur = self.suiveur_2 = self.suiv[1]

        if self.valeur > self.seuil_haut and self.alarme_resultat[1] == 0:
            self.trigger_alarm_2()
        if self.valeur > self.suiveur and self.alarme_resultat[1] == 0:
            self.trigger_alarm()

    def trigger_alarm_2(self):
        if self.mesure.get(1, 0) == 0 or (hasattr(self, 't_t_w') and time.time() < self.t_t_w):
            return
        if self.alarme_resultat.get(1, 0) < 2:
            self.alarme_resultat[1] = 2
        if self.alarme_resultat.get(10, 0) < 2:
            self.alarme_resultat[10] = 2
        self.mesure[1] = 2
        self.email_send_alarm[1] = 1

    def trigger_alarm(self):
        if self.mesure.get(1, 0) == 0 or (hasattr(self, 't_t_w') and time.time() < self.t_t_w):
            return
        if self.alarme_resultat.get(1, 0) < 1:
            self.alarme_resultat[1] = 1
        if self.alarme_resultat.get(10, 0) < 1:
            self.alarme_resultat[10] = 1
        self.mesure[1] = 2
        self.email_send_alarm[1] = 1
