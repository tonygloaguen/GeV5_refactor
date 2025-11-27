import threading
import time
import subprocess
import Svr_Unipi
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12

# ===============================
#        PARAMÈTRES
# ===============================
ACK_DI = 5
ACK_ACTIVE_HIGH = True
CELLS_DI = [3, 4]
FREE_RELEASE_MS = 200              # ms
CELLS_BUSY_WHEN = 0
ACK_CONFIRM_TIMEOUT = 15.0

# ===============================
#        ÉTATS INTERNES
# ===============================
_ack_last = 0
_ack_waiting_confirm = False
_ack_confirm_deadline = 0.0
_cells_free_since = None
_cells_src = "unipi"
_cells_snapshot = [0, 0]

_zenity_proc = None

# ===============================
#        HELPERS SAFE
# ===============================
def _safe_read_unipi_input(n, default=0):
    try:
        return int(getattr(Svr_Unipi.Svr_Unipi_rec, f"Inp_{n}")[1])
    except Exception:
        return default

# ===============================
#        LECTURE CELLULES
# ===============================
def _read_cells_states_from_unipi():
    try:
        return [int(getattr(Svr_Unipi.Svr_Unipi_rec, f"Inp_{n}")[1]) for n in CELLS_DI]
    except Exception:
        return [CELLS_BUSY_WHEN for _ in CELLS_DI]

def _read_cells_states_sim_first():
    global _cells_src
    try:
        import simulateur
        app = simulateur.Application
        if hasattr(app, "variable1") and hasattr(app, "variable2"):
            s1 = int(app.variable1[0]); s2 = int(app.variable2[0])
            _cells_src = "sim.variable1/2"
            return [s1, s2]
        if hasattr(app, "acqui"):
            arr = list(app.acqui)
            return [int(arr[n]) if 0 <= n < len(arr) else CELLS_BUSY_WHEN for n in CELLS_DI]
        _cells_src = "unipi"
        return _read_cells_states_from_unipi()
    except Exception:
        _cells_src = "unipi"
        return _read_cells_states_from_unipi()

def _cells_busy(cells_states):
    return any(v == CELLS_BUSY_WHEN for v in cells_states)

def _cells_free_and_stable(now_mono, busy):
    global _cells_free_since
    if not busy:
        if _cells_free_since is None:
            _cells_free_since = now_mono
    else:
        _cells_free_since = None
    if _cells_free_since is None:
        return False
    return (now_mono - _cells_free_since) * 1000.0 >= FREE_RELEASE_MS

# ===============================
#        GESTION ZENITY
# ===============================
def _open_zenity_non_blocking():
    global _zenity_proc
    if _zenity_proc is not None:
        return
    try:
        cmd = [
            "zenity", "--question",
            "--title=Confirmation",
            "--text=Confirmer l'acquittement ?",
            "--timeout=" + str(int(ACK_CONFIRM_TIMEOUT))
        ]
        _zenity_proc = subprocess.Popen(cmd)
    except Exception:
        _zenity_proc = None

def _poll_zenity_and_handle():
    global _zenity_proc
    if _zenity_proc is None:
        return
    try:
        ret = _zenity_proc.poll()
        if ret is None:
            return
        _zenity_proc = None
        if _ack_waiting_confirm:
            if ret == 0:
                _do_confirm_ack("Zenity")
            else:
                _cancel_confirm()
    except Exception:
        _zenity_proc = None

def _cancel_confirm():
    global _ack_waiting_confirm, _zenity_proc
    _ack_waiting_confirm = False
    if _zenity_proc is not None:
        try:
            if _zenity_proc.poll() is None:
                _zenity_proc.terminate()
        except Exception:
            pass
        _zenity_proc = None

def _do_confirm_ack(mode):
    global _ack_waiting_confirm, _zenity_proc
    _ack_waiting_confirm = False
    if _zenity_proc is not None:
        try:
            if _zenity_proc.poll() is None:
                _zenity_proc.terminate()
        except Exception:
            pass
        _zenity_proc = None
    InputWatcher.eta_acq[2] = None
    InputWatcher.eta_acq[1] = 1
    InputWatcher.eta_acq[2] = f"Acquittement confirmé ({mode})"
    print(f"[{mode}] ✅ Acquittement confirmé")

