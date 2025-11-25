import comptage_1, comptage_2, comptage_3, comptage_4, comptage_5, comptage_6, comptage_7, comptage_8, comptage_9, comptage_10, comptage_11, comptage_12
import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import courbe_1, courbe_2, courbe_3, courbe_4, courbe_5, courbe_6, courbe_7, courbe_8, courbe_9, courbe_10, courbe_11, courbe_12
import etat_cellule_1, etat_cellule_2
import prise_photo
import vitesse_chargement
import acquittement
import threading, time

class Interface(threading.Thread):

    liste_comptage = {1 : None}
    liste_variance = {1 : None}
    liste_alarm = {1 : None}
    liste_suiveur = {1 : None}
    list_recal = {1 : None}
    liste_val_max = {1 : None}
    liste_defaut = {1 : None}
    list_cell = {1 : None}
    liste_photo = {1 : None}
    liste_vitesse = {1 : None}
    list_acq = {1 : None}
    list_mesure = {1 : None}
    list_courbe = {1: None}
    list_val_deb_mes = {1: None}

    def __init__(self):

        threading.Thread.__init__(self)

    def run(self):

        while True:
            self.liste_comptage[1] = [
                comptage_1.Frequence_1_Thread.compteur[1], comptage_2.Frequence_2_Thread.compteur[2],
                comptage_3.Frequence_3_Thread.compteur[3], comptage_4.Frequence_4_Thread.compteur[4],
                comptage_5.Frequence_5_Thread.compteur[5], comptage_6.Frequence_6_Thread.compteur[6],
                comptage_7.Frequence_7_Thread.compteur[7], comptage_8.Frequence_8_Thread.compteur[8],
                comptage_9.Frequence_9_Thread.compteur[9], comptage_10.Frequence_10_Thread.compteur[10],
                comptage_11.Frequence_11_Thread.compteur[11], comptage_12.Frequence_12_Thread.compteur[12]
            ]
            self.liste_variance[1] = [
                comptage_1.Frequence_1_Thread.variance[1], comptage_2.Frequence_2_Thread.variance[2],
                comptage_3.Frequence_3_Thread.variance[3], comptage_4.Frequence_4_Thread.variance[4],
                comptage_5.Frequence_5_Thread.variance[5], comptage_6.Frequence_6_Thread.variance[6],
                comptage_7.Frequence_7_Thread.variance[7], comptage_8.Frequence_8_Thread.variance[8],
                comptage_9.Frequence_9_Thread.variance[9], comptage_10.Frequence_10_Thread.variance[10],
                comptage_11.Frequence_11_Thread.variance[11], comptage_12.Frequence_12_Thread.variance[12]
            ]
            self.liste_alarm[1] = [
                alarme_1.Alarme1.alarme_resultat[1], alarme_2.Alarme2.alarme_resultat[2],
                alarme_3.Alarme3.alarme_resultat[3], alarme_4.Alarme4.alarme_resultat[4],
                alarme_5.Alarme5.alarme_resultat[5], alarme_6.Alarme6.alarme_resultat[6],
                alarme_7.Alarme7.alarme_resultat[7], alarme_8.Alarme8.alarme_resultat[8],
                alarme_9.Alarme9.alarme_resultat[9], alarme_10.Alarme10.alarme_resultat[10],
                alarme_11.Alarme11.alarme_resultat[11], alarme_12.Alarme12.alarme_resultat[12]
            ]
            self.liste_suiveur[1] = [
                alarme_1.Alarme1.suiv[1], alarme_2.Alarme2.suiv[2],
                alarme_3.Alarme3.suiv[3], alarme_4.Alarme4.suiv[4],
                alarme_5.Alarme5.suiv[5], alarme_6.Alarme6.suiv[6],
                alarme_7.Alarme7.suiv[7], alarme_8.Alarme8.suiv[8],
                alarme_9.Alarme9.suiv[9], alarme_10.Alarme10.suiv[10],
                alarme_11.Alarme11.suiv[11], alarme_12.Alarme12.suiv[12]
            ]
            self.liste_val_max[1] = [
                alarme_1.Alarme1.val_max[1], alarme_2.Alarme2.val_max[2],
                alarme_3.Alarme3.val_max[3], alarme_4.Alarme4.val_max[4],
                alarme_5.Alarme5.val_max[5], alarme_6.Alarme6.val_max[6],
                alarme_7.Alarme7.val_max[7], alarme_8.Alarme8.val_max[8],
                alarme_9.Alarme9.val_max[9], alarme_10.Alarme10.val_max[10],
                alarme_11.Alarme11.val_max[11], alarme_12.Alarme12.val_max[12]
            ]
            self.liste_defaut[1] = [
                defaut_1.Defaut_1.eta_defaut[1], defaut_2.Defaut_2.eta_defaut[2],
                defaut_3.Defaut_3.eta_defaut[3], defaut_4.Defaut_4.eta_defaut[4],
                defaut_5.Defaut_5.eta_defaut[5], defaut_6.Defaut_6.eta_defaut[6],
                defaut_7.Defaut_7.eta_defaut[7], defaut_8.Defaut_8.eta_defaut[8],
                defaut_9.Defaut_9.eta_defaut[9], defaut_10.Defaut_10.eta_defaut[10],
                defaut_11.Defaut_11.eta_defaut[11], defaut_12.Defaut_12.eta_defaut[12]
            ]
            self.list_cell[1] = [
                etat_cellule_1.InputWatcher.cellules[1], etat_cellule_2.InputWatcher.cellules[2]
            ]
            self.liste_photo[1] = [
                prise_photo.PrisePhoto.timestamp[1], prise_photo.PrisePhoto.filename[1], prise_photo.PrisePhoto.cam_dispo[1]
            ]
            self.liste_vitesse[1] = [vitesse_chargement.ListWatcher.vitesse]
            self.list_acq[1] = [acquittement.InputWatcher.eta_acq[1]]
            self.list_mesure[1] = [
                alarme_1.Alarme1.mesure[1], alarme_2.Alarme2.mesure[2],
                alarme_3.Alarme3.mesure[3], alarme_4.Alarme4.mesure[4],
                alarme_5.Alarme5.mesure[5], alarme_6.Alarme6.mesure[6],
                alarme_7.Alarme7.mesure[7], alarme_8.Alarme8.mesure[8],
                alarme_9.Alarme9.mesure[9], alarme_10.Alarme10.mesure[10],
                alarme_11.Alarme11.mesure[11], alarme_12.Alarme12.mesure[12]
            ]
            self.list_recal[1] = [
                alarme_1.Alarme1.recal[1], alarme_2.Alarme2.recal[2],
                alarme_3.Alarme3.recal[3], alarme_4.Alarme4.recal[4],
                alarme_5.Alarme5.recal[5], alarme_6.Alarme6.recal[6],
                alarme_7.Alarme7.recal[7], alarme_8.Alarme8.recal[8],
                alarme_9.Alarme9.recal[9], alarme_10.Alarme10.recal[10],
                alarme_11.Alarme11.recal[11], alarme_12.Alarme12.recal[12]
            ]
            self.list_courbe[1] = [
                courbe_1.Courbe1.courbe1_liste[1], courbe_1.Courbe1.courbe1_liste[2],
                courbe_2.Courbe2.courbe2_liste[1], courbe_2.Courbe2.courbe2_liste[2],
                courbe_3.Courbe3.courbe3_liste[1], courbe_3.Courbe3.courbe3_liste[2],
                courbe_4.Courbe4.courbe4_liste[1], courbe_4.Courbe4.courbe4_liste[2],
                courbe_5.Courbe5.courbe5_liste[1], courbe_5.Courbe5.courbe5_liste[2],
                courbe_6.Courbe6.courbe6_liste[1], courbe_6.Courbe6.courbe6_liste[2],
                courbe_7.Courbe7.courbe7_liste[1], courbe_7.Courbe7.courbe7_liste[2],
                courbe_8.Courbe8.courbe8_liste[1], courbe_8.Courbe8.courbe8_liste[2],
                courbe_9.Courbe9.courbe9_liste[1], courbe_9.Courbe9.courbe9_liste[2],
                courbe_10.Courbe10.courbe10_liste[1], courbe_10.Courbe10.courbe10_liste[2],
                courbe_11.Courbe11.courbe11_liste[1], courbe_11.Courbe11.courbe11_liste[2],
                courbe_12.Courbe12.courbe12_liste[1], courbe_12.Courbe12.courbe12_liste[2]
            ]
            self.list_val_deb_mes[1] = [
                alarme_1.Alarme1.val_deb_mes[1], alarme_2.Alarme2.val_deb_mes[2],
                alarme_3.Alarme3.val_deb_mes[3], alarme_4.Alarme4.val_deb_mes[4],
                alarme_5.Alarme5.val_deb_mes[5], alarme_6.Alarme6.val_deb_mes[6],
                alarme_7.Alarme7.val_deb_mes[7], alarme_8.Alarme8.val_deb_mes[8],
                alarme_9.Alarme9.val_deb_mes[9], alarme_10.Alarme10.val_deb_mes[10],
                alarme_11.Alarme11.val_deb_mes[11], alarme_12.Alarme12.val_deb_mes[12]
            ]

            print("comptage = ", self.liste_comptage[1])
            print("Bdf au demarrage = ", self.list_val_deb_mes[1])
            print("variance = ", self.liste_variance[1])
            print("seuil 1 = ", self.liste_suiveur[1])
            print("seuil 1 recal = ", self.list_recal[1])
            print("valeur max = ", self.liste_val_max[1])
            print("alarme = ", self.liste_alarm[1])
            print("defaut = ", self.liste_defaut[1])
            print("cellules = ", self.list_cell[1])
            print("photo = ", self.liste_photo[1])
            print("vitesse = ", self.liste_vitesse[1])
            print("acquittement = ", self.list_acq[1])
            print("En mesure = ", self.list_mesure[1])
            print("Courbe = ", self.list_courbe[1])

            time.sleep(1)
