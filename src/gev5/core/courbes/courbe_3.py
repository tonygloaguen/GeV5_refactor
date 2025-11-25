import etat_cellule_1, etat_cellule_2
import comptage_3
import vitesse_chargement
import alarme_3
import threading, time

class Courbe3(threading.Thread):
    
    courbe3_liste = {1: [],2: [],3:[]}
    
    def __init__(self,D3_ON,Mode_sans_cellules):
        threading.Thread.__init__(self)
        self.liste = []
        self.D3_ON = D3_ON
        self.mss = Mode_sans_cellules
        self.t_start = None
        self.t = 0
        
    def run(self):
        while True:
            if self.D3_ON == 0:
                self.courbe3_liste[1] = []
                self.courbe3_liste[2] = []
                self.courbe3_liste[3] = []
                break
            if self.D3_ON == 1:            
                self.liste = etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]
                self.mes = alarme_3.Alarme3.mesure[3]

                if 1 in self.liste and self.mss == 0:
                    self.valeur = comptage_3.Frequence_3_Thread.compteur[3]

                    if self.t_start is None:
                        self.courbe3_liste[1] = []
                        self.courbe3_liste[2] = []
                        self.courbe3_liste[3] = []
                        self.t_start = time.time()
                    self.courbe3_liste[1].append(self.valeur)
                    self.courbe3_liste[2].append(time.time()-self.t_start)
                    try:
                        self.courbe3_liste[3].append((time.time()-self.t_start) * vitesse_chargement.ListWatcher.vitesse[1])
                    except:
                        self.courbe3_liste[3].append((time.time()-self.t_start) * 1)
                if 1 in self.liste and self.mss == 1:
                    self.valeur = comptage_3.Frequence_3_Thread.compteur[3]
                    if self.mes == 1:
                        self.courbe3_liste[1] = []
                        self.courbe3_liste[2] = []
                        self.courbe3_liste[3] = []
                        t = 0
                    if self.mes == 2:
                        self.courbe3_liste[1].append(self.valeur)
                        t=t+1
                        self.courbe3_liste[2].append(t)
                        
                if 1 not in self.liste and self.D3_ON == 1 and self.mes == 0:
                    self.t_start = None
                
                time.sleep(0.1)
                
