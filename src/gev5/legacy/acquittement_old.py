import threading
import time
import Svr_Unipi
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12

class InputWatcher(threading.Thread):

    eta_acq = {1 : 0,2: None}

    def __init__(self,sim):
        threading.Thread.__init__(self)
        self.current_state = 0
        self.t_count_acq_auto = 0
        self.sim = sim
        self.liste_alarm = {1: None}

    def run(self):

        # Scruptation de l'état de la cellule

        while True:
            # On vérifie si toutes les valeurs de self.liste_alarm[1] sont égales à 0
            if all(value == 0 for value in [
                            alarme_1.Alarme1.alarme_resultat[1], alarme_2.Alarme2.alarme_resultat[2],
                            alarme_3.Alarme3.alarme_resultat[3], alarme_4.Alarme4.alarme_resultat[4],
                            alarme_5.Alarme5.alarme_resultat[5], alarme_6.Alarme6.alarme_resultat[6],
                            alarme_7.Alarme7.alarme_resultat[7], alarme_8.Alarme8.alarme_resultat[8],
                            alarme_9.Alarme9.alarme_resultat[9], alarme_10.Alarme10.alarme_resultat[10],
                            alarme_11.Alarme11.alarme_resultat[11], alarme_12.Alarme12.alarme_resultat[12]
                        ]):
                # Si toutes les valeurs sont à 0, on assigne 0 à self.acq_auto
                self.eta_acq[1] = 0
                self.t_count_acq_auto = 0
                if self.eta_acq[2] != None:
                    time.sleep(2) #Attente pour enregistrement dans base
                    self.eta_acq[2] = None
            else:
                self.t_count_acq_auto += 1
                if self.t_count_acq_auto == 36000:
                    self.eta_acq[2] = None
                    #Si pas d'acquittement fait, acquittement auto au bout de 1 heures      
                    self.eta_acq[1] = 1
                    self.eta_acq[2] = "Acquittement automatique"
            if self.sim == 0:
                if int(Svr_Unipi.Svr_Unipi_rec.Inp_5[1]) == 1:
                    self.eta_acq[2] = None
                    self.eta_acq[1] = 1
                    self.eta_acq[2] = "Acquittement utilisateur"
            if self.sim == 1:
                import simulateur
                new_state = simulateur.Application.acqui[0]
                if new_state != self.current_state:
                    self.eta_acq[2] = None
                    self.current_state = new_state
                    self.eta_acq[1] = int(self.current_state)
                    self.eta_acq[2] = "Acquittement simulation"
            time.sleep(0.1)
