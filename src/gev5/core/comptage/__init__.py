"""
Gestion des 12 voies de comptage.

Ce module centralise le démarrage des 12 threads de comptage,
en reprenant la logique historique (GeV5_Moteur / starter).
"""

from ...legacy import (
    comptage_1, comptage_2, comptage_3, comptage_4,
    comptage_5, comptage_6, comptage_7, comptage_8,
    comptage_9, comptage_10, comptage_11, comptage_12,
)
from ...utils.config import SystemConfig


def start_comptage(cfg: SystemConfig) -> None:
    """Démarre les 12 threads de comptage."""

    # 1 à 4 : GPIO (pins physiques)
    t1 = comptage_1.Frequence_1_Thread(cfg.sample_time, cfg.D1_ON, cfg.pin_1, cfg.sim)
    t1.setName("Comptage_1_Thread")
    t1.start()

    t2 = comptage_2.Frequence_2_Thread(cfg.sample_time, cfg.D2_ON, cfg.pin_2, cfg.sim)
    t2.setName("Comptage_2_Thread")
    t2.start()

    t3 = comptage_3.Frequence_3_Thread(cfg.sample_time, cfg.D3_ON, cfg.pin_3, cfg.sim)
    t3.setName("Comptage_3_Thread")
    t3.start()

    t4 = comptage_4.Frequence_4_Thread(cfg.sample_time, cfg.D4_ON, cfg.pin_4, cfg.sim)
    t4.setName("Comptage_4_Thread")
    t4.start()

    # 5 à 8 : EVOK / base_url
    t5 = comptage_5.Frequence_5_Thread(cfg.sample_time, cfg.D5_ON, cfg.base_url, cfg.sim)
    t5.setName("Comptage_5_Thread")
    t5.start()

    t6 = comptage_6.Frequence_6_Thread(cfg.sample_time, cfg.D6_ON, cfg.base_url, cfg.sim)
    t6.setName("Comptage_6_Thread")
    t6.start()

    t7 = comptage_7.Frequence_7_Thread(cfg.sample_time, cfg.D7_ON, cfg.base_url, cfg.sim)
    t7.setName("Comptage_7_Thread")
    t7.start()

    t8 = comptage_8.Frequence_8_Thread(cfg.sample_time, cfg.D8_ON, cfg.base_url, cfg.sim)
    t8.setName("Comptage_8_Thread")
    t8.start()

    # 9 à 12 : deuxième hub EVOK / base_url_2
    t9 = comptage_9.Frequence_9_Thread(cfg.sample_time, cfg.D9_ON, cfg.base_url_2, cfg.sim)
    t9.setName("Comptage_9_Thread")
    t9.start()

    t10 = comptage_10.Frequence_10_Thread(cfg.sample_time, cfg.D10_ON, cfg.base_url_2, cfg.sim)
    t10.setName("Comptage_10_Thread")
    t10.start()

    t11 = comptage_11.Frequence_11_Thread(cfg.sample_time, cfg.D11_ON, cfg.base_url_2, cfg.sim)
    t11.setName("Comptage_11_Thread")
    t11.start()

    t12 = comptage_12.Frequence_12_Thread(cfg.sample_time, cfg.D12_ON, cfg.base_url_2, cfg.sim)
    t12.setName("Comptage_12_Thread")
    t12.start()
