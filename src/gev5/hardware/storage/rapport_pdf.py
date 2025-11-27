import threading
import os
import time
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
from datetime import datetime
import json

import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import courbe_1, courbe_2, courbe_3, courbe_4, courbe_5, courbe_6, courbe_7, courbe_8, courbe_9, courbe_10, courbe_11, courbe_12
import defaut_1, defaut_2, defaut_3, defaut_4, defaut_5, defaut_6, defaut_7, defaut_8, defaut_9, defaut_10, defaut_11, defaut_12
import vitesse_chargement
import prise_photo

class ReportThread(threading.Thread):
    email_send_rapport = {1: 0, 10: None}
    
    def __init__(self, Nom_portique, Mode_sans_cellules, noms_detecteurs, seuil2, language):
        super().__init__()
        self.nom_portique = Nom_portique
        self.mss = Mode_sans_cellules
        self.noms_detecteurs = noms_detecteurs
        self.seuil2 = seuil2
        self.print_in_cas_alarm = 0
        self.language = language
        self.translations = self.load_translations()

    def load_translations(self):
        with open('/home/pi/GeV5/static/lang/translations.json', 'r') as file:
            return json.load(file)

    def get_translation(self, key, *args):
        return self.translations[self.language][key].format(*args)

    def run(self):
        while True:
            try:
                if any(alarme.pdf_gen[i] == 1 for i, alarme in enumerate([
                    alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                    alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                    alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)):
                    self.generate_report()
                    for i, alarme in enumerate([
                        alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                        alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                        alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                    ], start=1):
                        alarme.pdf_gen[i] = 0
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in run loop: {e}")

    def generate_graph(self, data, filename, title, threshold):
        try:
            plt.figure(figsize=(5, 4))
            plt.plot(data['x'], data['y'], marker='o')
            plt.axhline(y=threshold, color='r', linestyle='--', label=self.get_translation('follower_threshold', threshold))
            plt.legend()
            plt.title(title)
            plt.xlabel(self.get_translation("load_lenght") if self.mss != 1 else self.get_translation('nb_points'))
            plt.ylabel('Cps')
            plt.grid(True)
            plt.savefig(filename, format='png')
        except Exception as e:
            print(f"Error generating graph: {e}")
        finally:
            plt.close()

    def compile_data(self):
        self.liste_suiveur = [alarme.suiv[i] for i, alarme in enumerate([
            alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
            alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
            alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
        ], start=1)]
        self.liste_val_max = [alarme.val_max[i] for i, alarme in enumerate([
            alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
            alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
            alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
        ], start=1)]
        self.liste_defaut = [defaut.eta_defaut[i] for i, defaut in enumerate([
            defaut_1.Defaut_1, defaut_2.Defaut_2, defaut_3.Defaut_3, defaut_4.Defaut_4, 
            defaut_5.Defaut_5, defaut_6.Defaut_6, defaut_7.Defaut_7, defaut_8.Defaut_8, 
            defaut_9.Defaut_9, defaut_10.Defaut_10, defaut_11.Defaut_11, defaut_12.Defaut_12
        ], start=1)]
        self.liste_bdf = [alarme.val_deb_mes[i] for i, alarme in enumerate([
            alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
            alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
            alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
        ], start=1)]
        
        self.resultats = [self.get_translation("detection", i, int(self.liste_val_max[i-1]) / int(self.liste_suiveur[i-1])) for i in range(1, 13) if self.liste_val_max[i-1] > self.liste_suiveur[i-1] or self.liste_val_max[i-1] > self.seuil2]
        print(self.resultats)
        if self.resultats:
            self.print_in_cas_alarm = 1
        if not self.resultats:
            self.resultats = [self.get_translation("no_detection")]
        
        self.eta_defaut = self.get_translation('technical_status') if 1 in self.liste_defaut else 'Mesure validée sans défaut technique'

    def generate_report(self):
        self.compile_data()
        if self.print_in_cas_alarm == 1:
        
            self.data = {
                self.get_translation('background_noise', i): [alarme.val_deb_mes[i], 'cps'] for i, alarme in enumerate([
                    alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                    alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                    alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)
            }
            self.data.update({
                self.get_translation('follower_threshold', i): [alarme.suiv[i], 'cps'] for i, alarme in enumerate([
                    alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                    alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                    alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)
            })
            self.data.update({
                self.get_translation('max_measure_value', i): [alarme.val_max[i], 'cps'] for i, alarme in enumerate([
                    alarme_1.Alarme1, alarme_2.Alarme2, alarme_3.Alarme3, alarme_4.Alarme4, 
                    alarme_5.Alarme5, alarme_6.Alarme6, alarme_7.Alarme7, alarme_8.Alarme8, 
                    alarme_9.Alarme9, alarme_10.Alarme10, alarme_11.Alarme11, alarme_12.Alarme12
                ], start=1)
            })
            self.data.update({
                self.get_translation('loading_speed'): [vitesse_chargement.ListWatcher.vitesse[1], 'km/h'],
                self.get_translation('technical_status'): [self.eta_defaut, ''],
                self.get_translation('measurement_result'): self.resultats,
                'graphs': [
                    {'x': courbe_1.Courbe1.courbe1_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_1.Courbe1.courbe1_liste[3], 'y': courbe_1.Courbe1.courbe1_liste[1]} if alarme_1.Alarme1.val_deb_mes[1] > 0 else None,
                    {'x': courbe_2.Courbe2.courbe2_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_2.Courbe2.courbe2_liste[3], 'y': courbe_2.Courbe2.courbe2_liste[1]} if alarme_2.Alarme2.val_deb_mes[2] > 0 else None,
                    {'x': courbe_3.Courbe3.courbe3_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_3.Courbe3.courbe3_liste[3], 'y': courbe_3.Courbe3.courbe3_liste[1]} if alarme_3.Alarme3.val_deb_mes[3] > 0 else None,
                    {'x': courbe_4.Courbe4.courbe4_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_4.Courbe4.courbe4_liste[3], 'y': courbe_4.Courbe4.courbe4_liste[1]} if alarme_4.Alarme4.val_deb_mes[4] > 0 else None,
                    {'x': courbe_5.Courbe5.courbe5_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_5.Courbe5.courbe5_liste[3], 'y': courbe_5.Courbe5.courbe5_liste[1]} if alarme_5.Alarme5.val_deb_mes[5] > 0 else None,
                    {'x': courbe_6.Courbe6.courbe6_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_6.Courbe6.courbe6_liste[3], 'y': courbe_6.Courbe6.courbe6_liste[1]} if alarme_6.Alarme6.val_deb_mes[6] > 0 else None,
                    {'x': courbe_7.Courbe7.courbe7_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_7.Courbe7.courbe7_liste[3], 'y': courbe_7.Courbe7.courbe7_liste[1]} if alarme_7.Alarme7.val_deb_mes[7] > 0 else None,
                    {'x': courbe_8.Courbe8.courbe8_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_8.Courbe8.courbe8_liste[3], 'y': courbe_8.Courbe8.courbe8_liste[1]} if alarme_8.Alarme8.val_deb_mes[8] > 0 else None,
                    {'x': courbe_9.Courbe9.courbe9_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_9.Courbe9.courbe9_liste[3], 'y': courbe_9.Courbe9.courbe9_liste[1]} if alarme_9.Alarme9.val_deb_mes[9] > 0 else None,
                    {'x': courbe_10.Courbe10.courbe10_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_10.Courbe10.courbe10_liste[3], 'y': courbe_10.Courbe10.courbe10_liste[1]} if alarme_10.Alarme10.val_deb_mes[10] > 0 else None,
                    {'x': courbe_11.Courbe11.courbe11_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_11.Courbe11.courbe11_liste[3], 'y': courbe_11.Courbe11.courbe11_liste[1]} if alarme_11.Alarme11.val_deb_mes[11] > 0 else None,
                    {'x': courbe_12.Courbe12.courbe12_liste[2] if (self.mss == 1 or vitesse_chargement.ListWatcher.vitesse[1] == 0) else courbe_12.Courbe12.courbe12_liste[3], 'y': courbe_12.Courbe12.courbe12_liste[1]} if alarme_12.Alarme12.val_deb_mes[12] > 0 else None
                ]
            })

            self.data['graphs'] = [graph for graph in self.data['graphs'] if graph is not None]

            maintenant = datetime.now()
            formatted_time = maintenant.strftime("%d%m%Y_%H%M")
            pdf_filename = self.email_send_rapport[10] = f"/home/pi/Partage/rapports/rapport_{formatted_time}.pdf"

            graph_filenames = [f"/home/pi/GeV5/temp/graph{i}.png" for i in range(1, 13)]
            graph_titles = self.noms_detecteurs
            logo_filename = "/home/pi/GeV5/static/logo.png"
            external_image_path = prise_photo.PrisePhoto.filename[1]
            footer_label = self.get_translation('footer')
            footer_variable = self.nom_portique
            footer_date_time = maintenant.strftime("%d/%m/%Y %H:%M")

            for i, graph_data in enumerate(self.data['graphs']):
                self.generate_graph(graph_data, graph_filenames[i], graph_titles[i], self.liste_suiveur[i])

            c = canvas.Canvas(pdf_filename, pagesize=letter)
            width, height = letter

            def add_footer(c):
                c.setFont("Helvetica", 8)
                footer_text = f"{footer_label} | {footer_variable} | {footer_date_time}"
                c.drawString(50, 30, footer_text)

            c.drawImage(logo_filename, 50, height - 50 - 50, width=1.5 * inch, height=0.5 * inch)
            c.line(50, height - 100, width - 50, height - 100)

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 130, self.get_translation('title'))
            c.line(50, height - 150, width - 50, height - 150)

            if external_image_path:
                c.drawImage(external_image_path, (width - 4 * inch) / 2, height - 500, width=5 * inch, height=4 * inch)
                c.showPage()
                add_footer(c)
                c.drawImage(logo_filename, 50, height - 50 - 50, width=1.5 * inch, height=0.5 * inch)
            y_position = height - 350
            for i, graph_filename in enumerate(graph_filenames[:len(self.data['graphs'])]):
                if i > 0 and i % 4 == 0:
                    c.showPage()
                    add_footer(c)
                    c.drawImage(logo_filename, 50, height - 50 - 50, width=1.5 * inch, height=0.5 * inch)
                    y_position = height - 350

                c.drawImage(graph_filename, 50 if i % 2 == 0 else width - 300, y_position, width=250, height=200)
                if i % 2 == 1:
                    y_position -= 220

            c.showPage()
            c.drawImage(logo_filename, 50, height - 50 - 50, width=1.5 * inch, height=0.5 * inch)
            y_position = height - 150

            variable_sections = [
                (
                    self.noms_detecteurs[i-1], 
                    [
                        self.get_translation('background_noise', i), 
                        self.get_translation('follower_threshold', i), 
                        self.get_translation('max_measure_value', i)
                    ]
                ) 
                for i in range(1, 13) 
                if self.data[self.get_translation('background_noise', i)][0] > 0
            ]

            variable_sections.append(('Résumé', [self.get_translation('loading_speed'), self.get_translation('technical_status')]))

            section_count = 0
            for section_title, variables in variable_sections:
                if section_count > 0 and section_count % 4 == 0:
                    c.showPage()
                    add_footer(c)
                    c.drawImage(logo_filename, 50, height - 50, width=1.5 * inch, height=0.5 * inch)
                    y_position = height - 100
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, section_title)
                c.line(50, y_position - 10, width - 50, y_position - 10)
                
                c.setFont("Helvetica", 10)
                text = c.beginText(50, y_position - 30)       
                for var in variables:
                    valeur = self.data.get(var, ['N/A', ''])
                    try:
                        if self.print_in_cas_alarm == 1:
                            text.setFillColor('red')  # Changer la couleur si l'alarme est activée
                        elif int(valeur[0]) > 10 and valeur[1] == "km/h":
                            text.setFillColor('red')
                        else:
                            text.setFillColor('black')
                    except:
                        text.setFillColor('black')
                    
                    text.textLine(f"{var}: {valeur[0]} {valeur[1]}")
                                        
                c.drawText(text)
                y_position -= 100
                section_count += 1
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, self.get_translation('measurement_result'))
            c.line(50, y_position - 10, width - 50, y_position - 10)
            c.setFont("Helvetica", 10)
            text = c.beginText(50, y_position - 30)
            for result in self.resultats:
                if "alarme" in result.lower():
                    text.setFillColor('red')
                else:
                    text.setFillColor('black')

                text.textLine(result)

            c.drawText(text)
            text.setFillColor('black')
            add_footer(c)
            c.save()
       
            print("PDF Généré",pdf_filename)
                        
            courbe_1.Courbe1.courbe1_liste = {1: [], 2: [], 3: []}
            courbe_2.Courbe2.courbe2_liste = {1: [], 2: [], 3: []}
            courbe_3.Courbe3.courbe3_liste = {1: [], 2: [], 3: []}
            courbe_4.Courbe4.courbe4_liste = {1: [], 2: [], 3: []}
            courbe_5.Courbe5.courbe5_liste = {1: [], 2: [], 3: []}
            courbe_6.Courbe6.courbe6_liste = {1: [], 2: [], 3: []}
            courbe_7.Courbe7.courbe7_liste = {1: [], 2: [], 3: []}
            courbe_8.Courbe8.courbe8_liste = {1: [], 2: [], 3: []}
            courbe_9.Courbe9.courbe9_liste = {1: [], 2: [], 3: []}
            courbe_10.Courbe10.courbe10_liste = {1: [], 2: [], 3: []}
            courbe_11.Courbe11.courbe11_liste = {1: [], 2: [], 3: []}
            courbe_12.Courbe12.courbe12_liste = {1: [], 2: [], 3: []}

            self.email_send_rapport[1] = 1
            print("Alarme : email rapport envoyé")
            self.print_in_cas_alarm = 0
