from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class DefautConfig:
    """Config d'un défaut voie.

    - channel_id : n° de voie (1..12)
    - raw_key    : clé "brute" utilisée dans les dicts (10, 20, ..., 120)
    - limite_inferieure / limite_superieure : bornes défaut bas / haut
    - period_s   : période de test
    """
    channel_id: int
    raw_key: int
    limite_inferieure: float
    limite_superieure: float
    period_s: float = 0.5


class DefautThread(threading.Thread):
    """
    Thread générique de défaut pour une voie.

    Reprend la logique Defaut_1 / Defaut_2 :
    - 0 = OK
    - 1 = défaut bas (perte comptage)
    - 2 = défaut haut (parasite)
    - email_send_defaut : flag → 1 sur front montant de défaut
    """

    # États partagés (comme dans ta V1)
    eta_defaut: Dict[int, int] = {}
    email_send_defaut: Dict[int, int] = {}

    def __init__(
        self,
        cfg: DefautConfig,
        get_val: Callable[[], float],
        get_d_on: Callable[[], int],
    ) -> None:
        super().__init__(name=f"Defaut_{cfg.channel_id}")
        self.cfg = cfg
        self._get_val = get_val        # ex: lambda: ComptageThread.compteur[raw_key]
        self._get_d_on = get_d_on      # ex: lambda: cfg.D1_ON
        self.valeur: float | None = None

        # init des dicts partagés
        self.eta_defaut.setdefault(self.cfg.channel_id, 0)
        self.eta_defaut.setdefault(self.cfg.raw_key, 0)
        self.email_send_defaut.setdefault(self.cfg.channel_id, 0)

    # ──────────────────────────────────────────────────────────────
    # Boucle principale
    # ──────────────────────────────────────────────────────────────
    def run(self) -> None:
        while True:
            # Si la voie est coupée → on reset et on sort
            if self._get_d_on() == 0:
                self.eta_defaut[self.cfg.channel_id] = 0
                self.eta_defaut[self.cfg.raw_key] = 0
                self.email_send_defaut[self.cfg.channel_id] = 0
                continue

            time.sleep(self.cfg.period_s)

            # lecture valeur brute (comptage brut)
            val = float(self._get_val())
            self.valeur = val

            # calcul état défaut
            if val < self.cfg.limite_inferieure:
                new_state = 1  # défaut bas
            elif val > self.cfg.limite_superieure:
                new_state = 2  # défaut haut
            else:
                new_state = 0  # OK

            old_state = self.eta_defaut[self.cfg.channel_id]

            if new_state != 0:
                # on enregistre le défaut pour la voie + valeur brute
                self.eta_defaut[self.cfg.channel_id] = new_state
                self.eta_defaut[self.cfg.raw_key] = val

                # front montant → lever le flag mail
                if old_state == 0 and self.email_send_defaut[self.cfg.channel_id] == 0:
                    self.email_send_defaut[self.cfg.channel_id] = 1

            else:
                # retour à la normale pour CETTE voie
                self.eta_defaut[self.cfg.channel_id] = 0
                self.eta_defaut[self.cfg.raw_key] = 0
                self.email_send_defaut[self.cfg.channel_id] = 0
