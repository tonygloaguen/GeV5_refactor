import threading
import datetime
from pyModbusTCP.server import ModbusServer, DataBank
from time import sleep
import socket
import os

import Check_open_cell

import alarme_1, alarme_2, alarme_3, alarme_4,alarme_5, alarme_6, alarme_7, alarme_8,alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4,defaut_5, defaut_6, defaut_7, defaut_8,defaut_9, defaut_10, defaut_11, defaut_12
import etat_cellule_1, etat_cellule_2
import comptage_1, comptage_2, comptage_3, comptage_4,comptage_5,comptage_6,comptage_7,comptage_8,comptage_9,comptage_10,comptage_11,comptage_12

os.system('sudo iptables -A PREROUTING -t nat -p tcp --dport 502 -j REDIRECT --to-port 5200')

class ModbusThread(threading.Thread):
    def __init__(self,echeance):
        threading.Thread.__init__(self)
        self.server = ModbusServer("0.0.0.0", 5200, no_block=True)
        self.running = True
        self.echeance = echeance
        self.words = "0"

    def run(self):
        try:
            print("{} / Start server...".format(datetime.datetime.now()))
            self.server.start()
            print("Server is online")

            while self.running:
                self.process_modbus()
                sleep(0.5)

        except Exception as e:
            print(e)
        finally:
            print("Shutdown server...")
            self.server.stop()
            print("Server is offline")

    def process_modbus(self):
        RegMean = [
            comptage_1.Frequence_1_Thread.compteur[1], comptage_2.Frequence_2_Thread.compteur[2],
            comptage_3.Frequence_3_Thread.compteur[3], comptage_4.Frequence_4_Thread.compteur[4],
            comptage_5.Frequence_5_Thread.compteur[5], comptage_6.Frequence_6_Thread.compteur[6],
            comptage_7.Frequence_7_Thread.compteur[7], comptage_8.Frequence_8_Thread.compteur[8],
            comptage_9.Frequence_9_Thread.compteur[9], comptage_10.Frequence_10_Thread.compteur[10], 
            comptage_11.Frequence_11_Thread.compteur[11], comptage_12.Frequence_12_Thread.compteur[12]
        ]

        RegMax = [
            alarme_1.Alarme1.val_max[1], alarme_2.Alarme2.val_max[2],
            alarme_3.Alarme3.val_max[3], alarme_4.Alarme4.val_max[4],
            alarme_5.Alarme5.val_max[5], alarme_6.Alarme6.val_max[6],
            alarme_7.Alarme7.val_max[7], alarme_8.Alarme8.val_max[8],
            alarme_9.Alarme9.val_max[9], alarme_10.Alarme10.val_max[10], 
            alarme_11.Alarme11.val_max[11], alarme_12.Alarme12.val_max[12]
        ]

        RegSuiveur = [
            alarme_1.Alarme1.suiv[1], alarme_2.Alarme2.suiv[2],
            alarme_3.Alarme3.suiv[3], alarme_4.Alarme4.suiv[4],
            alarme_5.Alarme5.suiv[5], alarme_6.Alarme6.suiv[6],
            alarme_7.Alarme7.suiv[7], alarme_8.Alarme8.suiv[8],
            alarme_9.Alarme9.suiv[9], alarme_10.Alarme10.suiv[10],
            alarme_11.Alarme11.suiv[11], alarme_12.Alarme12.suiv[12]
        ]
        
        RegLD = [
            comptage_1.Frequence_1_Thread.LD[1], comptage_2.Frequence_2_Thread.LD[2],
            comptage_3.Frequence_3_Thread.LD[3], comptage_4.Frequence_4_Thread.LD[4],
            comptage_5.Frequence_5_Thread.LD[5], comptage_6.Frequence_6_Thread.LD[6],
            comptage_7.Frequence_7_Thread.LD[7], comptage_8.Frequence_8_Thread.LD[8],
            comptage_9.Frequence_9_Thread.LD[9], comptage_10.Frequence_10_Thread.LD[10], 
            comptage_11.Frequence_11_Thread.LD[11], comptage_12.Frequence_12_Thread.LD[12]
        ]
        
        RegInfoCell = [etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]]
        
        RegAlarmRadio = [
            alarme_1.Alarme1.alarme_resultat[1], alarme_2.Alarme2.alarme_resultat[2],
            alarme_3.Alarme3.alarme_resultat[3], alarme_4.Alarme4.alarme_resultat[4],
            alarme_5.Alarme5.alarme_resultat[5], alarme_6.Alarme6.alarme_resultat[6],
            alarme_7.Alarme7.alarme_resultat[7], alarme_8.Alarme8.alarme_resultat[8],
            alarme_9.Alarme9.alarme_resultat[9], alarme_10.Alarme10.alarme_resultat[10],
            alarme_11.Alarme11.alarme_resultat[11], alarme_12.Alarme12.alarme_resultat[12]
        ]

        RegAlarmTech = [
            defaut_1.Defaut_1.eta_defaut[1], defaut_2.Defaut_2.eta_defaut[2],
            defaut_3.Defaut_3.eta_defaut[3], defaut_4.Defaut_4.eta_defaut[4],
            defaut_5.Defaut_5.eta_defaut[5], defaut_6.Defaut_6.eta_defaut[6],
            defaut_7.Defaut_7.eta_defaut[7], defaut_8.Defaut_8.eta_defaut[8],
            defaut_9.Defaut_9.eta_defaut[9], defaut_10.Defaut_10.eta_defaut[10], 
            defaut_11.Defaut_11.eta_defaut[11], defaut_12.Defaut_12.eta_defaut[12]
        ]
        
        RegAlarmLD = [
            alarme_1.Alarme1.etat_point_chaud[1], alarme_2.Alarme2.etat_point_chaud[2],
            alarme_3.Alarme3.etat_point_chaud[3], alarme_4.Alarme4.etat_point_chaud[4],
            alarme_5.Alarme5.etat_point_chaud[5], alarme_6.Alarme6.etat_point_chaud[6],
            alarme_7.Alarme7.etat_point_chaud[7], alarme_8.Alarme8.etat_point_chaud[8],
            alarme_9.Alarme9.etat_point_chaud[9], alarme_10.Alarme10.etat_point_chaud[10],
            alarme_11.Alarme11.etat_point_chaud[11], alarme_12.Alarme12.etat_point_chaud[12]
        ]

        en_mesure = [
            alarme_1.Alarme1.mesure[1], alarme_2.Alarme2.mesure[2],
            alarme_3.Alarme3.mesure[3], alarme_4.Alarme4.mesure[4],
            alarme_5.Alarme5.mesure[5], alarme_6.Alarme6.mesure[6],
            alarme_7.Alarme7.mesure[7], alarme_8.Alarme8.mesure[8],
            alarme_9.Alarme9.mesure[9], alarme_10.Alarme10.mesure[10],
            alarme_11.Alarme11.mesure[11], alarme_12.Alarme12.mesure[12]
        ]

        Update = []
        for i in RegMean:
            if i == -1:
                i = 0
            Update.append(int(i))
        for i in RegSuiveur:
            Update.append(i)
        for i in RegMax:
            Update.append(i)
        for i in RegLD:
            Update.append(i)
        for i in RegInfoCell:
            Update.append(i)
        for i in RegAlarmRadio:
            Update.append(i)
        for i in RegAlarmTech:
            Update.append(i)
        for i in RegAlarmLD:
            Update.append(i)
        Update.append(sum(RegMean))
        Update.append(sum(RegMax))
        Update.append(sum(RegSuiveur))
        if (sum(RegMax) >= sum(RegSuiveur)) and sum(RegInfoCell) > 0:
            Update.append(1)
        else:
            if sum(RegAlarmRadio) == 0:
                Update.append(0)
            else:
                Update.append(1)
        Update.append(int(self.echeance))
        now = datetime.datetime.now()
        now = now.strftime("%d%m%Y%H%M%S")
        Update.append(now[0:2])
        Update.append(now[2:4])
        Update.append(now[4:8])
        Update.append(now[8:10])
        Update.append(now[10:12])
        Update.append(now[12:14])
        Update.append(int(Check_open_cell.etat_cellule_check.defaut_cell[1]))
        self.server.data_bank.set_holding_registers(0, Update)

        try:
            self.words = self.server.data_bank.get_holding_registers(99)
            if self.words is None:
                self.words = "0"
            if (alarme_1.Alarme1.etat_acq_modbus[1] != self.words[0] or 
                alarme_2.Alarme2.etat_acq_modbus[2] != self.words[0] or 
                alarme_3.Alarme3.etat_acq_modbus[3] != self.words[0] or 
                alarme_4.Alarme4.etat_acq_modbus[4] != self.words[0] or
                alarme_5.Alarme5.etat_acq_modbus[5] != self.words[0] or
                alarme_6.Alarme6.etat_acq_modbus[6] != self.words[0] or
                alarme_7.Alarme7.etat_acq_modbus[7] != self.words[0] or
                alarme_8.Alarme8.etat_acq_modbus[8] != self.words[0] or
                alarme_9.Alarme9.etat_acq_modbus[9] != self.words[0] or
                alarme_10.Alarme10.etat_acq_modbus[10] != self.words[0] or
                alarme_11.Alarme11.etat_acq_modbus[11] != self.words[0] or
                alarme_12.Alarme12.etat_acq_modbus[12] != self.words[0]):
                alarme_1.Alarme1.etat_acq_modbus[1] = self.words[0] 
                alarme_2.Alarme2.etat_acq_modbus[2] = self.words[0]
                alarme_3.Alarme3.etat_acq_modbus[3] = self.words[0] 
                alarme_4.Alarme4.etat_acq_modbus[4] = self.words[0]
                alarme_5.Alarme5.etat_acq_modbus[5] = self.words[0]
                alarme_6.Alarme6.etat_acq_modbus[6] = self.words[0]
                alarme_7.Alarme7.etat_acq_modbus[7] = self.words[0]
                alarme_8.Alarme8.etat_acq_modbus[8] = self.words[0]
                alarme_9.Alarme9.etat_acq_modbus[9] = self.words[0]
                alarme_10.Alarme10.etat_acq_modbus[10] = self.words[0]
                alarme_11.Alarme11.etat_acq_modbus[11] = self.words[0]
                alarme_12.Alarme12.etat_acq_modbus[12] = self.words[0]
                self.server.data_bank.set_holding_registers(99, [0])
                
        except Exception as e:
            print(e)
            
