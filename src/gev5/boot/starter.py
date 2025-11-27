"""
Starter GeV5 - Orchestration principale
Démarre tous les services du portique.
Reprise de la logique GeV5_Moteur.py avec la nouvelle structure en packages.
"""

from __future__ import annotations

import subprocess
import threading
from logging import Logger
from typing import List, Optional

# ── Configuration et logging ──────────────────────────────────────────────────
from src.gev5.utils.config import SystemConfig
from src.gev5.utils.logging import get_logger

logger: Logger = get_logger("gev5.starter")
__all__ = ["Gev5System", "start_all"]

# ── HARDWARE ──────────────────────────────────────────────────────────────────
# Interfaces réseau/bus
try:
    from src.gev5.hardware.Svr_Unipi import Srv_Unipi
except ImportError:
    Srv_Unipi = None
    
try:
    from src.gev5.hardware.modbus_interface import Modbus_Interface
except ImportError:
    Modbus_Interface = None
    
try:
    from src.gev5.hardware.eVx_interface import EVx_Interface
except ImportError:
    EVx_Interface = None
    
try:
    from src.gev5.hardware.Driver_F2C import Driver_F2C
except ImportError:
    Driver_F2C = None

# Périphériques
try:
    from src.gev5.hardware.USB_control import USB_Control
except ImportError:
    USB_Control = None
    
try:
    from src.gev5.hardware.Chkdisk import ChkDisk
except ImportError:
    ChkDisk = None
    
try:
    from src.gev5.hardware.prise_photo import PrisePhoto
except ImportError:
    PrisePhoto = None
    
try:
    from src.gev5.hardware.relais import RelaisManager
except ImportError:
    RelaisManager = None

# Storage
try:
    from src.gev5.hardware.storage.DB_write import DB_Write
except ImportError:
    DB_Write = None
    
try:
    from src.gev5.hardware.storage.collect_bdf import CollectBDF
except ImportError:
    CollectBDF = None
    
try:
    from src.gev5.hardware.storage.rapport_pdf import ReportPDF
except ImportError:
    ReportPDF = None
    
try:
    from src.gev5.hardware.storage.email import EmailSender
except ImportError:
    EmailSender = None

# SMS
try:
    from src.gev5.hardware.modem.envoi_sms import EnvoiSMS
except ImportError:
    EnvoiSMS = None

# Cellules
try:
    from src.gev5.hardware.etat_cellule_1 import EtatCellule1
except ImportError:
    EtatCellule1 = None
    
try:
    from src.gev5.hardware.etat_cellule_2 import EtatCellule2
except ImportError:
    EtatCellule2 = None
    
try:
    from src.gev5.hardware.vitesse_chargement import VitesseChargement
except ImportError:
    VitesseChargement = None

# Watchdog
try:
    from src.gev5.hardware.system.Thread_Watchdog import WatchdogThread
except ImportError:
    WatchdogThread = None

# ── CORE MÉTIER (alarmes, comptage, etc.) ─────────────────────────────────────
# TODO: importer les modules métier quand ils seront disponibles
# from src.gev5.core.alarmes import ...
# from src.gev5.core.comptage import ...
# from src.gev5.core.defauts import ...
# from src.gev5.core.courbes import ...


# ── API ──────────────────────────────────────────────────────────────
try:
    from src.gev5.web.app import run_flask_app
except ImportError:
    run_flask_app = None

# ── Simulation ───────────────────────────────────────────────────────
try:
    from src.gev5.core.simulation.simulateur import Application as SimulationApp
except ImportError:
    SimulationApp = None

# ── Acquittement ─────────────────────────────────────────────────────
try:
    from src.gev5.core.acquittement.acquittement import InputWatcher
except ImportError:
    InputWatcher = None


# ─────────────────────────────────────────────────────
# UTILITAIRES UFW (gestion firewall)
# ─────────────────────────────────────────────────────
def ouvrir_ports(ports: List[int], proto: str = "tcp") -> None:
    """Ouvre les ports spécifiés via UFW."""
    for port in ports:
        try:
            subprocess.run(["sudo", "ufw", "allow", f"{port}/{proto}"], check=False)
            logger.debug("Port %d/%s ouvert", port, proto)
        except Exception as e:
            logger.warning("Impossible d'ouvrir le port %d/%s: %s", port, proto, e)


def fermer_ports(ports: List[int], proto: str = "tcp") -> None:
    """Ferme les ports spécifiés via UFW."""
    for port in ports:
        try:
            subprocess.run(["sudo", "ufw", "deny", f"{port}/{proto}"], check=False)
            logger.debug("Port %d/%s fermé", port, proto)
        except Exception as e:
            logger.warning("Impossible de fermer le port %d/%s: %s", port, proto, e)




