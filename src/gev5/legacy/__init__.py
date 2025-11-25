"""Code historique non refactorisé.

Tous les anciens modules .py sont ici pour compatibilité.
"""
import sys, pathlib
# On ajoute ce dossier au sys.path pour que les imports legacy (import comptage_1, ...) continuent de fonctionner.
THIS_DIR = pathlib.Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))
