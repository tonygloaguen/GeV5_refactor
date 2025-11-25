"""main.py — Application principale Berthold GeV5
Intègre l’envoi SMS via la clé 4G Huawei E3372h‑320 en mode Hi‑Link.
Le module Hi‑Link s’appelle **envoi_sms.py** et se trouve dans le même dossier.
"""

from __future__ import annotations

import subprocess
import threading
from datetime import datetime
import sqlite3

# ── Modules internes ──────────────────────────────────────────────────────────
import comptage_1, comptage_2, comptage_3, comptage_4, comptage_5, comptage_6, comptage_7, comptage_8, comptage_9, comptage_10, comptage_11, comptage_12
import etat_cellule_1, etat_cellule_2, vitesse_chargement
import prise_photo
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import acquittement
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import simulateur
import courbe_1, courbe_2, courbe_3, courbe_4, courbe_5, courbe_6, courbe_7, courbe_8, courbe_9, courbe_10, courbe_11, courbe_12
import DB_write, rapport_pdf, Envoi_email
import modbus_interface
import eVx_interface
import Driver_F2C
import envoi_sms                          # ← nouveau module Hi‑Link
import api_flsk
import collect_bdf
import Chkdisk
import USB_control
import Check_open_cell
import relais
import Svr_Unipi
import Thread_Watchdog

def ouvrir_ports(ports, proto='tcp'):
    for port in ports:
        subprocess.run(['sudo', 'ufw', 'allow', f'{port}/{proto}'])

def fermer_ports(ports, proto='tcp'):
    for port in ports:
        subprocess.run(['sudo', 'ufw', 'deny', f'{port}/{proto}'])

def demarrage_serveur_SMS(Nom_portique: str, SMS: list[str]):
    
    """Lance le thread d’envoi SMS via la clé Hi‑Link."""
    print("Démarrage service SMS (Hi‑Link)")
    sms_thread = envoi_sms.SMSModule(Nom_portique, phone_numbers=SMS)
    sms_thread.setName("SMS_Module_Thread")
    sms_thread.start()

def demarrage_compteurs(sample_time, D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON):

    print("Démarrage des modules de comptage")

    # Démarrage // des 8 voies de comptage
    
    comptage_1_thread = comptage_1.Frequence_1_Thread(sample_time, D1_ON, pin_1, sim)
    comptage_1_thread.setName("Comptage_1_Thread")
    comptage_1_thread.start()
    
    comptage_2_thread = comptage_2.Frequence_2_Thread(sample_time, D2_ON, pin_2, sim)
    comptage_2_thread.setName("Comptage_2_Thread")
    comptage_2_thread.start()
    
    comptage_3_thread = comptage_3.Frequence_3_Thread(sample_time, D3_ON, pin_3, sim)
    comptage_3_thread.setName("Comptage_3_Thread")
    comptage_3_thread.start()
    
    comptage_4_thread = comptage_4.Frequence_4_Thread(sample_time, D4_ON, pin_4, sim)
    comptage_4_thread.setName("Comptage_4_Thread")
    comptage_4_thread.start()
    
    comptage_5_thread = comptage_5.Frequence_5_Thread(sample_time, D5_ON, base_url, sim)
    comptage_5_thread.setName("Comptage_5_Thread")
    comptage_5_thread.start()
    
    comptage_6_thread = comptage_6.Frequence_6_Thread(sample_time, D6_ON, base_url, sim)
    comptage_6_thread.setName("Comptage_6_Thread")
    comptage_6_thread.start()
    
    comptage_7_thread = comptage_7.Frequence_7_Thread(sample_time, D7_ON, base_url, sim)
    comptage_7_thread.setName("Comptage_7_Thread")
    comptage_7_thread.start()
    
    comptage_8_thread = comptage_8.Frequence_8_Thread(sample_time, D8_ON, base_url, sim)
    comptage_8_thread.setName("Comptage_8_Thread")
    comptage_8_thread.start()
    
    comptage_9_thread = comptage_9.Frequence_9_Thread(sample_time, D9_ON, base_url_2, sim)
    comptage_9_thread.setName("Comptage_9_Thread")
    comptage_9_thread.start()
    
    comptage_10_thread = comptage_10.Frequence_10_Thread(sample_time, D10_ON, base_url_2, sim)
    comptage_10_thread.setName("Comptage_10_Thread")
    comptage_10_thread.start()
    
    comptage_11_thread = comptage_11.Frequence_11_Thread(sample_time, D11_ON, base_url_2, sim)
    comptage_11_thread.setName("Comptage_11_Thread")
    comptage_11_thread.start()
    
    comptage_12_thread = comptage_12.Frequence_12_Thread(sample_time, D12_ON, base_url_2, sim)
    comptage_12_thread.setName("Comptage_12_Thread")
    comptage_12_thread.start()