# ─────────────────────────────────────────────────────
# CLASSE ORCHESTRATION PRINCIPALE
# ─────────────────────────────────────────────────────
class Gev5System:
    """Orchestration de démarrage de tous les services GeV5."""
    
    def __init__(self, cfg: SystemConfig) -> None:
        self.cfg: SystemConfig = cfg
        self.sim_app: Optional[object] = None
        self.threads: List[threading.Thread] = []

    # ──────────────────────────────────────────────────
    # DÉMARRAGE DES SERVICES INDIVIDUELS
    # ──────────────────────────────────────────────────
    
    def _start_thread(self, thread_class, *args, thread_name: str, **kwargs) -> None:
        """Helper pour démarrer un thread de manière cohérente."""
        if thread_class is None:
            logger.warning("Classe %s non disponible (import échoué)", thread_name)
            return
        
        try:
            t = thread_class(*args, **kwargs)
            t.setName(thread_name)
            t.start()
            self.threads.append(t)
            logger.info("Thread %s démarré", thread_name)
        except Exception as e:
            logger.error("Erreur au démarrage de %s: %s", thread_name, e)

    def start_unipi(self) -> None:
        """Démarre le serveur UniPi."""
        self._start_thread(Srv_Unipi, thread_name="Srv_Unipi")

    def start_modbus(self) -> None:
        """Démarre l'interface Modbus."""
        ouvrir_ports([502, 5200])
        self._start_thread(Modbus_Interface, thread_name="Modbus_Interface")

    def start_evx(self) -> None:
        """Démarre l'interface eVx."""
        ouvrir_ports([9000, 6789])
        self._start_thread(EVx_Interface, thread_name="EVx_Interface")

    def start_f2c(self) -> None:
        """Démarre le driver F2C."""
        self._start_thread(Driver_F2C, thread_name="Driver_F2C")

    def start_relais(self) -> None:
        """Démarre le gestionnaire de relais."""
        self._start_thread(RelaisManager, thread_name="Relais_Manager")

    def start_usb(self) -> None:
        """Démarre le contrôle USB."""
        self._start_thread(USB_Control, thread_name="USB_Control")

    def start_disk(self) -> None:
        """Démarre la vérification disque."""
        self._start_thread(ChkDisk, thread_name="ChkDisk")

    def start_camera(self) -> None:
        """Démarre la capture d'images."""
        if PrisePhoto is None:
            logger.warning("PrisePhoto non disponible")
            return
        
        try:
            t = PrisePhoto(self.cfg.RTSP, self.cfg.mode_sans_cellules)
            t.setName("Camera_PrisePhoto")
            t.start()
            self.threads.append(t)
            logger.info("Thread Camera_PrisePhoto démarré")
        except Exception as e:
            logger.error("Erreur au démarrage de Camera_PrisePhoto: %s", e)

    def start_acquittement(self) -> None:
        """Démarre le module d'acquittement."""
        if InputWatcher is None:
            logger.warning("InputWatcher non disponible")
            return
        
        try:
            t = InputWatcher(self.cfg.sim)
            t.setName("Acquittement")
            t.start()
            self.threads.append(t)
            logger.info("Thread Acquittement démarré")
        except Exception as e:
            logger.error("Erreur au démarrage d'Acquittement: %s", e)

    def start_bdf(self) -> None:
        """Démarre la collection des base de données.fichiers."""
        self._start_thread(CollectBDF, thread_name="CollectBDF")

    def start_db_write(self) -> None:
        """Démarre l'enregistrement en base de données."""
        self._start_thread(DB_Write, thread_name="DB_Write")

    def start_report(self) -> None:
        """Démarre la génération de rapports PDF."""
        if ReportPDF is None:
            logger.warning("ReportPDF non disponible")
            return
        
        try:
            noms_detecteurs = [
                self.cfg.D1_nom, self.cfg.D2_nom, self.cfg.D3_nom,
                self.cfg.D4_nom, self.cfg.D5_nom, self.cfg.D6_nom,
                self.cfg.D7_nom, self.cfg.D8_nom, self.cfg.D9_nom,
                self.cfg.D10_nom, self.cfg.D11_nom, self.cfg.D12_nom,
            ]
            t = ReportPDF(
                self.cfg.nom_portique,
                self.cfg.mode_sans_cellules,
                noms_detecteurs,
                self.cfg.seuil2,
                self.cfg.language
            )
            t.setName("ReportPDF")
            t.start()
            self.threads.append(t)
            logger.info("Thread ReportPDF démarré")
        except Exception as e:
            logger.error("Erreur au démarrage de ReportPDF: %s", e)

    def start_email(self) -> None:
        """Démarre le module d'envoi d'emails."""
        if EmailSender is None:
            logger.warning("EmailSender non disponible")
            return
        
        try:
            t = EmailSender(
                self.cfg.nom_portique,
                self.cfg.smtp_server,
                self.cfg.port,
                self.cfg.login,
                self.cfg.password,
                self.cfg.sender,
                self.cfg.recipients,
            )
            t.setName("EmailSender")
            t.start()
            self.threads.append(t)
            logger.info("Thread EmailSender démarré")
        except Exception as e:
            logger.error("Erreur au démarrage d'EmailSender: %s", e)

    def start_sms(self) -> None:
        """Démarre le module SMS."""
        if EnvoiSMS is None:
            logger.warning("EnvoiSMS non disponible")
            return
        
        try:
            t = EnvoiSMS(self.cfg.nom_portique, self.cfg.SMS)
            t.setName("SMS_Module")
            t.start()
            self.threads.append(t)
            logger.info("Thread SMS_Module démarré")
        except Exception as e:
            logger.error("Erreur au démarrage du SMS: %s", e)

    def start_cellules(self) -> None:
        """Démarre les modules de cellules."""
        cellules = []
        
        if EtatCellule1:
            try:
                c1 = EtatCellule1(self.cfg.sim)
                c1.setName("EtatCellule1")
                cellules.append(c1)
            except Exception as e:
                logger.error("Erreur création EtatCellule1: %s", e)
        
        if EtatCellule2:
            try:
                c2 = EtatCellule2(self.cfg.sim)
                c2.setName("EtatCellule2")
                cellules.append(c2)
            except Exception as e:
                logger.error("Erreur création EtatCellule2: %s", e)
        
        if VitesseChargement:
            try:
                c3 = VitesseChargement(self.cfg.sim)
                c3.setName("VitesseChargement")
                cellules.append(c3)
            except Exception as e:
                logger.error("Erreur création VitesseChargement: %s", e)
        
        for t in cellules:
            t.start()
            self.threads.append(t)
            logger.info("Thread %s démarré", t.name)

    def start_watchdog(self) -> None:
        """Démarre le watchdog système."""
        self._start_thread(WatchdogThread, thread_name="Watchdog_Thread")

    def start_api(self) -> None:
        """Démarre l'API Flask."""
        if run_flask_app is None:
            logger.warning("API Flask non disponible")
            return
        
        try:
            noms_detecteurs = [
                self.cfg.D1_nom, self.cfg.D2_nom, self.cfg.D3_nom,
                self.cfg.D4_nom, self.cfg.D5_nom, self.cfg.D6_nom,
                self.cfg.D7_nom, self.cfg.D8_nom, self.cfg.D9_nom,
                self.cfg.D10_nom, self.cfg.D11_nom, self.cfg.D12_nom,
            ]
            thread = threading.Thread(
                target=run_flask_app,
                args=(
                    *noms_detecteurs,
                    self.cfg.nom_portique,
                    self.cfg.mode_sans_cellules,
                    self.cfg.echeance,
                ),
                daemon=True,
                name="Flask_API"
            )
            thread.start()
            self.threads.append(thread)
            logger.info("Thread Flask_API démarré")
        except Exception as e:
            logger.error("Erreur au démarrage de l'API: %s", e)

    # ──────────────────────────────────────────────────
    # DÉMARRAGE GLOBAL ET ORCHESTRATION
    # ──────────────────────────────────────────────────
    
    def start_all(self) -> None:
        """Lance tous les services du portique."""
        cfg: SystemConfig = self.cfg
        logger.info("╔════════════════════════════════════════════╗")
        logger.info("║    Démarrage GeV5 - %s", cfg.nom_portique)
        logger.info("╚════════════════════════════════════════════╝")

        # Démarrage du simulateur si mode simulation activé
        if cfg.sim == 1:
            if SimulationApp:
                try:
                    self.sim_app = SimulationApp()
                    logger.info("Mode simulation activé")
                except Exception as e:
                    logger.error("Erreur au démarrage du simulateur: %s", e)
            else:
                logger.warning("Simulateur non disponible")

        # Services toujours actifs
        self.start_unipi()
        self.start_cellules()
        self.start_relais()
        self.start_camera()
        self.start_acquittement()
        self.start_db_write()
        self.start_bdf()
        self.start_report()
        self.start_email()
        self.start_api()
        self.start_disk()
        self.start_usb()
        self.start_watchdog()

        # Services conditionnels - Modbus
        if cfg.modbus == 1:
            logger.info("Modbus activé")
            self.start_modbus()
        else:
            fermer_ports([502, 5200])
            logger.info("Modbus désactivé")

        # Services conditionnels - eVx
        if cfg.eVx == 1:
            logger.info("eVx activé")
            self.start_evx()
            self.start_f2c()
        else:
            fermer_ports([9000, 6789])
            logger.info("eVx désactivé")

        # Services conditionnels - SMS
        if cfg.mod_SMS == 1:
            logger.info("SMS activé")
            self.start_sms()

        logger.info("╔════════════════════════════════════════════╗")
        logger.info("║    Tous les threads sont lancés ✓         ║")
        logger.info("╚════════════════════════════════════════════╝")

        # Lance la boucle du simulateur si actif
        if cfg.sim == 1 and self.sim_app:
            try:
                logger.info("Entrée en mode simulation (GUI)")
                self.sim_app.mainloop()
            except Exception as e:
                logger.error("Erreur lors de mainloop simulateur: %s", e)


def start_all(cfg: SystemConfig) -> None:
    """Point d'entrée principal pour démarrer GeV5."""
    system = Gev5System(cfg)
    system.start_all()
