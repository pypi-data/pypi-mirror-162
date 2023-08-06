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
from bahiart_gym.server.player import Player
import socket
from bahiart_gym.server.agentProxy import AgentProxy
import threading


class Proxy:


    def __init__(self,agent_port,server_port=3100,server_host='localhost'):

        self.SERVER_HOST = server_host
        self.SERVER_PORT = server_port
        self.AGENT_PORT = agent_port

        self.agentSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.agentSock.bind(('localhost', self.AGENT_PORT))
   
        self.proxies = []

    def start(self):
        threading._start_new_thread(self.main,())

    def getMessagesFromAgent(self,agentNumber:str):
        messages = []
        for x in range(len(self.proxies)):
            if self.proxies[x].getAgentNumber() == agentNumber:
                messages = self.proxies[x].getAgentMessages()
        
        self.verifyAgent(agentNumber)
        return messages
    
    def getPlayerObj(self,agentNumber:str):
        for x in range(len(self.proxies)):
            if self.proxies[x].getAgentNumber() == agentNumber:
                player = self.proxies[x].getPlayerObj()
                self.verifyAgent(agentNumber)
                return player
        
        self.verifyAgent(agentNumber)
        return None

    def verifyAgent(self,agentNumber:str):
        for x in range(len(self.proxies)):
            if self.proxies[x].getAgentNumber() == agentNumber:
                if not self.proxies[x].getIsConnected():
                    self.proxies.remove(self.proxies[x])

    def main(self):
        while True:
            self.agentSock.listen()
            newAgentSock, _ = self.agentSock.accept()


            try:
                pxy = AgentProxy(newAgentSock,self.SERVER_PORT,self.SERVER_HOST)
                pxy.connectionManager()
                self.proxies.append(pxy)
                print("[PROXY] New agent connected on port : " + str(self.AGENT_PORT))
            except:
                print("[PROXY] Couldn't connect new agent.")