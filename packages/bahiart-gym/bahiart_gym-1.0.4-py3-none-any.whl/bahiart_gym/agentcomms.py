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
import threading
from bahiart_gym.server.singleton import Singleton

class InvalidHostAndPortLengths(Exception):
    """ Raised when Host and Port lists has different sizes """
    pass

class AgentComms(metaclass=Singleton):
    """
    Communication class between Gym and Agents.
    Constructor default parameters creates a HOST-PORT localhost-3200 connection
    """
    

    def __init__(self,  port=4100):

        
 
        self.gymsock= socket.socket()        
        print ("[AGENT COMMS] Socket successfully created")
                       
        self.gymsock.bind(('', port))        
        print ("[AGENT COMMS] socket binded to %s" %(port))
         
        self.gymsock.listen(11)    
        print ("[AGENT COMMS] socket is listening")      
        
        self.agents={}
        self.agentMessages={}
         
        threading._start_new_thread(self.acceptConnections,())
 



################################
 #        if len(host)!=len(port):
 #            raise InvalidHostAndPortLengths("Host and Port lists should have the same size!")
 #        self.HOST = host
 #        self.PORT = port
 #        self.socks=[]
 #        i=1
 #        try: 
 #            for h in host:
 #                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 #                self.socks.append(sock)             
 #                print("Socket {} created".format(i))
 #                i=i+1
 #        except socket.error as err:
 #            print("Socket {} not created.".format(i))
 #            print("Error : " + str(err))
        
 #        i=1
 #        try: 
            
 #            for h,p,s in zip(host,port,self.socks):
 #                s.connect((h, p))
              
 #                print("[AGENTCOMMS]Connection {} established".format(i))
 #                i+=1
 # #               s.setblocking(0)
 #        except socket.error as err:
 #            print("[AGENTCOMMS]Connection {} not established.".format(i))
 #            print("Error : " + str(err))


    def acceptConnections(self):
        """
        Accept connections from agents in Training Mode. Must run as an independent Thread.

        Returns
        -------
        None.

        """
        while True:        
            c, addr = self.gymsock.accept()    
            print ('[AGENT COMMS] Got connection from', addr )
            msg = c.recv(4)  
            num = int.from_bytes(msg, 'little') 
            unum = socket.ntohl(num)

            msg = "Ok"
            msgLen = socket.htonl(len(msg))
            prefix = msgLen.to_bytes(4, 'little')
            fullmsg = str(prefix, "utf-8") + msg
            if unum>0:
                self.agents[unum]=c
                print("[AGENT COMMS] Agent %s connected." %(unum))
                c.send(fullmsg.encode())
            else:
                if msg==0:
                    print("[AGENT COMMS] Client %s closed the connection." %(addr))
                elif msg==-1:
                    print("[AGENT COMMS] Error receiving message from %s." %(addr))
   
        
    def sendAll(self, msg: str):
        """
        Sends environment message msg to all agents.
        Returns true if message sent or false if there is any problem.

        Parameters
       ----------
        None
        
        Returns
        -------
        Boolean.
        
        """
        msgLen = socket.htonl(len(msg))
        prefix = msgLen.to_bytes(4, 'little')
        fullmsg = str(prefix, "utf-8") + msg
    
        try:
            for unum in self.agents:
                self.agents[unum].sendall(fullmsg.encode())
                #print("[AGENT COMMS]Socket message sent to player %s." %(unum))
                #print("[AGENT COMMS]Socket message: {}".format(fullmsg))
            return True

        except socket.error as err:
           print("[AGENT COMMS]Socket message not sent to player %s." %(unum))
           print("Error : " + str(err))
           print("Message : " + str(fullmsg))
           return False

    def send(self, unum: int, msg:str):     
       """
       Sends the message msg to the agent identified by the number of t-shirt in the list of sockets initialized in this object.
       Returns true if message sent or false if there is any problem.

       Parameters
       ----------
       unum : int
           number of player's t-shirt used as index to retrieve its socket.
       msg : str
            Message to be sent.
        
        Returns
        -------
        Boolean.
        
        """
       msgLen = socket.htonl(len(msg))
       prefix = msgLen.to_bytes(4, 'little')
       fullmsg = str(prefix, "utf-8") + msg
       
       try:
           sock=self.agents[unum]
           sock.sendall(fullmsg.encode())    
           #print("[AGENT COMMS] Socket message sent to player %s." %(unum))
           return True
       except KeyError:
            print("[AGENT COMMS] Player %s has no connection initialized to Gym." %(unum))
            return False
       except socket.error as err:
           #pass
           print("[AGENTCOMMS] Socket message not sent.")
           print("Error : " + str(err))
           print("Message : " + str(fullmsg))
           return False
        
    def receiveAll(self):
        """
        Receive messages from all connected agents.

        """
        try:
            for unum in self.agents:
                length = self.agents[unum].recv(4)          
                sockLen = int.from_bytes(length, 'little')          
                sockIntLen = socket.ntohl(sockLen)
                if(unum not in self.agentMessages):
                    self.agentMessages[unum] = []
                try:
                    self.agentMessages[unum].append(self.agents[unum].recv(sockIntLen).decode())
                except Exception as e:
                    print("Couldn't add message into list")
                    print(str(e))
        except socket.error as err:
            print("[AGENT COMMS]Socket message not received from player %s" %(unum))
            print("Error : " + str(err))
                  
    def receive(self,unum: int):
        """
        Receive a message from player number unum.

        Parameters
        ----------
        unum : int
            Number of player's t-shirt whose message is received.

        """
        try:
            length = self.agents[unum].recv(4)          
            sockLen = int.from_bytes(length, 'little')          
            sockIntLen = socket.ntohl(sockLen)
            if(unum not in self.agentMessages):
                self.agentMessages[unum] = []
            try:
                self.agentMessages[unum].append(self.agents[unum].recv(sockIntLen).decode())
            except Exception as e:
                print("Couldn't add message into list")
                print(str(e))
            #print("[AGENT COMMS]Socket message received from player %s." %(unum))
        except KeyError:
            print("[AGENT COMMS] Player %s has no connection initialized to Gym." %(unum))
        except socket.error as err:
            print("[AGENT COMMS]Socket message not received rom player %s." %(unum))
            print("Error : " + str(err))


    def getAgentMessages(self):
        """
        Returns dictionary with agent messages and clear previous messages.

        Parameters
        ----------
        None

        Returns
        -------
        Dictionary.

        """
        agentMsgs = self.agentMessages.copy()
        self.agentMessages = {}
        return agentMsgs