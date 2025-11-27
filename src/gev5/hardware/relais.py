import time
import requests
import threading
import alarme_1, alarme_2, alarme_3, alarme_4,alarme_5, alarme_6, alarme_7, alarme_8,alarme_9, alarme_10, alarme_11, alarme_12
#import alarme_1_2,alarme_2_2,alarme_3_2,alarme_4_2
import defaut_1, defaut_2, defaut_3, defaut_4,defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import etat_cellule_1, etat_cellule_2
import websocket
import Check_open_cell


class Relais(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)

        self.liste_alarm = []
        self.liste_defaut = []
        self.list_cell = []
        self.flag_al_1 = 0
        self.flag_al_2 = 0
        self.flag_def_1 = 0
        self.flag_cell = 0

        self.ws = websocket.WebSocket()  # Ouverture du socket vers les relai Unipi
        self.ws.connect("ws://127.0.0.1:8080/ws")
        
        self.ws.send('{"cmd":"set","dev":"relay","circuit":"3","value":"0"}') #al1
        self.ws.send('{"cmd":"set","dev":"relay","circuit":"4","value":"0"}') #al2
        self.ws.send('{"cmd":"set","dev":"relay","circuit":"6","value":"0"}') #al
        self.ws.send('{"cmd":"set","dev":"relay","circuit":"1","value":"1"}') #def
        self.ws.send('{"cmd":"set","dev":"relay","circuit":"5","value":"1"}') #def
        self.ws.send('{"cmd":"set","dev":"relay","circuit":"2","value":"0"}') #cell

    def run(self):

        while True:
            self.liste_alarm = [alarme_1.Alarme1.alarme_resultat[1], alarme_2.Alarme2.alarme_resultat[2],
                                alarme_3.Alarme3.alarme_resultat[3], alarme_4.Alarme4.alarme_resultat[4],
                                alarme_5.Alarme5.alarme_resultat[5], alarme_6.Alarme6.alarme_resultat[6],
                                alarme_7.Alarme7.alarme_resultat[7], alarme_8.Alarme8.alarme_resultat[8],
                                alarme_9.Alarme9.alarme_resultat[9], alarme_10.Alarme10.alarme_resultat[10],
                                alarme_11.Alarme11.alarme_resultat[11], alarme_12.Alarme12.alarme_resultat[12]]
            self.liste_defaut = [defaut_1.Defaut_1.eta_defaut[1], defaut_2.Defaut_2.eta_defaut[2],
                                defaut_3.Defaut_3.eta_defaut[3], defaut_4.Defaut_4.eta_defaut[4],
                                defaut_5.Defaut_5.eta_defaut[5], defaut_6.Defaut_6.eta_defaut[6],
                                defaut_7.Defaut_7.eta_defaut[7], defaut_8.Defaut_8.eta_defaut[8],
                                defaut_9.Defaut_9.eta_defaut[9], defaut_10.Defaut_10.eta_defaut[10],
                                defaut_11.Defaut_11.eta_defaut[11], defaut_12.Defaut_12.eta_defaut[12],Check_open_cell.etat_cellule_check.defaut_cell[1]]
            self.list_cell = [etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]]

            if 1 in self.liste_alarm and self.flag_al_1 == 0:  # Test des alarmes
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"3","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"6","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"5","value":"1"}')
                self.flag_al_1 = 1
            else:
                if all(val == 0 for val in self.liste_alarm) and (self.flag_al_1 == 1 or self.flag_al_2 == 1): # Si toutes les alarmes sont à 0
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"3","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"6","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"5","value":"0"}')
                    self.flag_al_1 = 0

            if 2 in self.liste_alarm and self.flag_al_2 == 0:  # Test des alarmes
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"4","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"7","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"3","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"6","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"5","value":"1"}')

                self.flag_al_1 = 1
                self.flag_al_2 = 1
            else:
                if all(val == 0 for val in self.liste_alarm) and (self.flag_al_1 == 1 or self.flag_al_2 == 1): # Si toutes les alarmes sont à 0
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"3","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"4","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"6","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"7","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"5","value":"0"}')
                    self.flag_al_2 = 0

            if 1 in self.liste_defaut or 2 in self.liste_defaut and self.flag_def_1 == 0:  # Test des défauts
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"1","value":"0"}')
                self.flag_def_1 = 1
            else:
                if all(val == 0 for val in self.liste_defaut) and self.flag_def_1 == 1:  # Si toutes les défauts sont à 0
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"1","value":"1"}')
                    self.flag_def_1 = 0

            if 1 in (self.list_cell):  # Test des cellules
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"2","value":"1"}')
                self.ws.send('{"cmd":"set","dev":"relay","circuit":"8","value":"1"}')
                self.flag_cell = 1
            else:
                if all(val == 0 for val in self.list_cell) and self.flag_cell == 1:
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"2","value":"0"}')
                    self.ws.send('{"cmd":"set","dev":"relay","circuit":"8","value":"0"}')
                    self.flag_cell = 0

            time.sleep(1)
