import etat_cellule_1, etat_cellule_2
import comptage_6
import vitesse_chargement
import alarme_6
import threading, time

class Courbe6(threading.Thread):
    
    courbe6_liste = {1: [],2: [],3:[]}
    
    def __init__(self,D6_ON,Mode_sans_cellules):
        threading.Thread.__init__(self)
        self.liste = []
        self.D6_ON = D6_ON
        self.mss = Mode_sans_cellules
        self.t_start = None
        self.t = 0
        
    def run(self):
        while True:
            if self.D6_ON == 0:
                self.courbe6_liste[1] = []
                self.courbe6_liste[2] = []
                self.courbe6_liste[3] = []
                break
            if self.D6_ON == 1:            
                self.liste = etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]
                self.mes = alarme_6.Alarme6.mesure[6]

                if 1 in self.liste and self.mss == 0:
                    self.valeur = comptage_6.Frequence_6_Thread.compteur[6]

                    if self.t_start is None:
                        self.courbe6_liste[1] = []
                        self.courbe6_liste[2] = []
                        self.courbe6_liste[3] = []
                        self.t_start = time.time()
                    self.courbe6_liste[1].append(self.valeur)
                    self.courbe6_liste[2].append(time.time()-self.t_start)
                    try:
                        self.courbe6_liste[3].append((time.time()-self.t_start) * vitesse_chargement.ListWatcher.vitesse[1])
                    except:
                        self.courbe6_liste[3].append((time.time()-self.t_start) * 1)
                if 1 in self.liste and self.mss == 1:
                    self.valeur = comptage_6.Frequence_6_Thread.compteur[6]
                    if self.mes == 1:
                        self.courbe6_liste[1] = []
                        self.courbe6_liste[2] = []
                        self.courbe6_liste[3] = []
                        t = 0
                    if self.mes == 2:
                        self.courbe6_liste[1].append(self.valeur)
                        t=t+1
                        self.courbe6_liste[2].append(t)
                        
                if 1 not in self.liste and self.D6_ON == 1 and self.mes == 0:
                    self.t_start = None
                
                time.sleep(0.1)
                
