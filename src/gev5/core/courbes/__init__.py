"""
Gestion des courbes (12 voies).

Ce module centralise le démarrage des 12 threads CourbeX,
en reprenant la logique historique du moteur.
"""

from ...legacy import (
    courbe_1, courbe_2, courbe_3, courbe_4, courbe_5, courbe_6,
    courbe_7, courbe_8, courbe_9, courbe_10, courbe_11, courbe_12,
)
from ...utils.config import SystemConfig


def start_courbes(cfg: SystemConfig) -> None:
    """Démarre les 12 threads de courbes, comme dans le code historique."""

    clist = [
        (courbe_1.Courbe1, cfg.D1_ON, "Courbe_1_Thread"),
        (courbe_2.Courbe2, cfg.D2_ON, "Courbe_2_Thread"),
        (courbe_3.Courbe3, cfg.D3_ON, "Courbe_3_Thread"),
        (courbe_4.Courbe4, cfg.D4_ON, "Courbe_4_Thread"),
        (courbe_5.Courbe5, cfg.D5_ON, "Courbe_5_Thread"),
        (courbe_6.Courbe6, cfg.D6_ON, "Courbe_6_Thread"),
        (courbe_7.Courbe7, cfg.D7_ON, "Courbe_7_Thread"),
        (courbe_8.Courbe8, cfg.D8_ON, "Courbe_8_Thread"),
        (courbe_9.Courbe9, cfg.D9_ON, "Courbe_9_Thread"),
        (courbe_10.Courbe10, cfg.D10_ON, "Courbe_10_Thread"),
        (courbe_11.Courbe11, cfg.D11_ON, "Courbe_11_Thread"),
        (courbe_12.Courbe12, cfg.D12_ON, "Courbe_12_Thread"),
    ]

    for cls, d_on, name in clist:
        t = cls(d_on, cfg.mode_sans_cellules)
        t.setName(name)
        t.start()
