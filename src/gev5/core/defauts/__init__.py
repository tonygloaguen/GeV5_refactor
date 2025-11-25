"""
Gestion des défauts (12 voies).

Ce module centralise le démarrage des 12 threads Defaut_X,
en reprenant la logique de GeV5_Moteur / starter.
"""

from ...legacy import (
    defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6,
    defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12,
)
from ...utils.config import SystemConfig


def start_defauts(cfg: SystemConfig) -> None:
    """Démarre les 12 threads de défaut, comme dans le code historique."""

    dlist = [
        (defaut_1.Defaut_1, cfg.D1_ON, "Defaut_1_Thread"),
        (defaut_2.Defaut_2, cfg.D2_ON, "Defaut_2_Thread"),
        (defaut_3.Defaut_3, cfg.D3_ON, "Defaut_3_Thread"),
        (defaut_4.Defaut_4, cfg.D4_ON, "Defaut_4_Thread"),
        (defaut_5.Defaut_5, cfg.D5_ON, "Defaut_5_Thread"),
        (defaut_6.Defaut_6, cfg.D6_ON, "Defaut_6_Thread"),
        (defaut_7.Defaut_7, cfg.D7_ON, "Defaut_7_Thread"),
        (defaut_8.Defaut_8, cfg.D8_ON, "Defaut_8_Thread"),
        (defaut_9.Defaut_9, cfg.D9_ON, "Defaut_9_Thread"),
        (defaut_10.Defaut_10, cfg.D10_ON, "Defaut_10_Thread"),
        (defaut_11.Defaut_11, cfg.D11_ON, "Defaut_11_Thread"),
        (defaut_12.Defaut_12, cfg.D12_ON, "Defaut_12_Thread"),
    ]

    for cls, d_on, name in dlist:
        t = cls(cfg.low, cfg.high, d_on)
        t.setName(name)
        t.start()
