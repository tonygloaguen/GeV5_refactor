"""
Starter GeV5 - Orchestration principale (version refactorisée et cohérente
avec SystemConfig, le comptage, les alarmes, les défauts et les courbes).

Hypothèses basées sur la V1 :

- Défauts :
    * seuil bas  défaut  = cfg.low
    * seuil haut défaut  = cfg.high

- Alarmes radiologiques :
    * seuil N1 (alarme)  = cfg.seuil2
    * seuil de retour    ≈ 0.8 * cfg.seuil2  (hystérésis simple)
    * seuil N2 (alarme 2)= calculé dans AlarmeThread via n2_factor (par défaut 1.5)
    * seuil suiveur      = fond * cfg.multiple

- Voies :
    * voies 1..4  : électroniques locales, comptage GPIO (PIN_1..PIN_4)
    * voies 5..8  : électronique esclave 1 (Rem_IP)  → à intégrer plus tard
    * voies 9..12 : électronique esclave 2 (Rem_IP_2)→ à intégrer plus tard
"""

from __future__ import annotations



import threading
from logging import Logger
from typing import Dict, List

from ..utils.config import SystemConfig
from ..utils.logging import get_logger

from ..core.comptage.build import build_all_comptages
from ..core.comptage.comptage import ComptageThread
from ..core.alarmes.build import build_all_alarmes
from ..core.defauts.build import build_all_defauts
from ..core.courbes.build import build_all_courbes

from ..hardware.storage.collect_bdf_v2 import BdfCollectorV2
from ..hardware.storage.db_write_v2 import PassageRecorderV2

logger: Logger = get_logger("gev5.starter")


