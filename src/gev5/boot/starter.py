# src/gev5/boot/starter.py
"""
Démarrage coordonné de tous les services GeV5.

Ce module reprend la logique de démarrage de legacy/GeV5_Moteur.py,
mais en l'adossant à SystemConfig plutôt qu'à des variables globales.
"""
from ..core.defauts import start_defauts

from ..core.courbes import start_courbes

from ..core.comptage import start_comptage

from ..core.alarmes import start_alarmes

from __future__ import annotations

import subprocess
from typing import List

from ..utils.config import SystemConfig
from ..utils.logging import get_logger

# ── Imports legacy (code historique) ──────────────────────────────────────────
from ..legacy import (
    etat_cellule_1, etat_cellule_2, vitesse_chargement,
    prise_photo,
    alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6,
    alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12,
    acquittement, simulateur,
    DB_write, rapport_pdf, Envoi_email,
    modbus_interface,
    eVx_interface,
    Driver_F2C,
    envoi_sms,
    api_flsk,
    collect_bdf,
    Chkdisk,
    USB_control,
    Check_open_cell,
    relais,
    Svr_Unipi,
    Thread_Watchdog,
)

logger = get_logger("gev5.starter")


# ── Utilitaires réseau (copie de GeV5_Moteur) ────────────────────────────────

def ouvrir_ports(ports: List[int], proto: str = "tcp") -> None:
    for port in ports:
        logger.info("Ouverture du port %s/%s via ufw", port, proto)
        subprocess.run(["sudo", "ufw", "allow", f"{port}/{proto}"])


def fermer_ports(ports: List[int], proto: str = "tcp") -> None:
    for port in ports:
        logger.info("Fermeture du port %s/%s via ufw", port, proto)
        subprocess.run(["sudo", "ufw", "deny", f"{port}/{proto}"])


def is_ip_reachable(ip: str) -> bool:
    """
    Vérifie si une adresse IP est joignable (ping -c 1, comme sur le Pi).
    """
    try:
        output = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return output.returncode == 0
    except Exception as e:
        logger.error("Erreur lors de la vérification IP %s : %s", ip, e)
        return False


# ── Fonctions de démarrage "pures" (utilisent SystemConfig) ──────────────────

def demarrage_serveur_SMS(cfg: SystemConfig) -> None:
    logger.info("Démarrage service SMS (Hi-Link)")
    sms_thread = envoi_sms.SMSModule(cfg.nom_portique, phone_numbers=cfg.SMS)
    sms_thread.setName("SMS_Module_Thread")
    sms_thread.start()


def demarrage_compteurs(cfg: SystemConfig) -> None:
    start_comptage(cfg)
    logger.info("Démarrage des modules de comptage")


def demarrage_cellules(cfg: SystemConfig) -> None:
    logger.info("Démarrage des modules de contrôle des cellules")

    input1_watcher = etat_cellule_1.InputWatcher(cfg.mode_sans_cellules, cfg.sim)
    input1_watcher.setName("Etat_Cellule_1_Watcher")
    input1_watcher.start()

    input2_watcher = etat_cellule_2.InputWatcher(cfg.mode_sans_cellules, cfg.sim)
    input2_watcher.setName("Etat_Cellule_2_Watcher")
    input2_watcher.start()

    list_watcher = vitesse_chargement.ListWatcher(
        cfg.distance_cellules, cfg.mode_sans_cellules
    )
    list_watcher.setName("Vitesse_Chargement_Watcher")
    list_watcher.start()


def demarrage_fonctions_camera(cfg: SystemConfig) -> None:
    logger.info("Démarrage prise de photo et ANPR")
    prise_plaque = prise_photo.PrisePhoto(cfg.RTSP, cfg.mode_sans_cellules)
    prise_plaque.setName("Prise_Plaque_Thread")
    prise_plaque.start()


def demarrage_alarmes(cfg: SystemConfig) -> None:
    start_alarmes(cfg)
    logger.info("Démarrage des modules d'alarmes")


def demarrage_acq(cfg: SystemConfig) -> None:
    logger.info("Démarrage du contrôle acquittement")
    t = acquittement.InputWatcher(cfg.sim)
    t.setName("Acquittement_InputWatcher")
    t.start()


