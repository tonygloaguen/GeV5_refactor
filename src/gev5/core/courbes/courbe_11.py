import etat_cellule_1, etat_cellule_2
import comptage_11
import vitesse_chargement
import alarme_11
import threading, time

class Courbe11(threading.Thread):
    
    courbe11_liste = {1: [],2: [],3:[]}
    
    def __init__(self,D11_ON,Mode_sans_cellules):
        threading.Thread.__init__(self)
        self.liste = []
        self.D11_ON = D11_ON
        self.mss = Mode_sans_cellules
        self.t_start = None
        self.t = 0
        
    def run(self):
        while True:
            if self.D11_ON == 0:
                self.courbe11_liste[1] = []
                self.courbe11_liste[2] = []
                self.courbe11_liste[3] = []
                break
            if self.D11_ON == 1:            
                self.liste = etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]
                self.mes = alarme_11.Alarme11.mesure[11]

                if 1 in self.liste and self.mss == 0:
                    self.valeur = comptage_11.Frequence_11_Thread.compteur[11]

                    if self.t_start is None:
                        self.courbe11_liste[1] = []
                        self.courbe11_liste[2] = []
                        self.courbe11_liste[3] = []
                        self.t_start = time.time()
                    self.courbe11_liste[1].append(self.valeur)
                    self.courbe11_liste[2].append(time.time()-self.t_start)
                    try:
                        self.courbe11_liste[3].append((time.time()-self.t_start) * vitesse_chargement.ListWatcher.vitesse[1])
                    except:
                        self.courbe11_liste[3].append((time.time()-self.t_start) * 1)
                if 1 in self.liste and self.mss == 1:
                    self.valeur = comptage_11.Frequence_11_Thread.compteur[11]
                    if self.mes == 1:
                        self.courbe11_liste[1] = []
                        self.courbe11_liste[2] = []
                        self.courbe11_liste[3] = []
                        t = 0
                    if self.mes == 2:
                        self.courbe11_liste[1].append(self.valeur)
                        t=t+1
                        self.courbe11_liste[2].append(t)
                        
                if 1 not in self.liste and self.D11_ON == 1 and self.mes == 0:
                    self.t_start = None
                
                time.sleep(0.1)
                
