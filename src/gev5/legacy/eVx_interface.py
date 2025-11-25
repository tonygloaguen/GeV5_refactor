import socket
import threading

import alarme_1, alarme_2, alarme_3, alarme_4, alarme_5, alarme_6, alarme_7, alarme_8, alarme_9, alarme_10, alarme_11, alarme_12
import defaut_1, defaut_2, defaut_3, defaut_4
import etat_cellule_1, etat_cellule_2

class eVx_Thread(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        with open('/home/pi/GeV5/static/version.txt', 'r') as fichier:
            self.ver = fichier.readline().strip()

    def run(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                print(f"Received from {self.client_address}: {data.decode('utf-8')}")

                string = "{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{},{},{}".format(
                    int(alarme_1.Alarme1.val_deb_mes[1]), int(alarme_2.Alarme2.val_deb_mes[2]),
                    sum([int(alarme_1.Alarme1.val_deb_mes[1]), alarme_2.Alarme2.val_deb_mes[2]]),
                    int(alarme_1.Alarme1.suiv[1]), int(alarme_2.Alarme2.suiv[2]),
                    sum([int(alarme_1.Alarme1.suiv[1]), int(alarme_2.Alarme2.suiv[2])]),
                    int(alarme_1.Alarme1.val_max[1]), int(alarme_2.Alarme2.val_max[2]),
                    sum([int(alarme_1.Alarme1.val_max[1]), int(alarme_2.Alarme2.val_max[2])]),
                    alarme_1.Alarme1.alarme_resultat[10], alarme_2.Alarme2.alarme_resultat[20],
                    sum([alarme_1.Alarme1.alarme_resultat[10], alarme_2.Alarme2.alarme_resultat[20]]))
                
                string_2 = "{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{:6},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                    int(alarme_1.Alarme1.val_deb_mes[1]), int(alarme_2.Alarme2.val_deb_mes[2]),
                    int(alarme_3.Alarme3.val_deb_mes[3]), int(alarme_4.Alarme4.val_deb_mes[4]),
                    int(alarme_5.Alarme5.val_deb_mes[5]), int(alarme_6.Alarme6.val_deb_mes[6]),
                    int(alarme_7.Alarme7.val_deb_mes[7]), int(alarme_8.Alarme8.val_deb_mes[8]),
                    int(alarme_9.Alarme9.val_deb_mes[9]), int(alarme_10.Alarme10.val_deb_mes[10]),
                    int(alarme_11.Alarme11.val_deb_mes[11]), int(alarme_12.Alarme12.val_deb_mes[12]),
                    sum([int(alarme_1.Alarme1.val_deb_mes[1]), int(alarme_2.Alarme2.val_deb_mes[2]),
                         int(alarme_3.Alarme3.val_deb_mes[3]), int(alarme_4.Alarme4.val_deb_mes[4]),
                         int(alarme_5.Alarme5.val_deb_mes[5]), int(alarme_6.Alarme6.val_deb_mes[6]),
                         int(alarme_7.Alarme7.val_deb_mes[7]), int(alarme_8.Alarme8.val_deb_mes[8]),
                         int(alarme_9.Alarme9.val_deb_mes[9]), int(alarme_10.Alarme10.val_deb_mes[10]),
                         int(alarme_11.Alarme11.val_deb_mes[11]), int(alarme_12.Alarme12.val_deb_mes[12])]),
                    int(alarme_1.Alarme1.suiv[1]), int(alarme_2.Alarme2.suiv[2]),
                    int(alarme_3.Alarme3.suiv[3]), int(alarme_4.Alarme4.suiv[4]),
                    int(alarme_5.Alarme5.suiv[5]), int(alarme_6.Alarme6.suiv[6]),
                    int(alarme_7.Alarme7.suiv[7]), int(alarme_8.Alarme8.suiv[8]),
                    int(alarme_9.Alarme9.suiv[9]), int(alarme_10.Alarme10.suiv[10]),
                    int(alarme_11.Alarme11.suiv[11]), int(alarme_12.Alarme12.suiv[12]),
                    sum([int(alarme_1.Alarme1.suiv[1]), int(alarme_2.Alarme2.suiv[2]),
                         int(alarme_3.Alarme3.suiv[3]), int(alarme_4.Alarme4.suiv[4]),
                         int(alarme_5.Alarme5.suiv[5]), int(alarme_6.Alarme6.suiv[6]),
                         int(alarme_7.Alarme7.suiv[7]), int(alarme_8.Alarme8.suiv[8]),
                         int(alarme_9.Alarme9.suiv[9]), int(alarme_10.Alarme10.suiv[10]),
                         int(alarme_11.Alarme11.suiv[11]), int(alarme_12.Alarme12.suiv[12])]),
                    int(alarme_1.Alarme1.val_max[1]), int(alarme_2.Alarme2.val_max[2]),
                    int(alarme_3.Alarme3.val_max[3]), int(alarme_4.Alarme4.val_max[4]),
                    int(alarme_5.Alarme5.val_max[5]), int(alarme_6.Alarme6.val_max[6]),
                    int(alarme_7.Alarme7.val_max[7]), int(alarme_8.Alarme8.val_max[8]),
                    int(alarme_9.Alarme9.val_max[9]), int(alarme_10.Alarme10.val_max[10]),
                    int(alarme_11.Alarme11.val_max[11]), int(alarme_12.Alarme12.val_max[12]),
                    sum([int(alarme_1.Alarme1.val_max[1]), int(alarme_2.Alarme2.val_max[2]),
                         int(alarme_3.Alarme3.val_max[3]), int(alarme_4.Alarme4.val_max[4]),
                         int(alarme_5.Alarme5.val_max[5]), int(alarme_6.Alarme6.val_max[6]),
                         int(alarme_7.Alarme7.val_max[7]), int(alarme_8.Alarme8.val_max[8]),
                         int(alarme_9.Alarme9.val_max[9]), int(alarme_10.Alarme10.val_max[10]),
                         int(alarme_11.Alarme11.val_max[11]), int(alarme_12.Alarme12.val_max[12])]),
                    alarme_1.Alarme1.alarme_resultat[10], alarme_2.Alarme2.alarme_resultat[20],
                    alarme_3.Alarme3.alarme_resultat[30], alarme_4.Alarme4.alarme_resultat[40],
                    alarme_5.Alarme5.alarme_resultat[50], alarme_6.Alarme6.alarme_resultat[60],
                    alarme_7.Alarme7.alarme_resultat[70], alarme_8.Alarme8.alarme_resultat[80],
                    alarme_9.Alarme9.alarme_resultat[90], alarme_10.Alarme10.alarme_resultat[100],
                    alarme_11.Alarme11.alarme_resultat[110], alarme_12.Alarme12.alarme_resultat[120],
                    sum([alarme_1.Alarme1.alarme_resultat[10], alarme_2.Alarme2.alarme_resultat[20],
                         alarme_3.Alarme3.alarme_resultat[30], alarme_4.Alarme4.alarme_resultat[40],
                         alarme_5.Alarme5.alarme_resultat[50], alarme_6.Alarme6.alarme_resultat[60],
                         alarme_7.Alarme7.alarme_resultat[70], alarme_8.Alarme8.alarme_resultat[80],
                         alarme_9.Alarme9.alarme_resultat[90], alarme_10.Alarme10.alarme_resultat[100],
                         alarme_11.Alarme11.alarme_resultat[110], alarme_12.Alarme12.alarme_resultat[120]]))

                length = len(string)
                string = "{:3}{}".format(length, string)
                length_2 = len(string_2)
                string_2 = "{:3}{}".format(length_2, string_2)
                print(data)
                # Vous pouvez traiter les données reçues ici et envoyer une réponse
                if 'LireValeursRadioactivite' in str(data):
                    self.client_socket.sendall(string.encode('utf-8'))  # Echo back the received data
                if 'LireValeursRadioactivite_2' in str(data):
                    self.client_socket.sendall(string.encode('utf-8'))  # Echo back the received data
                if 'bruitFondV1' in str(data):
                    self.client_socket.sendall(str(int(alarme_1.Alarme1.val_deb_mes[1])).encode('utf-8'))
                if 'bruitFondV2' in str(data):
                    self.client_socket.sendall(str(int(alarme_2.Alarme2.val_deb_mes[2])).encode('utf-8'))
                if 'bruitFondV3' in str(data):
                    self.client_socket.sendall(str(int(alarme_3.Alarme3.val_deb_mes[3])).encode('utf-8'))
                if 'bruitFondV4' in str(data):
                    self.client_socket.sendall(str(int(alarme_4.Alarme4.val_deb_mes[4])).encode('utf-8'))
                if 'bruitFondVSomme' in str(data):
                    self.client_socket.sendall(str(sum([int(alarme_1.Alarme1.val_deb_mes[1]), int(alarme_2.Alarme2.val_deb_mes[2]),int(alarme_3.Alarme3.val_deb_mes[3]),
                                                        int(alarme_4.Alarme4.val_deb_mes[4])])).encode('utf-8'))
                if 'SeuilAlarmeV1' in str(data):
                    self.client_socket.sendall(str(int(alarme_1.Alarme1.suiv[1])).encode('utf-8'))
                if 'SeuilAlarmeV2' in str(data):
                    self.client_socket.sendall(str(int(alarme_2.Alarme2.suiv[2])).encode('utf-8'))
                if 'SeuilAlarmeV3' in str(data):
                    self.client_socket.sendall(str(int(alarme_3.Alarme3.suiv[3])).encode('utf-8'))
                if 'SeuilAlarmeV4' in str(data):
                    self.client_socket.sendall(str(int(alarme_4.Alarme4.suiv[4])).encode('utf-8'))
                if 'SeuilAlarmeVSomme' in str(data):
                    self.client_socket.sendall(str(sum([int(alarme_1.Alarme1.suiv[1]), int(alarme_2.Alarme2.suiv[2]),int(alarme_3.Alarme3.suiv[3]),
                                                        int(alarme_4.Alarme4.suiv[4])])).encode('utf-8'))
                if 'MesureMaxVoie1' in str(data):
                    self.client_socket.sendall(str(int(alarme_1.Alarme1.val_max[1])).encode('utf-8'))
                if 'MesureMaxVoie2' in str(data):
                    self.client_socket.sendall(str(int(alarme_2.Alarme2.val_max[2])).encode('utf-8'))
                if 'MesureMaxVoie3' in str(data):
                    self.client_socket.sendall(str(int(alarme_3.Alarme3.val_max[3])).encode('utf-8'))
                if 'MesureMaxVoie4' in str(data):
                    self.client_socket.sendall(str(int(alarme_4.Alarme4.val_max[4])).encode('utf-8'))
                if 'MesureMaxVoieSomme' in str(data):
                    self.client_socket.sendall(str(sum([int(alarme_1.Alarme1.val_max[1]), int(alarme_2.Alarme2.val_max[2]),int(alarme_3.Alarme3.val_max[3]),
                                                        int(alarme_4.Alarme4.val_max[4])])).encode('utf-8'))
                if 'AlerteV1' in str(data):
                    self.client_socket.sendall(str(alarme_1.Alarme1.alarme_resultat[1]).encode('utf-8'))
                if 'AlerteV2' in str(data):
                    self.client_socket.sendall(str(alarme_2.Alarme2.alarme_resultat[2]).encode('utf-8'))
                if 'AlerteV3' in str(data):
                    self.client_socket.sendall(str(alarme_3.Alarme3.alarme_resultat[3]).encode('utf-8'))
                if 'AlerteV4' in str(data):
                    self.client_socket.sendall(str(alarme_4.Alarme4.alarme_resultat[4]).encode('utf-8'))
                if 'AlerteVSomme' in str(data):
                    self.client_socket.sendall(str(sum([alarme_1.Alarme1.alarme_resultat[1],alarme_2.Alarme2.alarme_resultat[2],
                                                        alarme_3.Alarme3.alarme_resultat[3],alarme_4.Alarme4.alarme_resultat[4]])).encode('utf-8'))
                if 'etaCellule_1' in str(data):
                    self.client_socket.sendall(str(etat_cellule_1.InputWatcher.cellules[1]).encode('utf-8'))
                if 'etaCellule_2' in str(data):
                    self.client_socket.sendall(str(etat_cellule_2.InputWatcher.cellules[2]).encode('utf-8'))
                if 'CON_TEST' in str(data):
                    self.client_socket.sendall("OK".encode('utf-8'))
#                 if 'infoTech' in str(data):
#                     self.client_socket.sendall("Proc à {} °C / {} Octets libre sur le media / {} charge CPU / {} Octets en "
#                                          "memoire / version soft = {}".format(self.RegInfoTech[0],
#                                                           self.RegInfoTech[1],
#                                                           self.RegInfoTech[2],
#                                                           self.RegInfoTech[3],self.ver).encode('utf-8'))
        except Exception as e:
            print(f"Error handling client {self.client_address}: {e}")
        finally:
            self.client_socket.close()


class eVx_Start(threading.Thread):
    def __init__(self, host='', port=6789):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def run(self):
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_socket.settimeout(None)
                print(f"Accepted connection from {client_address}")
                client_handler = eVx_Thread(client_socket, client_address)
                client_handler.start()
        except KeyboardInterrupt:
            print("Server is shutting down.")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            print("Close")
            self.server_socket.close()