def demarrage_stock_base(cfg: SystemConfig) -> None:
    logger.info("Démarrage du module d'écriture BDD")
    t = DB_write.DataRecorder()
    t.setName("DB_Write_Thread")
    t.start()


def demarrage_defaut(cfg: SystemConfig) -> None:
    start_defauts(cfg)
    logger.info("Démarrage des modules de défauts")


def demarrage_courbe(cfg: SystemConfig) -> None:
    start_courbes(cfg)
    logger.info("Démarrage des modules de courbes")


def demarrage_relais(cfg: SystemConfig) -> None:
    logger.info("Démarrage du module relais")
    t = relais.Relais()
    t.setName("Relais_Thread")
    t.start()


def demarrage_report_pdf(cfg: SystemConfig) -> None:
    logger.info("Démarrage moteur génération PDF")

    noms_detecteurs = [
        cfg.D1_nom, cfg.D2_nom, cfg.D3_nom, cfg.D4_nom,
        cfg.D5_nom, cfg.D6_nom, cfg.D7_nom, cfg.D8_nom,
        cfg.D9_nom, cfg.D10_nom, cfg.D11_nom, cfg.D12_nom,
    ]
    t = rapport_pdf.ReportThread(
        cfg.nom_portique,
        cfg.mode_sans_cellules,
        noms_detecteurs,
        cfg.seuil2,
        cfg.language,
    )
    t.setName("Rapport_PDF_Thread")
    t.start()


def demarrage_serveur_email(cfg: SystemConfig) -> None:
    logger.info("Démarrage serveur mail")
    email_sender = Envoi_email.EmailSender(
        cfg.nom_portique,
        cfg.smtp_server,
        cfg.port,
        cfg.login,
        cfg.password,
        cfg.sender,
        cfg.recipients,
    )
    email_sender.setName("Email_Sender_Thread")
    email_sender.start()


def demarrage_int_modbus(cfg: SystemConfig) -> None:
    logger.info("Démarrage communication ModBus")
    t = modbus_interface.ModbusThread(cfg.echeance)
    t.setName("Modbus_Thread")
    t.start()


def demarrage_eVx_interface(cfg: SystemConfig) -> None:
    logger.info("Démarrage communication protocole eVx")
    t = eVx_interface.eVx_Start()
    t.setName("eVx_Interface_Thread")
    t.start()


def demarrage_F2C_Driver(cfg: SystemConfig) -> None:
    logger.info("Démarrage communication protocole F2C")
    t = Driver_F2C.F2CThread()
    t.setName("F2C_Driver_Thread")
    t.start()


def demarrage_API_Web(cfg: SystemConfig) -> None:
    logger.info("Démarrage Serveur WSGI (Flask)")
    args = (
        cfg.D1_nom, cfg.D2_nom, cfg.D3_nom, cfg.D4_nom,
        cfg.D5_nom, cfg.D6_nom, cfg.D7_nom, cfg.D8_nom,
        cfg.D9_nom, cfg.D10_nom, cfg.D11_nom, cfg.D12_nom,
        cfg.nom_portique,
        cfg.mode_sans_cellules,
        cfg.echeance,
    )
    flask_thread = threading.Thread(
        target=api_flsk.run_flask_app,
        args=args,
        name="Flask_API_Thread",
        daemon=True,
    )
    flask_thread.start()


def demarrage_stockage_bdf(cfg: SystemConfig) -> None:
    logger.info("Démarrage collection de BDF")
    t = collect_bdf.DataCollector()
    t.setName("Collect_BDF_Thread")
    t.start()


def demarrage_control_diskspc(cfg: SystemConfig) -> None:
    logger.info("Démarrage nettoyage disque")
    directories_to_clean = [
        "/home/pi/Partage/rapports",
        "/home/pi/Partage/photo",
    ]
    monitor = Chkdisk.DiskSpaceMonitor(dirs_to_clean=directories_to_clean)
    monitor.setName("Chkdisk_Thread")
    monitor.start()