def demarrage_cellules(distance_cellules, Mode_sans_cellules):

    print("Démarrage des modules de contrôle des cellules")

    # Démarrage // du contrôle des deux cellules

    input1_watcher = etat_cellule_1.InputWatcher(Mode_sans_cellules, sim)
    input1_watcher.setName("Etat_Cellule_1_Watcher")
    input1_watcher.start()
    
    input2_watcher = etat_cellule_2.InputWatcher(Mode_sans_cellules, sim)
    input2_watcher.setName("Etat_Cellule_2_Watcher")
    input2_watcher.start()
    
    list_watcher = vitesse_chargement.ListWatcher(distance_cellules, Mode_sans_cellules)
    list_watcher.setName("Vitesse_Chargement_Watcher")
    list_watcher.start()

def demarrage_fonctions_camera(RTSP, Mode_sans_cellules):

    print("Démarrage prise de photo et ANPR")

    # Fonctions de photo en cas de passage et contrôle des plaques

    prise_plaque = prise_photo.PrisePhoto(RTSP, Mode_sans_cellules)
    prise_plaque.setName("Prise_Plaque_Thread")
    prise_plaque.start()

def demarrage_alarmes(multiple, seuil2, D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON, Mode_sans_cellules,suiv_block):

    print("Démarrage des modules d'alarmes")
    
    somme_det = 0
    somme_list = [D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON]
    for v in somme_list:
        somme_det += v

    controle_alarmes_1 = alarme_1.Alarme1(multiple, seuil2, D1_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_1.setName("Alarme_1_Thread")
    controle_alarmes_1.start()
    
    controle_alarmes_2 = alarme_2.Alarme2(multiple, seuil2, D2_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_2.setName("Alarme_2_Thread")
    controle_alarmes_2.start()
    
    controle_alarmes_3 = alarme_3.Alarme3(multiple, seuil2, D3_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_3.setName("Alarme_3_Thread")
    controle_alarmes_3.start()
    
    controle_alarmes_4 = alarme_4.Alarme4(multiple, seuil2, D4_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_4.setName("Alarme_4_Thread")
    controle_alarmes_4.start()

    controle_alarmes_5 = alarme_5.Alarme5(multiple, seuil2, D5_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_5.setName("Alarme_5_Thread")
    controle_alarmes_5.start()
    
    controle_alarmes_6 = alarme_6.Alarme6(multiple, seuil2, D6_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_6.setName("Alarme_6_Thread")
    controle_alarmes_6.start()
    
    controle_alarmes_7 = alarme_7.Alarme7(multiple, seuil2, D7_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_7.setName("Alarme_7_Thread")
    controle_alarmes_7.start()
    
    controle_alarmes_8 = alarme_8.Alarme8(multiple, seuil2, D8_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_8.setName("Alarme_8_Thread")
    controle_alarmes_8.start()
    
    controle_alarmes_9 = alarme_9.Alarme9(multiple, seuil2, D9_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_9.setName("Alarme_9_Thread")
    controle_alarmes_9.start()
    
    controle_alarmes_10 = alarme_10.Alarme10(multiple, seuil2, D10_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_10.setName("Alarme_10_Thread")
    controle_alarmes_10.start()
    
    controle_alarmes_11 = alarme_11.Alarme11(multiple, seuil2, D11_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_11.setName("Alarme_11_Thread")
    controle_alarmes_11.start()
    
    controle_alarmes_12 = alarme_12.Alarme12(multiple, seuil2, D12_ON, Mode_sans_cellules, somme_det, suiv_block)
    controle_alarmes_12.setName("Alarme_12_Thread")
    controle_alarmes_12.start()


def demarrage_acq(sim):

    print("Démarrage du contrôle acquittement")

    input_acq_watcher = acquittement.InputWatcher(sim)
    input_acq_watcher.setName("Acquittement_InputWatcher")
    input_acq_watcher.start()

def demarrage_stock_base():

    print("Démarrage du module d'écriture BDD")

    ecrit_base = DB_write.DataRecorder()
    ecrit_base.setName("DB_Write_Thread")
    ecrit_base.start()

def demarrage_defaut(low, high, D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON):

    print("Démarrage des modules de defaut")

    # Démarrage // des 8 voies de defaut

    defaut_1_thread = defaut_1.Defaut_1(low, high, D1_ON)
    defaut_1_thread.setName("Defaut_1_Thread")
    defaut_1_thread.start()
    
    defaut_2_thread = defaut_2.Defaut_2(low, high, D2_ON)
    defaut_2_thread.setName("Defaut_2_Thread")
    defaut_2_thread.start()
    
    defaut_3_thread = defaut_3.Defaut_3(low, high, D3_ON)
    defaut_3_thread.setName("Defaut_3_Thread")
    defaut_3_thread.start()
    
    defaut_4_thread = defaut_4.Defaut_4(low, high, D4_ON)
    defaut_4_thread.setName("Defaut_4_Thread")
    defaut_4_thread.start()

    defaut_5_thread = defaut_5.Defaut_5(low, high, D5_ON)
    defaut_5_thread.setName("Defaut_5_Thread")
    defaut_5_thread.start()
    
    defaut_6_thread = defaut_6.Defaut_6(low, high, D6_ON)
    defaut_6_thread.setName("Defaut_6_Thread")
    defaut_6_thread.start()
    
    defaut_7_thread = defaut_7.Defaut_7(low, high, D7_ON)
    defaut_7_thread.setName("Defaut_7_Thread")
    defaut_7_thread.start()
    
    defaut_8_thread = defaut_8.Defaut_8(low, high, D8_ON)
    defaut_8_thread.setName("Defaut_8_Thread")
    defaut_8_thread.start()
    
    defaut_9_thread = defaut_9.Defaut_9(low, high, D9_ON)
    defaut_9_thread.setName("Defaut_9_Thread")
    defaut_9_thread.start()
    
    defaut_10_thread = defaut_10.Defaut_10(low, high, D10_ON)
    defaut_10_thread.setName("Defaut_10_Thread")
    defaut_10_thread.start()
    
    defaut_11_thread = defaut_11.Defaut_11(low, high, D11_ON)
    defaut_11_thread.setName("Defaut_11_Thread")
    defaut_11_thread.start()
    
    defaut_12_thread = defaut_12.Defaut_12(low, high, D12_ON)
    defaut_12_thread.setName("Defaut_12_Thread")
    defaut_12_thread.start()


def demarrage_courbe(D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON, Mode_sans_cellules):

    print("Démarrage de l'acquisition des courbes")

    # Démarrage // du l'acquisition et traitement courbes valeurs en mesure

    courbe_1_thread = courbe_1.Courbe1(D1_ON, Mode_sans_cellules)
    courbe_1_thread.setName("Courbe_1_Thread")
    courbe_1_thread.start()
    
    courbe_2_thread = courbe_2.Courbe2(D2_ON, Mode_sans_cellules)
    courbe_2_thread.setName("Courbe_2_Thread")
    courbe_2_thread.start()
    
    courbe_3_thread = courbe_3.Courbe3(D3_ON, Mode_sans_cellules)
    courbe_3_thread.setName("Courbe_3_Thread")
    courbe_3_thread.start()
    
    courbe_4_thread = courbe_4.Courbe4(D4_ON, Mode_sans_cellules)
    courbe_4_thread.setName("Courbe_4_Thread")
    courbe_4_thread.start()

    courbe_5_thread = courbe_5.Courbe5(D5_ON, Mode_sans_cellules)
    courbe_5_thread.setName("Courbe_5_Thread")
    courbe_5_thread.start()
    
    courbe_6_thread = courbe_6.Courbe6(D6_ON, Mode_sans_cellules)
    courbe_6_thread.setName("Courbe_6_Thread")
    courbe_6_thread.start()
    
    courbe_7_thread = courbe_7.Courbe7(D7_ON, Mode_sans_cellules)
    courbe_7_thread.setName("Courbe_7_Thread")
    courbe_7_thread.start()
    
    courbe_8_thread = courbe_8.Courbe8(D8_ON, Mode_sans_cellules)
    courbe_8_thread.setName("Courbe_8_Thread")
    courbe_8_thread.start()
    
    courbe_9_thread = courbe_9.Courbe9(D9_ON, Mode_sans_cellules)
    courbe_9_thread.setName("Courbe_9_Thread")
    courbe_9_thread.start()
    
    courbe_10_thread = courbe_10.Courbe10(D10_ON, Mode_sans_cellules)
    courbe_10_thread.setName("Courbe_10_Thread")
    courbe_10_thread.start()
    
    courbe_11_thread = courbe_11.Courbe11(D11_ON, Mode_sans_cellules)
    courbe_11_thread.setName("Courbe_11_Thread")
    courbe_11_thread.start()
    
    courbe_12_thread = courbe_12.Courbe12(D12_ON, Mode_sans_cellules)
    courbe_12_thread.setName("Courbe_12_Thread")
    courbe_12_thread.start()


def demarrage_relais():

    print("Démarrage du module relais")

    relais_thread = relais.Relais()
    relais_thread.setName("Relais_Thread")
    relais_thread.start()

def demarrage_interface():
    
    print("Démarrage interface moteur")
    
    interface_thread = interface.Interface()
    interface_thread.setName("Interface_Thread")
    interface_thread.start()

def demarrage_report_pdf(Nom_portique, Mode_sans_cellules, noms_detecteurs, seuil2, language):
    
    print("Démarrage moteur génération PDF")
    
    rapport_thread = rapport_pdf.ReportThread(Nom_portique, Mode_sans_cellules, noms_detecteurs, seuil2, language)
    rapport_thread.setName("Rapport_PDF_Thread")
    rapport_thread.start()

def demarrage_serveur_email(smtp_server, port, login, password, sender, recipients, Nom_portique):
    
    print("Démarrage serveur mail")

    email_sender = Envoi_email.EmailSender(Nom_portique, smtp_server, port, login, password, sender, recipients)
    email_sender.setName("Email_Sender_Thread")
    email_sender.start()

def demarrage_int_modbus(echeance):
    
    print("Démarrage communication ModBus")
    
    modbus_thread = modbus_interface.ModbusThread(echeance)
    modbus_thread.setName("Modbus_Thread")
    modbus_thread.start()

def demarrage_eVx_interface():
    
    print("Démarrage communication protocole eVx")
    
    eVx_thread = eVx_interface.eVx_Start()
    eVx_thread.setName("eVx_Interface_Thread")
    eVx_thread.start()

def demarrage_F2C_Driver():
    
    print("Démarrage communication protocole F2C")
    
    F2C_thread = Driver_F2C.F2CThread()
    F2C_thread.setName("F2C_Driver_Thread")
    F2C_thread.start()
    
#def demarrage_serveur_SMS(Nom_portique, SMS):

#    print("Démarrage serveur mail")

#    sms_module = envoi_sms.SMSModule(Nom_portique, phone_numbers=SMS)
#    sms_module.setName("SMS_Module_Thread")
#    sms_module.start()
    
def demarrage_API_Web(D1_nom, D2_nom, D3_nom, D4_nom, D5_nom, D6_nom, D7_nom, D8_nom, D9_nom, D10_nom, D11_nom, D12_nom, Nom_portique, Mode_sans_cellules, echeance):
    
    print("Démarrage Serveur WSGI")
    
    flask_thread = threading.Thread(target=api_flsk.run_flask_app, args=(D1_nom, D2_nom, D3_nom, D4_nom, D5_nom, D6_nom, D7_nom, D8_nom, D9_nom, D10_nom, D11_nom, D12_nom, Nom_portique, Mode_sans_cellules, echeance))
    flask_thread.setName("Flask_API_Thread")
    flask_thread.start()

def demarrage_stockage_bdf():
    
    print("Démarrage collection de bdf")

    collector = collect_bdf.DataCollector()
    collector.setName("Collect_BDF_Thread")
    collector.start()

def demmarage_control_diskspc():
    
    print("Démarrage nettoyage disque")
    
    directories_to_clean = [
        "/home/pi/Partage/rapports",
        "/home/pi/Partage/photo"
    ]

    monitor = Chkdisk.DiskSpaceMonitor(dirs_to_clean=directories_to_clean)
    monitor.setName("Chkdisk_Thread")
    monitor.start()

def demarrage_control_cle_USB():
    
    print("Démarrage contrôle clé USB")
    t = threading.Thread(
        target=USB_control.run_headless,   # ⬅️ plus main()
        name="USB_Control_Thread",
        daemon=True
    )
    t.start()

def control_open_cell(Mode_sans_cellules):
    
    print("Démarrage contrôle ouverture cellules")
    
    chk_cell = Check_open_cell.etat_cellule_check(Mode_sans_cellules)
    chk_cell.setName("Check_Open_Cell_Thread")
    chk_cell.start()
def demarrage_Srv_Unipi():
    
    print("Démarrage Serveur Unipi")
    
    Srv_unipi_control = Svr_Unipi.Svr_Unipi_rec()
    Srv_unipi_control.setName("Srv_Unipi_Thread")
    Srv_unipi_control.start()
    
def Watchdog():
    
    print("Démarrage Watchdog")

    monitor_thread = threading.Thread(target=Thread_Watchdog.monitor_threads, name="MonitorThread", daemon=True)
    monitor_thread.start()
    
def is_ip_reachable(ip):
    """
    Vérifie si une adresse IP est joignable.

    :param ip: Adresse IP à vérifier.
    :return: True si l'adresse IP est joignable, False sinon.
    """
    try:
        # Utilise la commande ping en fonction du système d'exploitation
        output = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Erreur lors de la vérification de l'IP: {e}")
        return False

# Ajout des appels aux fonctions pour les détecteurs 5 à 8
if __name__ == '__main__':

    # Fonction pour récupérer les paramètres depuis la base de données
    def get_parametres(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT nom, valeur FROM Parametres')
        rows = c.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    # Chemin de la base de données
    db_path = '/home/pi/Partage/Base_donnees/Parametres.db'
    try:
        parametres = get_parametres(db_path)
    except sqlite3.OperationalError:
        import reinit_params
        parametres = get_parametres(db_path)

    # Conversion des paramètres si nécessaire
    parametres['sample_time'] = float(parametres['sample_time'])
    parametres['distance_cellules'] = float(parametres['distance_cellules'])
    parametres['Mode_sans_cellules'] = int(parametres['Mode_sans_cellules'])
    parametres['multiple'] = float(parametres['multiple'])
    parametres['seuil2'] = int(parametres['seuil2'])
    parametres['low'] = int(parametres['low'])
    parametres['high'] = int(parametres['high'])
    parametres['camera'] = int(parametres['camera'])
    parametres['modbus'] = int(parametres['modbus'])
    parametres['eVx'] = int(parametres['eVx'])
    parametres['mod_SMS'] = int(parametres['mod_SMS'])
    parametres['D1_ON'] = int(parametres['D1_ON'])
    parametres['D2_ON'] = int(parametres['D2_ON'])
    parametres['D3_ON'] = int(parametres['D3_ON'])
    parametres['D4_ON'] = int(parametres['D4_ON'])
    parametres['D5_ON'] = int(parametres['D5_ON'])
    parametres['D6_ON'] = int(parametres['D6_ON'])
    parametres['D7_ON'] = int(parametres['D7_ON'])
    parametres['D8_ON'] = int(parametres['D8_ON'])
    parametres['D9_ON'] = int(parametres['D9_ON'])
    parametres['D10_ON'] = int(parametres['D10_ON'])
    parametres['D11_ON'] = int(parametres['D11_ON'])
    parametres['D12_ON'] = int(parametres['D12_ON'])

    if parametres['port'] != "--":
        parametres['port'] = int(parametres['port'])
    parametres['recipients'] = parametres['recipients'].split(',')
    parametres['SMS'] = parametres['SMS'].split(',')

    # Calcul de l'échéance
    date_prochaine_visite = datetime.strptime(parametres['date_prochaine_visite'], "%d/%m/%Y").date()
    today = datetime.now().date()
    echeance = (date_prochaine_visite - today).days
    
    parametres['PIN_1'] = int(parametres['PIN_1'])
    parametres['PIN_2'] = int(parametres['PIN_2'])
    parametres['PIN_3'] = int(parametres['PIN_3'])
    parametres['PIN_4'] = int(parametres['PIN_4'])
    
    parametres['SIM'] = int(parametres['SIM'])

    # Les autres paramètres
    Nom_portique = parametres['Nom_portique']
    sample_time = parametres['sample_time']
    distance_cellules = parametres['distance_cellules']
    Mode_sans_cellules = parametres['Mode_sans_cellules']
    multiple = parametres['multiple']
    seuil2 = parametres['seuil2']
    low = parametres['low']
    high = parametres['high']
    camera = parametres['camera']
    modbus = parametres['modbus']
    eVx = parametres['eVx']
    mod_SMS = parametres['mod_SMS']

    D1_ON = parametres['D1_ON']
    D2_ON = parametres['D2_ON']
    D3_ON = parametres['D3_ON']
    D4_ON = parametres['D4_ON']
    D5_ON = parametres['D5_ON']
    D6_ON = parametres['D6_ON']
    D7_ON = parametres['D7_ON']
    D8_ON = parametres['D8_ON']
    D9_ON = parametres['D9_ON']
    D10_ON = parametres['D10_ON']
    D11_ON = parametres['D11_ON']
    D12_ON = parametres['D12_ON']

    D1_nom = parametres['D1_nom']
    D2_nom = parametres['D2_nom']
    D3_nom = parametres['D3_nom']
    D4_nom = parametres['D4_nom']
    D5_nom = parametres['D5_nom']
    D6_nom = parametres['D6_nom']
    D7_nom = parametres['D7_nom']
    D8_nom = parametres['D8_nom']
    D9_nom = parametres['D9_nom']
    D10_nom = parametres['D10_nom']
    D11_nom = parametres['D11_nom']
    D12_nom = parametres['D12_nom']
    
    suiv_block =  int(parametres['suiv_block'])

    Rem_IP = parametres['Rem_IP']
    base_url = f"http://{Rem_IP}:5002"
    Rem_IP_2 = parametres['Rem_IP_2']
    base_url_2 = f"http://{Rem_IP_2}:5002"

    RTSP = parametres['RTSP']
    IP = parametres['IP']

    smtp_server = parametres['smtp_server']
    port = parametres['port']
    login = parametres['login']
    password = parametres['password']
    sender = parametres['sender']
    recipients = parametres['recipients']

    SMS = parametres['SMS']
    
    pin_1 = parametres['PIN_1']
    pin_2 = parametres['PIN_2']
    pin_3 = parametres['PIN_3']
    pin_4 = parametres['PIN_4']
    
    sim = parametres['SIM']
    language = parametres['language']

    def main():
        demarrage_Srv_Unipi()
        demarrage_compteurs(sample_time, D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON)
        demarrage_cellules(distance_cellules, Mode_sans_cellules)
        if camera == 1:
            demarrage_fonctions_camera(RTSP, Mode_sans_cellules)
        demarrage_alarmes(multiple, seuil2, D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON, Mode_sans_cellules,suiv_block)
        demarrage_acq(sim)
        demarrage_defaut(low, high, D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON)
        demarrage_courbe(D1_ON, D2_ON, D3_ON, D4_ON, D5_ON, D6_ON, D7_ON, D8_ON, D9_ON, D10_ON, D11_ON, D12_ON, Mode_sans_cellules)
        demarrage_stock_base()
        noms_detecteurs = [D1_nom, D2_nom, D3_nom, D4_nom, D5_nom, D6_nom, D7_nom, D8_nom, D9_nom, D10_nom, D11_nom, D12_nom]
        demarrage_report_pdf(Nom_portique, Mode_sans_cellules, noms_detecteurs, seuil2, language)
        demarrage_serveur_email(smtp_server, port, login, password, sender, recipients, Nom_portique)
        if modbus == 1:
            ouvrir_ports([502, 5200])
            demarrage_int_modbus(echeance)
        else:
            fermer_ports([502, 5200])
        if eVx == 1:
            ouvrir_ports([9000, 6789])
            demarrage_eVx_interface()
            demarrage_F2C_Driver()
        else:
            fermer_ports([9000, 6789])
        if mod_SMS == 1:
            demarrage_serveur_SMS(Nom_portique, SMS)
        demarrage_API_Web(D1_nom, D2_nom, D3_nom, D4_nom, D5_nom, D6_nom, D7_nom, D8_nom, D9_nom, D10_nom, D11_nom, D12_nom, Nom_portique, Mode_sans_cellules, echeance)
        demarrage_stockage_bdf()
        demmarage_control_diskspc()
        control_open_cell(Mode_sans_cellules)
        
        if is_ip_reachable(Rem_IP):
            print(f"Le Hub {Rem_IP} est joignable.")
        else:
            print(f"Le Hub {Rem_IP} n'est pas joignable.")
        if is_ip_reachable(Rem_IP_2):
            print(f"Le Hub {Rem_IP_2} est joignable.")
        else:
            print(f"Le Hub {Rem_IP_2} n'est pas joignable.")
#         if sim == 0:
        demarrage_relais()
        # test_valeurs()
        Watchdog()
        demarrage_control_cle_USB()
        
    if __name__ == '__main__':
        if sim == 1:
            print("Démarrage du Simulateur")
            app = simulateur.Application()
            
        main()
        print("Chargement du main terminé")
        if sim == 1:
            app.mainloop()
        
