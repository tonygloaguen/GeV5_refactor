ARM_DELAY_S = 5  # anti faux départ
import time
import random
from math import sqrt
import threading
from collections import deque
import simulateur
import defaut_2
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12

class Frequence_2_Thread(threading.Thread):
    compteur = {2: 0, 20: 0}
    variance = {2: 0}
    LD = {2: 0}

    def __init__(self, sampling, D2_ON, pin, sim):
        threading.Thread.__init__(self)
        self.frequence = 0
        self.sampling = sampling
        self.fifo = deque(maxlen=int(10 * sampling))
        self.fifo_stat = deque(maxlen=int(36000 * sampling))
        self.compteur_old = 0
        self.D2_ON = D2_ON
        self.pin = pin
        self.sim = sim

        if self.sim == 0:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.increaserev_2)
    
    def increaserev_2(self, channel):
        self.frequence += 1
        return self.frequence
    
    def correction_formula(self, impulses):
        if impulses <= 950:
            return impulses
        else:
            a0 = 0.0000000000001089
            a1 = -0.000000001664
            a2 = 0.00002223
            a3 = 1.156
            a4 = -0.092
            return a0*impulses**4 + a1*impulses**3 + a2*impulses**2 + a3*impulses + a4

    def run(self):
        while True:
            if self.D2_ON == 1:
                time.sleep(0.1)
                if self.sim == 1:
                    self.frequence = (random.randint(950, 1050)) * simulateur.Application.multiplier[0]
                
                # blocage du comptage si génération PDF
                if all(alarme.pdf_gen[i] == 0 for i, alarme in enumerate([
                    alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                    alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                    alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)):

                    frequence_filtree = self.correction_formula(self.frequence)
                    val = frequence_filtree / 0.1

                    self.fifo.append(val)
                    self.fifo_stat.append(val)

                    # moyenne glissante
                    moy = round((sum(self.fifo) / len(self.fifo)), 0)
                    self.compteur[20] = moy  # canal brut pour défaut
                    if defaut_2.Defaut_2.eta_defaut[2] == 0:
                        self.compteur[2] = moy
                    else:
                        self.compteur[2] = 0

                    # LD
                    stat = sum(self.fifo_stat) / len(self.fifo_stat)
                    self.LD[2] = stat + 8.4 * sqrt(stat)
                    
                    # variance
                    if self.compteur[2] != 0:
                        self.variance[2] = self.compteur_old / self.compteur[2]
                    self.compteur_old = self.compteur[2]
                
                self.frequence = 0

            if self.D2_ON == 0:
                self.compteur[2] = -1
                break