def demarrage_control_cle_USB(cfg: SystemConfig) -> None:
    logger.info("Démarrage contrôle clé USB")
    t = threading.Thread(
        target=USB_control.run_headless,
        name="USB_Control_Thread",
        daemon=True,
    )
    t.start()


def control_open_cell(cfg: SystemConfig) -> None:
    logger.info("Démarrage contrôle ouverture cellules")
    chk_cell = Check_open_cell.etat_cellule_check(cfg.mode_sans_cellules)
    chk_cell.setName("Check_Open_Cell_Thread")
    chk_cell.start()


def demarrage_Srv_Unipi(cfg: SystemConfig) -> None:
    logger.info("Démarrage Serveur Unipi")
    t = Svr_Unipi.Svr_Unipi_rec()
    t.setName("Srv_Unipi_Thread")
    t.start()


def Watchdog(cfg: SystemConfig) -> None:
    logger.info("Démarrage Watchdog")
    monitor_thread = threading.Thread(
        target=Thread_Watchdog.monitor_threads,
        name="MonitorThread",
        daemon=True,
    )
    monitor_thread.start()


# ── Classe de haut niveau : Gev5System ───────────────────────────────────────

class Gev5System:
    """
    Orchestrateur de démarrage GeV5 à partir d'un SystemConfig.
    """

    def __init__(self, cfg: SystemConfig) -> None:
        self.cfg = cfg
        self._sim_app = None

    def start_all(self) -> None:
        cfg = self.cfg
        logger.info("=== Démarrage GeV5 pour le portique %s ===", cfg.nom_portique)

        # Simulateur éventuel
        if cfg.sim == 1:
            logger.info("Mode SIM = 1 : démarrage du simulateur Tkinter")
            self._sim_app = simulateur.Application()

        # Démarrage des différents services (ordre inspiré de GeV5_Moteur.main)
        demarrage_Srv_Unipi(cfg)
        demarrage_compteurs(cfg)
        demarrage_cellules(cfg)

        if cfg.camera == 1:
            demarrage_fonctions_camera(cfg)

        demarrage_alarmes(cfg)
        demarrage_acq(cfg)
        demarrage_defaut(cfg)
        demarrage_courbe(cfg)
        demarrage_stock_base(cfg)
        demarrage_report_pdf(cfg)
        demarrage_serveur_email(cfg)

        # Modbus
        if cfg.modbus == 1:
            ouvrir_ports([502, 5200])
            demarrage_int_modbus(cfg)
        else:
            fermer_ports([502, 5200])

        # eVx / F2C
        if cfg.eVx == 1:
            ouvrir_ports([9000, 6789])
            demarrage_eVx_interface(cfg)
            demarrage_F2C_Driver(cfg)
        else:
            fermer_ports([9000, 6789])

        if cfg.mod_SMS == 1:
            demarrage_serveur_SMS(cfg)

        # API Web
        demarrage_API_Web(cfg)

        # Stockage BDF / maintenance
        demarrage_stockage_bdf(cfg)
        demarrage_control_diskspc(cfg)
        control_open_cell(cfg)

        # Check IPs des Hubs
        if is_ip_reachable(cfg.Rem_IP):
            logger.info("Le Hub %s est joignable.", cfg.Rem_IP)
        else:
            logger.warning("Le Hub %s n'est pas joignable.", cfg.Rem_IP)

        if is_ip_reachable(cfg.Rem_IP_2):
            logger.info("Le Hub %s est joignable.", cfg.Rem_IP_2)
        else:
            logger.warning("Le Hub %s n'est pas joignable.", cfg.Rem_IP_2)

        # Relais, watchdog, clé USB
        demarrage_relais(cfg)
        Watchdog(cfg)
        demarrage_control_cle_USB(cfg)

        logger.info("Chargement du moteur GeV5 terminé.")

        # Boucle Tk si simulateur
        if cfg.sim == 1 and self._sim_app is not None:
            logger.info("Entrée dans la boucle principale du simulateur Tkinter.")
            self._sim_app.mainloop()


def start_all(cfg: SystemConfig) -> None:
    """
    Fonction helper si tu ne veux pas instancier la classe à la main.
    """
    system = Gev5System(cfg)
    system.start_all()
