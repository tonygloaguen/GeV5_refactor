import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import ssl
import alarme_1, alarme_2, alarme_3, alarme_4,alarme_5, alarme_6, alarme_7, alarme_8,alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4,defaut_5, defaut_6, defaut_7, defaut_8,defaut_9, defaut_10, defaut_11, defaut_12
import rapport_pdf
import time, os

class EmailSender(threading.Thread):
    def __init__(self, Nom_portique, smtp_server, port, login=None, password=None, sender=None, recipients=None, subject="", body="", attachment=None):
        threading.Thread.__init__(self)
        self.smtp_server = str(smtp_server)
        self.port = int(port)
        self.login = login
        self.password = password
        self.sender = sender
        self.recipients = recipients if recipients else []
        self.nom_portique = Nom_portique

    def run(self):
        while True:
            if alarme_1.Alarme1.email_send_alarm[1] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 1",None)
                alarme_1.Alarme1.email_send_alarm[1] = 0
            if alarme_2.Alarme2.email_send_alarm[2] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 2",None)
                alarme_2.Alarme2.email_send_alarm[2] = 0
            if alarme_3.Alarme3.email_send_alarm[3] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 3",None)
                alarme_3.Alarme3.email_send_alarm[3] = 0
            if alarme_4.Alarme4.email_send_alarm[4] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 4",None)
                alarme_4.Alarme4.email_send_alarm[4] = 0
            if alarme_5.Alarme5.email_send_alarm[5] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 5",None)
                alarme_5.Alarme5.email_send_alarm[5] = 0
            if alarme_6.Alarme6.email_send_alarm[6] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 6",None)
                alarme_6.Alarme6.email_send_alarm[6] = 0
            if alarme_7.Alarme7.email_send_alarm[7] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 7",None)
                alarme_7.Alarme7.email_send_alarm[7] = 0
            if alarme_8.Alarme8.email_send_alarm[8] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 8",None)
                alarme_8.Alarme8.email_send_alarm[8] = 0
            if alarme_9.Alarme9.email_send_alarm[9] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 9",None)
                alarme_9.Alarme9.email_send_alarm[9] = 0
            if alarme_10.Alarme10.email_send_alarm[10] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 10",None)
                alarme_10.Alarme10.email_send_alarm[10] = 0
            if alarme_11.Alarme11.email_send_alarm[11] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 11",None)
                alarme_11.Alarme11.email_send_alarm[11] = 0
            if alarme_12.Alarme12.email_send_alarm[12] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Alarme radiologique sur détecteur 12",None)
                alarme_12.Alarme12.email_send_alarm[12] = 0
            if defaut_1.Defaut_1.email_send_defaut[1] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 1 - {defaut_1.Defaut_1.eta_defaut[10]}",None)
                defaut_1.Defaut_1.email_send_defaut[1] = 2
            if defaut_2.Defaut_2.email_send_defaut[2] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 2 - {defaut_2.Defaut_2.eta_defaut[20]}",None)
                defaut_2.Defaut_2.email_send_defaut[2] = 2
            if defaut_3.Defaut_3.email_send_defaut[3] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 3 - {defaut_3.Defaut_3.eta_defaut[30]}",None)
                defaut_3.Defaut_3.email_send_defaut[3] = 2
            if defaut_4.Defaut_4.email_send_defaut[4] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 4 - {defaut_4.Defaut_4.eta_defaut[40]}",None)
                defaut_4.Defaut_4.email_send_defaut[4] = 2
            if defaut_5.Defaut_5.email_send_defaut[5] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 5 - {defaut_5.Defaut_5.eta_defaut[50]}",None)
                defaut_5.Defaut_5.email_send_defaut[5] = 2
            if defaut_6.Defaut_6.email_send_defaut[6] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 6 - {defaut_6.Defaut_6.eta_defaut[60]}",None)
                defaut_6.Defaut_6.email_send_defaut[6] = 2
            if defaut_7.Defaut_7.email_send_defaut[7] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 7 - {defaut_7.Defaut_7.eta_defaut[70]}",None)
                defaut_7.Defaut_7.email_send_defaut[7] = 2
            if defaut_8.Defaut_8.email_send_defaut[8] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 8 - {defaut_8.Defaut_8.eta_defaut[80]}",None)
                defaut_8.Defaut_8.email_send_defaut[8] = 2
            if defaut_9.Defaut_9.email_send_defaut[9] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 9 - {defaut_9.Defaut_9.eta_defaut[90]}",None)
                defaut_9.Defaut_9.email_send_defaut[9] = 2
            if defaut_10.Defaut_10.email_send_defaut[10] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 10 - {defaut_10.Defaut_10.eta_defaut[100]}",None)
                defaut_10.Defaut_10.email_send_defaut[10] = 2
            if defaut_11.Defaut_11.email_send_defaut[11] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 11 - {defaut_11.Defaut_11.eta_defaut[110]}",None)
                defaut_11.Defaut_11.email_send_defaut[11] = 2
            if defaut_12.Defaut_12.email_send_defaut[12] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}",f"Alarme technique sur détecteur 12 - {defaut_12.Defaut_12.eta_defaut[120]}",None)
                defaut_12.Defaut_12.email_send_defaut[12] = 2

            if rapport_pdf.ReportThread.email_send_rapport[1] == 1:
                self.send_email(f"Message portique Berthold GeV5 - {self.nom_portique}","Rapport de passage",rapport_pdf.ReportThread.email_send_rapport[10])
            time.sleep(0.1)

    def create_server(self, context):
        try:
            if self.port == 465:
                return smtplib.SMTP_SSL(self.smtp_server, self.port, context=context)
            else:
                server = smtplib.SMTP(self.smtp_server, self.port)
                server.ehlo()
                if self.port in [587, 2525]:
                    server.starttls(context=context)
                return server
        except Exception as e:
            print(e)
            return None

    def send_email(self, subject, body, attachment):
        context = ssl.create_default_context()
        try:
            server = self.create_server(context)
            if server is not None:
                if self.login and self.password and self.port != 25:
                    server.login(self.login, self.password)
                self._send(server, subject, body, attachment)
            else:
                print("Failed to create server connection.")
        except ssl.SSLCertVerificationError:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            server = self.create_server(context)
            if server is not None:
                if self.login and self.password and self.port != 25:
                    server.login(self.login, self.password)
                self._send(server, subject, body, attachment)
            else:
                print("Failed to create server connection after SSL certificate verification error.")
        except Exception as e:
            raise
            print(e)
        rapport_pdf.ReportThread.email_send_rapport[1] = 0
        print("Email envoyé : ", body)

    def _send(self, server,subject,body,attachment):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ", ".join(self.recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachment:
            filename = os.path.basename(attachment)
            with open(attachment, "rb") as attach_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attach_file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)
        server.sendmail(msg['From'], self.recipients, msg.as_string())
        server.quit()