# ===============================
#        THREAD INPUT WATCHER
# ===============================
class InputWatcher(threading.Thread):

    eta_acq = {1: 0, 2: None}

    def __init__(self, sim):
        threading.Thread.__init__(self, name="Acquittement_InputWatcher")
        self.sim = sim

    def _handle_front_ack(self, mode, cells_ok):
        global _ack_waiting_confirm, _ack_confirm_deadline, _cells_snapshot
        if not cells_ok:
            print(f"[{mode}] ⚠️ Cellules non stables, ACK ignoré")
            return
        if not _ack_waiting_confirm:
            _ack_waiting_confirm = True
            _ack_confirm_deadline = time.monotonic() + ACK_CONFIRM_TIMEOUT
            _cells_snapshot = _read_cells_states_sim_first() if self.sim else _read_cells_states_from_unipi()
            print(f"[{mode}] 🟡 Confirmation demandée (double appui ou Zenity)")
            _open_zenity_non_blocking()
        else:
            print(f"[{mode}] 🟢 Confirmation par 2e appui")
            _do_confirm_ack(f"{mode} double appui")

    def _tick_confirm_state(self):
        global _ack_waiting_confirm
        # Zenity
        _poll_zenity_and_handle()
        # Timeout
        if _ack_waiting_confirm and time.monotonic() >= _ack_confirm_deadline:
            print("[ACK] ⏳ Timeout confirmation")
            _cancel_confirm()
        # Si cellules changent pendant attente → annuler
        if _ack_waiting_confirm:
            current = _read_cells_states_sim_first() if self.sim else _read_cells_states_from_unipi()
            if current != _cells_snapshot:
                print("[ACK] ❌ Cellules instables → confirmation annulée")
                _cancel_confirm()

    def run(self):
        global _ack_last, _cells_free_since, _cells_src

        while True:
            try:
                # reset acquittement auto si plus d'alarme
                if all(value == 0 for value in [
                    alarme_1.Alarme1.alarme_resultat[1], alarme_2.Alarme2.alarme_resultat[2],
                    alarme_3.Alarme3.alarme_resultat[3], alarme_4.Alarme4.alarme_resultat[4],
                    alarme_5.Alarme5.alarme_resultat[5], alarme_6.Alarme6.alarme_resultat[6],
                    alarme_7.Alarme7.alarme_resultat[7], alarme_8.Alarme8.alarme_resultat[8],
                    alarme_9.Alarme9.alarme_resultat[9], alarme_10.Alarme10.alarme_resultat[10],
                    alarme_11.Alarme11.alarme_resultat[11], alarme_12.Alarme12.alarme_resultat[12]
                ]):
                    self.eta_acq[1] = 0
                    if self.eta_acq[2] is not None:
                        time.sleep(2)
                        self.eta_acq[2] = None
                    _cancel_confirm()

                # lecture ACK
                if self.sim == 0:
                    ack_raw = _safe_read_unipi_input(ACK_DI)
                    ack_now = ack_raw if ACK_ACTIVE_HIGH else (1 - ack_raw)
                    front_ack = (ack_now == 1 and _ack_last == 0)
                    _ack_last = ack_now
                    cells_states = _read_cells_states_from_unipi()
                    busy = _cells_busy(cells_states)
                    cells_ok = _cells_free_and_stable(time.monotonic(), busy)
                    if front_ack:
                        self._handle_front_ack("DI5", cells_ok)

                if self.sim == 1:
                    import simulateur
                    ack_raw = int(simulateur.Application.acqui[0])
                    ack_now = ack_raw if ACK_ACTIVE_HIGH else (1 - ack_raw)
                    front_ack = (ack_now == 1 and _ack_last == 0)
                    _ack_last = ack_now
                    cells_states = _read_cells_states_sim_first()
                    busy = _cells_busy(cells_states)
                    cells_ok = _cells_free_and_stable(time.monotonic(), busy)
                    if front_ack:
                        self._handle_front_ack("SIM", cells_ok)

                self._tick_confirm_state()
                time.sleep(0.1)

            except Exception as e:
                print(f"[ACK] ERR run(): {e}")
                time.sleep(0.2)
