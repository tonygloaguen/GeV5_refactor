"""
Gestion des alarmes (12 voies).

Ce module centralise le démarrage des 12 threads d'alarme,
en reprenant la logique historique du moteur.
"""

from ...legacy import (
    alarme_1, alarme_2, alarme_3, alarme_4,
    alarme_5, alarme_6, alarme_7, alarme_8,
    alarme_9, alarme_10, alarme_11, alarme_12,
)
from ...utils.config import SystemConfig


def start_alarmes(cfg: SystemConfig) -> None:
    """Démarre les 12 threads d'alarmes."""

    # Somme des détecteurs actifs, comme dans le code original
    somme_det = sum([
        cfg.D1_ON, cfg.D2_ON, cfg.D3_ON, cfg.D4_ON,
        cfg.D5_ON, cfg.D6_ON, cfg.D7_ON, cfg.D8_ON,
        cfg.D9_ON, cfg.D10_ON, cfg.D11_ON, cfg.D12_ON,
    ])

    alist = [
        (alarme_1.Alarme1,  cfg.D1_ON,  "Alarme_1_Thread"),
        (alarme_2.Alarme2,  cfg.D2_ON,  "Alarme_2_Thread"),
        (alarme_3.Alarme3,  cfg.D3_ON,  "Alarme_3_Thread"),
        (alarme_4.Alarme4,  cfg.D4_ON,  "Alarme_4_Thread"),
        (alarme_5.Alarme5,  cfg.D5_ON,  "Alarme_5_Thread"),
        (alarme_6.Alarme6,  cfg.D6_ON,  "Alarme_6_Thread"),
        (alarme_7.Alarme7,  cfg.D7_ON,  "Alarme_7_Thread"),
        (alarme_8.Alarme8,  cfg.D8_ON,  "Alarme_8_Thread"),
        (alarme_9.Alarme9,  cfg.D9_ON,  "Alarme_9_Thread"),
        (alarme_10.Alarme10, cfg.D10_ON, "Alarme_10_Thread"),
        (alarme_11.Alarme11, cfg.D11_ON, "Alarme_11_Thread"),
        (alarme_12.Alarme12, cfg.D12_ON, "Alarme_12_Thread"),
    ]

    for cls, d_on, name in alist:
        t = cls(
            cfg.multiple,
            cfg.seuil2,
            d_on,
            cfg.mode_sans_cellules,
            somme_det,
            cfg.suiv_block,
        )
        t.setName(name)
        t.start()
