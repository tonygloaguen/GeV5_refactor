# prise_photo.py — ONE-SHOT stable (sans live), UDP, H.264 conseillé
import threading
import subprocess
import time
import datetime
from pathlib import Path

import etat_cellule_1, etat_cellule_2
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import interface


class PrisePhoto(threading.Thread):
    """
    Snapshot RTSP -> JPEG (one-shot) fiable et rapide.
    Déclenchement sur front montant des cellules, si alarmes inactives.
    Expose:
      - PrisePhoto.filename[1]  -> chemin du dernier .jpg
      - PrisePhoto.timestamp[1] -> YYYYMMDD_HHMMSS
      - PrisePhoto.cam_dispo[1] -> 0 durant capture, 1 sinon
    """

    # Etats partagés
    timestamp = {1: 0}
    filename  = {1: None}
    cam_dispo = {1: 1}
    photo_prise = False
    lock = threading.Lock()

    # --- Config ---
    OUT_DIR = Path("/home/pi/Partage/photo")
    FFMPEG  = "ffmpeg"           # ex: "/usr/bin/ffmpeg"

    MAX_W   = 1280               # largeur max (pour lisibilité plaques)
    Q_JPEG  = "4"                # 2..31 (↓ = meilleure qualité). Ajuste si tu veux ~500 Ko
    STIMEOUT_US     = 2_000_000  # 2s handshake RTSP
    CAPTURE_TIMEOUT = 5          # 5s max commande

    # Parsing court & robuste
    PROBESIZE   = "1M"
    ANALYZEDUR  = "200k"

    # Déclenchement
    COOL_DOWN_S = 1.2

    def __init__(self, snapshot_url: str, Mode_sans_cellules: int):
        """
        snapshot_url: lien RTSP complet — idéal: H.264 sub + port 554.
          ex: rtsp://user:pwd@IP:554/h264Preview_01_sub
        """
        super().__init__()
        self.snapshot_url = snapshot_url
        self.mss = Mode_sans_cellules
        self.running = True

        self.OUT_DIR.mkdir(parents=True, exist_ok=True)

        self._last_shot_ts = 0.0
        self._prev_cellules = False
        self._shot_lock = threading.Lock()

    # ------------------ Helpers état process ------------------

    def _cellules_actives(self) -> bool:
        try:
            return (
                etat_cellule_1.InputWatcher.cellules.get(1, 0) == 1 or
                etat_cellule_2.InputWatcher.cellules.get(2, 0) == 1
            )
        except Exception:
            return False

    def _alarmes_inactives(self) -> bool:
        try:
            for i in range(1, 13):
                try:
                    mod = globals()[f"alarme_{i}"]
                    val = getattr(mod, f"Alarme{i}").alarme_resultat.get(i, 1)
                    if val != 0:
                        return False
                except Exception:
                    continue
            return True
        except Exception:
            return True

    # ------------------ Capture ONE-SHOT ------------------

    def _capture_rtsp_frame(self) -> bool:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        final_jpg = self.OUT_DIR / f"photo_{ts}.jpg"

        # Redimensionne + unsharp, keyframe only, UDP pour éviter timeouts
        vf = f"scale='min({self.MAX_W},iw)':-2,unsharp=3:3:0.8"
        cmd = [
            self.FFMPEG,
            "-hide_banner", "-loglevel", "error",
            "-rtsp_transport", "udp",
            "-stimeout", str(self.STIMEOUT_US),
            "-probesize", self.PROBESIZE,
            "-analyzeduration", self.ANALYZEDUR,
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-err_detect", "ignore_err",
            "-skip_frame", "nokey",              # attendre une keyframe propre
            "-use_wallclock_as_timestamps", "1",
            "-y",
            "-i", self.snapshot_url,
            "-frames:v", "1",
            "-vf", vf,
            "-q:v", self.Q_JPEG,
            "-f", "image2",
            str(final_jpg)
        ]

        try:
            subprocess.run(cmd, check=True, timeout=self.CAPTURE_TIMEOUT)
            with self.lock:
                self.timestamp[1] = ts
                self.filename[1]  = str(final_jpg)
            print(f"[{ts}] Snapshot : {final_jpg}")
            self.photo_prise = True
            self._last_shot_ts = time.time()
            return True
        except subprocess.TimeoutExpired:
            print("[FFMPEG_ERR] Timeout capture ffmpeg.")
        except subprocess.CalledProcessError as e:
            print(f"[FFMPEG_ERR] {self.snapshot_url} : {e}")
        except Exception as e:
            print(f"[ERR] Capture RTSP: {e}")

        return False

    def capture_photo(self) -> bool:
        # anti-rafale
        if time.time() - self._last_shot_ts < self.COOL_DOWN_S:
            return False
        return self._capture_rtsp_frame()

    # ------------------ Thread loop ------------------

    def run(self):
        try:
            while self.running:
                try:
                    cells_now = self._cellules_actives()
                    alarmes_ok = self._alarmes_inactives()

                    # front montant
                    rising_edge = (not self._prev_cellules) and cells_now
                    self._prev_cellules = cells_now

                    if rising_edge and alarmes_ok:
                        print("Condition remplie, snapshot RTSP en cours...")
                        with self._shot_lock:
                            with self.lock:
                                self.cam_dispo[1] = 0
                            try:
                                if self.mss == 0:
                                    self.capture_photo()
                            finally:
                                with self.lock:
                                    self.cam_dispo[1] = 1

                    if not cells_now:
                        self.photo_prise = False

                    time.sleep(0.10)

                except Exception as e:
                    print(f"[THREAD_ERR] {e}")
                    time.sleep(0.25)
        finally:
            pass

    def stop(self):
        self.running = False
