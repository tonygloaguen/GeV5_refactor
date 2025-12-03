ARM_DELAY_S = 5  # anti faux départ
import time
import random
from math import sqrt
import numpy as np
import threading
from collections import deque
import simulateur
import defaut_1
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12

class Frequence_1_Thread(threading.Thread):
    compteur = {1: 0,10: 0}
    variance = {1: 0}
    LD = {1: 0}

    def __init__(self, sampling, D1_ON, pin, sim):
        threading.Thread.__init__(self)
        self.frequence = 0
        self.sampling = sampling
        self.fifo = deque(maxlen=int(10 * sampling))
        self.fifo_stat = deque(maxlen=int(36000 * sampling))
        self.compteur_old = 0
        self.D1_ON = D1_ON
        self.pin = pin
        self.sim = sim
        self.frequence = 0

        if self.sim == 0:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.increaserev_1)
    
    def increaserev_1(self, channel):
        self.frequence += 1
        return self.frequence
    
    def correction_formula(self, impulses):
        """
        Corrige la valeur mesurée en fonction d'une calibration polynomiale de degré 3
        si elle est supérieure à 9500. En dessous, la valeur est retournée telle quelle.
        """
        if impulses <= 950:
            return impulses
        else:
            # Coefficients du polynôme de degré 3
            a0 = 0.0000000000001089
            a1 = -0.000000001664
            a2 = 0.00002223
            a3 = 1.156
            a4 = -0.092

            return a0*impulses**4 + a1*impulses**3 + a2*impulses**2 + a3*impulses + a4

    def run(self):
        while True:
            if self.D1_ON == 1:
                time.sleep(0.1)
                if self.sim == 1:
                    self.frequence = (random.randint(950, 1050)) * simulateur.Application.multiplier[0]
                
                if all(alarme.pdf_gen[i] == 0 for i, alarme in enumerate([
                alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)):  # Blocage du comptage quand un PDF est généré
                    
                    frequence_filtree = self.correction_formula(self.frequence)

                    self.fifo.append(frequence_filtree / 0.1)
                    self.fifo_stat.append(frequence_filtree / 0.1)
                    if defaut_1.Defaut_1.eta_defaut[1] == 0:
                        self.compteur[1] = round((sum(self.fifo) / len(self.fifo)), 0)
                        self.compteur[10] = round((sum(self.fifo) / len(self.fifo)), 0)
                        stat = sum(self.fifo_stat) / len(self.fifo_stat)
                        self.LD[1] = stat + 8.4 * sqrt(stat)
                    else:
                        self.compteur[1] = 0
                        self.compteur[10] = round((sum(self.fifo) / len(self.fifo)), 0)
                    
                    
                    if self.compteur[1] != 0:
                        self.variance[1] = self.compteur_old / self.compteur[1]
                    self.compteur_old = self.compteur[1]
                
                self.frequence = 0

            if self.D1_ON == 0:
                self.compteur[1] = -1
                break
