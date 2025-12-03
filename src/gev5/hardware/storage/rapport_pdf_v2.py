# src/gev5/hardware/storage/rapport_pdf_v2.py
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from ...utils.paths import (
    GEV5_DB_PATH,
    BRUIT_FOND_DB_PATH,
    RAPPORTS_DIR,
    ensure_partage_structure,
)


# ---------------------------------------------------------------------------
# Helpers BDD
# ---------------------------------------------------------------------------

def _fetch_last_passage(db_path: str, passage_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Récupère un enregistrement de passages_v2.

    - si passage_id est None -> dernier passage
    - sinon -> passage avec cet id
    """
    if not os.path.exists(db_path):
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        if passage_id is None:
            cur.execute("SELECT * FROM passages_v2 ORDER BY id DESC LIMIT 1")
        else:
            cur.execute("SELECT * FROM passages_v2 WHERE id = ?", (passage_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        conn.close()


def _fetch_bdf_stats(limit: int = 50) -> Optional[Dict[int, Dict[str, float]]]:
    """
    Récupère des statistiques de bruit de fond récentes depuis bdf_history
    (moyenne / min / max) sur un certain nombre de lignes.

    Retourne:
        {voie: {"avg": x, "min": y, "max": z}, ...}
    ou None si la base n'existe pas ou est vide.
    """
    db_path = str(BRUIT_FOND_DB_PATH)
    if not os.path.exists(db_path):
        return None

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM bdf_history ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        if not rows:
            return None

        stats: Dict[int, Dict[str, float]] = {}
        # indices colonnes : 0=timestamp, 1..12 = bdf1..12
        for voie in range(1, 13):
            values: List[float] = []
            idx = voie  # colonne : bdfN
            for r in rows:
                try:
                    v = float(r[idx])
                    values.append(v)
                except Exception:
                    continue
            if not values:
                stats[voie] = {"avg": 0.0, "min": 0.0, "max": 0.0}
            else:
                stats[voie] = {
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }
        return stats
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Génération PDF
# ---------------------------------------------------------------------------

def _build_pdf_filename(passage: Dict[str, Any]) -> Path:
    """
    Construit un nom de fichier PDF à partir du passage.
    """
    ts_start_str = passage.get("ts_start", "unknown")
    try:
        ts_start = datetime.strptime(ts_start_str, "%Y-%m-%d %H:%M:%S")
        base = ts_start.strftime("Rapport_%Y%m%d_%H%M%S")
    except Exception:
        base = "Rapport_unk"

    pid = passage.get("id")
    if pid is not None:
        base += f"_id{pid}"

    filename = base + ".pdf"
    return RAPPORTS_DIR / filename


def generate_rapport_pdf_v2(passage_id: Optional[int] = None) -> Optional[Path]:
    """
    Génère un rapport PDF basé sur :
      - un enregistrement de passages_v2 dans Db_GeV5.db
      - les stats récentes de bdf_history dans Bruit_de_fond.db

    Args:
        passage_id: id explicite du passage.
                    Si None -> utilise le dernier passage.

    Returns:
        Path du PDF généré, ou None si aucun passage trouvé.
    """
    ensure_partage_structure()

    db_path = str(GEV5_DB_PATH)
    passage = _fetch_last_passage(db_path, passage_id=passage_id)
    if passage is None:
        print("[rapport_pdf_v2] Aucun passage trouvé dans passages_v2.")
        return None

    bdf_stats = _fetch_bdf_stats(limit=50)

    # Création dossier rapports
    RAPPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = _build_pdf_filename(passage)

    # Création du canvas
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    # Marges
    margin_left = 20 * mm
    margin_top = 20 * mm

    # ------------------------------------------------------------------ #
    # En-tête
    # ------------------------------------------------------------------ #
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_left, height - margin_top, "Rapport de passage - GeV5 V2")

    c.setFont("Helvetica", 10)
    ts_start = passage.get("ts_start", "")
    ts_end = passage.get("ts_end", "")
    duration_s = passage.get("duration_s", 0.0)
    comment = passage.get("comment", "")
    vitesse = passage.get("vitesse", 0.0)

    y = height - margin_top - 15

    c.drawString(margin_left, y, f"Début de passage : {ts_start}")
    y -= 12
    c.drawString(margin_left, y, f"Fin de passage   : {ts_end}")
    y -= 12
    c.drawString(margin_left, y, f"Durée (s)        : {duration_s:.2f}")
    y -= 12
    c.drawString(margin_left, y, f"Vitesse          : {vitesse:.2f}")
    y -= 12
    c.drawString(margin_left, y, f"Commentaire      : {comment}")
    y -= 20

    # ------------------------------------------------------------------ #
    # Tableau par voie : bruit de fond & max & états
    # ------------------------------------------------------------------ #
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "Synthèse par voie")
    y -= 14

    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_left, y, "Voie")
    c.drawString(margin_left + 30 * mm, y, "BDF début")
    c.drawString(margin_left + 60 * mm, y, "Max passage")
    c.drawString(margin_left + 95 * mm, y, "Alarme")
    c.drawString(margin_left + 115 * mm, y, "Défaut")
    if bdf_stats is not None:
        c.drawString(margin_left + 135 * mm, y, "BDF moy. (N derniers)")
    y -= 10
    c.setFont("Helvetica", 9)

    for voie in range(1, 13):
        if y < 40 * mm:
            # nouvelle page si plus de place
            c.showPage()
            width, height = A4
            y = height - margin_top

            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin_left, y, "Synthèse par voie (suite)")
            y -= 14
            c.setFont("Helvetica-Bold", 9)
            c.drawString(margin_left, y, "Voie")
            c.drawString(margin_left + 30 * mm, y, "BDF début")
            c.drawString(margin_left + 60 * mm, y, "Max passage")
            c.drawString(margin_left + 95 * mm, y, "Alarme")
            c.drawString(margin_left + 115 * mm, y, "Défaut")
            if bdf_stats is not None:
                c.drawString(margin_left + 135 * mm, y, "BDF moy. (N derniers)")
            y -= 10
            c.setFont("Helvetica", 9)

        # Noms de colonnes dans passages_v2 :
        bdf_col = "bdf%d" % voie
        max_col = "max%d" % voie
        alarm_col = "alarm%d" % voie
        defaut_col = "defaut%d" % voie

        bdf_val = float(passage.get(bdf_col, 0.0))
        max_val = float(passage.get(max_col, 0.0))
        alarm_val = int(passage.get(alarm_col, 0))
        defaut_val = int(passage.get(defaut_col, 0))

        c.drawString(margin_left, y, f"{voie}")
        c.drawRightString(margin_left + 55 * mm, y, f"{bdf_val:.1f}")
        c.drawRightString(margin_left + 90 * mm, y, f"{max_val:.1f}")
        c.drawRightString(margin_left + 110 * mm, y, f"{alarm_val}")
        c.drawRightString(margin_left + 130 * mm, y, f"{defaut_val}")

        if bdf_stats is not None:
            stats = bdf_stats.get(voie, {"avg": 0.0})
            c.drawRightString(margin_left + 170 * mm, y, f"{stats['avg']:.1f}")

        y -= 10

    # ------------------------------------------------------------------ #
    # Résumé global BDF récent
    # ------------------------------------------------------------------ #
    if bdf_stats is not None:
        if y < 60 * mm:
            c.showPage()
            width, height = A4
            y = height - margin_top

        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left, y, "Statistiques récentes de bruit de fond")
        y -= 14

        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin_left, y, "Voie")
        c.drawString(margin_left + 30 * mm, y, "BDF moy.")
        c.drawString(margin_left + 60 * mm, y, "BDF min.")
        c.drawString(margin_left + 90 * mm, y, "BDF max.")
        y -= 10
        c.setFont("Helvetica", 9)

        for voie in range(1, 13):
            stats = bdf_stats.get(voie, {"avg": 0.0, "min": 0.0, "max": 0.0})
            c.drawString(margin_left, y, f"{voie}")
            c.drawRightString(margin_left + 55 * mm, y, f"{stats['avg']:.1f}")
            c.drawRightString(margin_left + 85 * mm, y, f"{stats['min']:.1f}")
            c.drawRightString(margin_left + 115 * mm, y, f"{stats['max']:.1f}")
            y -= 10
            if y < 40 * mm:
                c.showPage()
                width, height = A4
                y = height - margin_top
                c.setFont("Helvetica", 9)

    # ------------------------------------------------------------------ #
    # Finalisation
    # ------------------------------------------------------------------ #
    c.showPage()
    c.save()

    print(f"[rapport_pdf_v2] Rapport généré : {pdf_path}")
    return pdf_path
