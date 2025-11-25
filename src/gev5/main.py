# src/gev5/main.py
"""
Point d'entrée principal GeV5 (nouvelle architecture).

Il utilise désormais :
- boot.loader.load_config() pour lire Parametres.db
- boot.starter.Gev5System pour démarrer tous les services
"""

from .boot.loader import load_config
from .boot.starter import Gev5System


def main() -> None:
    cfg = load_config()          # lit Parametres.db → SystemConfig
    system = Gev5System(cfg)     # instancie l’orchestrateur
    system.start_all()           # démarre tout (threads, Flask, etc.)


if __name__ == "__main__":
    main()
