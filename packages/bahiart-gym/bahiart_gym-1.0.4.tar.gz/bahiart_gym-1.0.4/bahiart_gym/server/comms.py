"""
        Copyright (C) 2022  Salvador, Bahia
        Gabriel Mascarenhas, Marco A. C. Simões, Rafael Fonseca

        This file is part of BahiaRT GYM.

        BahiaRT GYM is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as
        published by the Free Software Foundation, either version 3 of the
        License, or (at your option) any later version.

        BahiaRT GYM is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Affero General Public License for more details.

        You should have received a copy of the GNU Affero General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import socket
import select as slt
from bahiart_gym.server.serverParser import ServerParser
from bahiart_gym.server.singleton import Singleton

class Comms(metaclass=Singleton):
    """
    Communication class between Gym and Server.
    Constructor default parameters creates a HOST-PORT localhost-3200 connection
    """
    

    def __init__(self, host='localhost', port=3200):
        self.HOST = host
        self.PORT = port
        print("Trying connection to ",self.HOST,":",self.PORT, flush=True)
        print("\ntype(port)",type(self.PORT), flush=True)
        try: 
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[COMMS] Socket created.")
        except socket.error as err:
            print("[COMMS] Socket not created.")
            print("[COMMS] Error : " + str(err))
        try: 
            self.sock.connect((self.HOST, self.PORT))
            self.serverSocket = self.sock
            print("[COMMS] Connection established to ",self.HOST,":",self.PORT, flush=True)
            self.serverSocket.setblocking(0)
        except socket.error as err:
            print("[COMMS] Connection not established.", flush=True)
            print("[COMMS] Error : " + str(err), flush=True)

        self.setParser()



    def setParser(self):
        self.serverParser = ServerParser()

    def send(self, msg: str):
        """
        Sends trainer message to server.
        """
        msgLen = socket.htonl(len(msg))
        prefix = msgLen.to_bytes(4, 'little')
        fullmsg = str(prefix, "utf-8") + msg
        try:
            self.sock.send(fullmsg.encode())
            #print("Socket message sent.")
        except socket.error as err:
            pass
            #print("Socket message not sent.")
            #print("Error : " + str(err))
            #print("Message : " + str(fullmsg))

    def updateSExp(self):
        try:
            ready = slt.select([self.sock], [], [], 5)
            if not ready[0]:
                return False
        
            # Receive 4 first bytes which contains message lenght info
            lenght = self.sock.recv(4)                                                               
            
            # Converts message bytes into integer, 
            # with the bytes ordered from lowest to highest(little)
            sockLen = int.from_bytes(lenght, 'little')          
            
            # Converts message lenght from 'network' to 'host long'(NtoHL) 
            sockIntLen = socket.ntohl(sockLen)

            read=0

            # Receive message with the right size as parameter until byteMsg has the full server message
            byteMsg = None

            while read < sockIntLen:
                if byteMsg is None:
                    byteMsg = self.sock.recv(sockIntLen-read)
                else:
                    byteMsg += self.sock.recv(sockIntLen-read)
                if byteMsg is not None:
                    read = len(byteMsg)

        except socket.timeout:
            print("[COMMS] Timeout in updateSExp")
            return(False)
        except socket.error as err:
            print("[COMMS] Socker error in updateSExp")
            return(False)
        except:
            print("[COMMS] Connection Dropped in updateSExp")
            return(False)

        #Transforms byteMsg into string
        self.sexp = str(byteMsg, 'utf-8')

        #Sends string with the S-Expression to the parser
        try:
            self.serverExp = self.serverParser.parse(self.sexp)
        except Exception as e:
            pass
            #print("-----COMMS SERVER PARSE EXCEPTION-----: ")
            #print(e)