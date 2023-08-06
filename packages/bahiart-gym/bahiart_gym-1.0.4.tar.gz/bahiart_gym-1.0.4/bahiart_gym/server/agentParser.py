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
from bahiart_gym.server.sexpr import str2sexpr
from bahiart_gym.server.singleton import Singleton
from multiprocessing import Lock
import numpy as np


class AgentParser(object):
    """
    Class to retrieve and parse the S-Expression sent by the server to the agents
    """

    def __init__(self):
        super().__init__()
       # self.mutex = Lock()

    def parse(self, string:str):
        parsedString = []       
      #  with self.mutex:
        try:
            if len(string)>0:
                parsedString = str2sexpr(string)   
            else:
                print("[PARSE] Empty String!")
        except Exception as e:
            print("[SEXPR] Erro:", e)
            print("Message: ",string)
        return parsedString

    def getHingePos(self, lst: list):
        hingeName = lst[0][1]
        ax=float(lst[1][1])
        return hingeName,float(ax)
                    

    
    def getAcc(self, lst:list):
        ax=float(lst[1][1])
        ay=float(lst[1][2])
        az=float(lst[1][3])
        return [ax,ay,az]
    

    def getGyr(self, lst: list):
        
        gx=float(lst[1][1])
        gy=float(lst[1][2])
        gz=float(lst[1][3])
        return [gx,gy,gz]

    def getGameState(self,lst: list):
        try:
            leftscore=0
            rightscore=0
            gTime=0.0
            playmode="other"
            if(lst[0][0]=='sl'):
                leftscore=int(lst[0][1])
            if(lst[1][0]=='sr'):
                rightscore=int(lst[1][1])
            if(lst[2][0]=='t'):
                gTime=float(lst[2][1])
            if(lst[3][0]=='pm'):
                playmode=lst[3][1]
            return [leftscore,rightscore,gTime,playmode]
        except Exception as e:
            #print("Exception [agentParser]getTime():", e)
            return None    

    def getTime(self, lst: list):
            try:
                cTime=float(lst[0][1])
                return cTime
            except Exception as e:
                #print("Exception [agentParser]getTime():", e)
                return None
        


    def getBallVision(self, lst: list):
        distance = float(lst[0][1])
        angleH = float(lst[0][2])
        angleV = float(lst[0][3])
        value = [distance, angleH, angleV]
        return value
                

    def getFootResistance(self,  lst: list):
        x1 = float(lst[1][1])
        y1 = float(lst[1][2])
        z1 = float(lst[1][3])
        x2 = float(lst[2][1])
        y2 = float(lst[2][2])
        z2 = float(lst[2][3])
        return [[x1, y1, z1], [x2, y2, z2]]
                        

    def search(self, word: str, lst: list):
        for i in range(0,len(lst)):
            if type(lst[i]) is list:
                self.search(word, lst[i])
            elif lst[i] == word:
                print(word, '=', lst[i+1])
            continue
        return

    def getValue(self, word: str, lst: list, old):
        value = old
        for i in range(0,len(lst)):
            if value == None or value == old:
                if lst[i] == word:
                    value = lst[i+1]
                    return value
                elif type(lst[i]) is list:
                    value = self.getValue(word, lst[i], old)
                else:
                    continue
                if value == None or value == old:
                    continue
            else:
                return value
        if value is None:
            value = old
        return value