class Gev5System:
    """Orchestrateur principal GeV5 (voies / alarmes / défauts / courbes)."""

    def __init__(self, cfg: SystemConfig) -> None:
        self.cfg = cfg
        self.threads: List[threading.Thread] = []

        # Références vers les threads par famille
        self.comptage_threads: List[ComptageThread] = []
        self.alarme_threads: List[threading.Thread] = []
        self.defaut_threads: List[threading.Thread] = []
        self.courbe_threads: List[threading.Thread] = []

        self.bdf_thread: threading.Thread | None = None
        self.passage_thread: threading.Thread | None = None


    # ------------------------------------------------------------------ #
    # Helpers de mapping
    # ------------------------------------------------------------------ #
    def _build_pins(self) -> Dict[int, int]:
        """
        Mapping {voie: pin_GPIO}.

        Voies locales (1..4) → PIN_1..PIN_4
        Voies 5..12 → pour l'instant 0 (seront gérées via Rem_IP / eVx
        par d'autres services ; ici on ne crée que le squelette).
        """
        pins: Dict[int, int] = {
            1: self.cfg.pin_1,
            2: self.cfg.pin_2,
            3: self.cfg.pin_3,
            4: self.cfg.pin_4,
        }
        # voies "remote" → placeholder (0)
        for ch in range(5, 13):
            pins[ch] = 0
        return pins

    def _build_d_on_flags(self) -> Dict[int, int]:
        """Mapping {voie: Dn_ON} à partir de SystemConfig."""
        return {
            1: self.cfg.D1_ON,
            2: self.cfg.D2_ON,
            3: self.cfg.D3_ON,
            4: self.cfg.D4_ON,
            5: self.cfg.D5_ON,
            6: self.cfg.D6_ON,
            7: self.cfg.D7_ON,
            8: self.cfg.D8_ON,
            9: self.cfg.D9_ON,
            10: self.cfg.D10_ON,
            11: self.cfg.D11_ON,
            12: self.cfg.D12_ON,
        }

    def _build_passage_flags(self) -> Dict[int, callable]:
        """
        Construit un dict {voie: callable_bool} indiquant si un passage
        est en cours.

        Implémentation basée sur les modules legacy etat_cellule_1 / etat_cellule_2 :

        - InputWatcher.cellules[1] / [2] → 1 si faisceau coupé
        - On considère qu'il y a passage si au moins une des deux cellules est à 1.

        Même logique pour toutes les voies (les cellules pilotent le portique entier).
        """
        # Import local pour éviter les cycles
        from ..hardware import etat_cellule_1, etat_cellule_2  # type: ignore

        def passage_actif() -> bool:
            try:
                c1 = getattr(etat_cellule_1.InputWatcher, "cellules", {}).get(1, 0)
                c2 = getattr(etat_cellule_2.InputWatcher, "cellules", {}).get(2, 0)
                return (c1 == 1) or (c2 == 1)
            except Exception:
                return False

        flags: Dict[int, callable] = {}
        for ch in range(1, 13):
            flags[ch] = passage_actif
        return flags

    # ------------------------------------------------------------------ #
    # Démarrage des familles
    # ------------------------------------------------------------------ #
    def start_comptage(self) -> None:
        """
        Démarre les 12 threads de comptage.

        - voies 1..4 : GPIO réels (PIN_1..PIN_4)
        - voies 5..12: pour l’instant, pins=0 (intégration remote à venir)
        """
        pins = self._build_pins()
        d_on = self._build_d_on_flags()

        self.comptage_threads = build_all_comptages(
            sampling=self.cfg.sample_time,  # même rôle que "sampling" V1
            pins=pins,
            d_on_flags=d_on,
            sim=self.cfg.sim,
        )

        for t in self.comptage_threads:
            t.start()
            self.threads.append(t)

        logger.info("Comptage: %d threads démarrés", len(self.comptage_threads))

    def start_defauts(self) -> None:
        """
        Démarre les défauts génériques.

        Mapping V1 → V2 :
        - limite_inferieure (défaut bas)  = cfg.low
        - limite_superieure (défaut haut) = cfg.high
        - période de test ≈ 60 s (comme Defaut_1 V1)
        """
        d_on_flags = self._build_d_on_flags()

        limites_inf = {i: float(self.cfg.low) for i in range(1, 13)}
        limites_sup = {i: float(self.cfg.high) for i in range(1, 13)}

        # brut = compteur[10,20,...,120] comme dans la V1
        get_raw_vals = {
            i: (lambda i=i: ComptageThread.compteur.get(i * 10, 0.0))
            for i in range(1, 13)
        }

        # D_ON par voie
        get_d_on = {
            i: (lambda i=i: d_on_flags[i])
            for i in range(1, 13)
        }

        self.defaut_threads = build_all_defauts(
            limites_inf=limites_inf,
            limites_sup=limites_sup,
            get_raw_vals=get_raw_vals,
            get_d_on_flags=get_d_on,
            period_s=60.0,  # comme le time.sleep(60) des Defaut_X V1
        )

        for t in self.defaut_threads:
            t.start()
            self.threads.append(t)

        logger.info("Défauts: %d threads démarrés", len(self.defaut_threads))

    def start_alarmes(self) -> None:
        """
        Démarre les alarmes génériques.

        V1 :
        - seuil radiologique = seuil2
        - multiple           = multiple (sert au suiveur)
        - Mode_sans_cellules : 0 = alarme déclenchée seulement pendant passage

        Pour cette V2 générique :
        - seuil_haut (N1) = cfg.seuil2
        - seuil_bas       = 0.8 * cfg.seuil2 (hystérésis simple)
        - tempo_s         = 0 (instantané, on pourra faire évoluer)
        - multiple        = cfg.multiple (seuil suiveur = fond * multiple)
        - get_passage_flags basé sur etat_cellule_1 / 2 si mode_sans_cellules == 0
        """
        d_on_flags = self._build_d_on_flags()

        seuil_n1 = float(self.cfg.seuil2)
        seuils_haut = {i: seuil_n1 for i in range(1, 13)}
        seuils_bas = {i: 0.8 * seuil_n1 for i in range(1, 13)}

        # lecture du comptage filtré : compteur[1..12]
        get_vals = {
            i: (lambda i=i: ComptageThread.compteur.get(i, 0.0))
            for i in range(1, 13)
        }

        # activation par voie : Dn_ON == 1
        enabled_flags = {
            i: (lambda i=i: d_on_flags[i] == 1)
            for i in range(1, 13)
        }

        # Hooks passage (cellules) seulement si on n'est PAS en mode sans cellules
        get_passage_flags = None
        if int(self.cfg.mode_sans_cellules) == 0:
            get_passage_flags = self._build_passage_flags()

        self.alarme_threads = build_all_alarmes(
            seuils_haut=seuils_haut,
            seuils_bas=seuils_bas,
            get_vals=get_vals,
            enabled_flags=enabled_flags,
            period_s=0.1,                    # même rythme que le comptage
            hysteresis=0.0,                  # hystérésis déjà géré via seuil_bas
            tempo_s=0.0,                     # instantané pour l'instant
            multiple=float(self.cfg.multiple),
            mode_sans_cellules=int(self.cfg.mode_sans_cellules),
            get_passage_flags=get_passage_flags,
        )

        for t in self.alarme_threads:
            t.start()
            self.threads.append(t)

        logger.info("Alarmes: %d threads démarrés", len(self.alarme_threads))

    def start_courbes(self) -> None:
        """
        Démarre les courbes génériques.

        On échantillonne 1 valeur / seconde par défaut,
        avec une profondeur de 3600 points (~1h).
        """
        get_vals = {
            i: (lambda i=i: ComptageThread.compteur.get(i, 0.0))
            for i in range(1, 13)
        }

        self.courbe_threads = build_all_courbes(
            get_vals=get_vals,
            max_points=3600,
            period_s=1.0,
        )

        for t in self.courbe_threads:
            t.start()
            self.threads.append(t)

        logger.info("Courbes: %d threads démarrés", len(self.courbe_threads))
    
        def start_bdf_collector(self) -> None:
            """
            Démarre le collecteur V2 du bruit de fond.

            Il lit AlarmeThread.fond[1..12] et écrit dans Bruit_de_fond.db.
            """
            self.bdf_thread = BdfCollectorV2(interval=60)
            self.bdf_thread.start()
            self.threads.append(self.bdf_thread)
            logger.info("BdfCollectorV2 démarré (interval=60s).")

    def start_passage_recorder(self) -> None:
        """
        Démarre l'enregistreur V2 des passages.

        Il détecte les passages via les cellules et logge dans passages_v2.
        """
        self.passage_thread = PassageRecorderV2()
        self.passage_thread.start()
        self.threads.append(self.passage_thread)
        logger.info("PassageRecorderV2 démarré.")


    # ------------------------------------------------------------------ #
    # Démarrage global
    # ------------------------------------------------------------------ #
        def start_all(self) -> None:
            logger.info("Démarrage GeV5 (cœur voies + stockage V2)")

            # Cœur temps réel
            self.start_comptage()
            self.start_defauts()
            self.start_alarmes()
            self.start_courbes()

            # Stockage V2 (fond + passages)
            self.start_bdf_collector()
            self.start_passage_recorder()

            logger.info("Tous les threads GeV5 (voies + stockage V2) sont démarrés.")

