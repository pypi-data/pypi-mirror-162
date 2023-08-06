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
from math import sqrt
from bahiart_gym.server.comms import Comms
from bahiart_gym.server.singleton import Singleton
from bahiart_gym.server.trainer import Trainer

class World(metaclass=Singleton):
    
    
    
    
    def __init__(self,monitorPort=3200):
        
        print("Creating Comms with monitorPort ",monitorPort,"\n")
        #Network Connection
        self.net = Comms(port=monitorPort)
        self.parser = self.net.serverParser
        self.trainer = Trainer(self.net)
        
        #DYNAMIC
        self.time = 0.0
        self.playMode = 0
        self.scoreLeft = 0
        self.scoreRight = 0
        self.teamLeftName = None
        self.teamRightName = None
        
        #PLAYER
        self.playersLeft = {}
        self.playersRight = {}
        self.playersLeftIndex = [0]*12
        self.playersRightIndex = [0]*12
        self.connectedPlayers = 0

        #STATIC
        self.fieldLength = 0.0
        self.fieldHeight = 0.0
        self.fieldwidth = 0.0
        self.goalWidth = 0.0
        self.goalDepth = 0.0
        self.goalHeight = 0.0

        #BALL
        self.ballRadius = 0.0
        self.ballMass = 0.0
        self.ballIndex = 0

        #BALL SPEED
        self.ballFinalPos = []
        self.ballInitPos = []
        self.ballSpeed = 0
        self.ballInitTime = 0

        #PRIVATE
        self.__count = 0
        self.__playerLeftNode = []
        self.__playerLeftGraph = []
        self.__playerLeftPos = []
        self.__playerRightNode = []
        self.__playerRightGraph = []
        self.__playerRightPos = []
        self.__ballNode = []
        self.__ballGraph = []
        self.__serverExpLength = 0
    
    def dynamicUpdate(self):
        
        serverExp = []
        try:
            self.net.updateSExp()
            serverExp = self.net.serverExp            
        except Exception as e:
            pass
            # print("-----SERVER S-EXPRESSION UPDATE ERROR-----:")
            # print(e)

        try:
            if(len(serverExp[2]) != self.__serverExpLength):
                self.playersLeftIndex = [0]*12
                self.playersRightIndex = [0]*12
                self.connectedPlayers = 0
                self.staticUpdate()
        except Exception as e:
            pass
            # print("-----STATIC UPDATE AFTER LENGTH CHANGE ERROR-----:")
            # print(e) 
        
        #ENVIRONMENT
        try:
            for value in serverExp[0]:
                if type(value) is list:
                    value,args=self.extractTokens(value)
                
                if value=='time':
                    self.time = float(args[0])
                elif value=='play_mode':
                    self.playMode = int(args[0])
                elif value=='score_left':
                    self.scoreLeft = int(args[0])
                elif value=='score_right':
                    self.scoreRight = int(args[0])
                elif value=='team_left':
                    self.teamLeftName = (args[0])
                elif value=='team_right':
                    self.teamRightName = (args[0])
        except Exception as e:
            pass
            # print("-----ENVIRONMENT EXCEPTION-----")
            # print(e)

        #BALLPOS
        try:
            self.__ballNode = self.parser.getObjNd(serverExp, self.ballIndex)
            self.__ballGraph = self.parser.getObjGraph(self.__ballNode, self.__ballGraph)
            self.ballFinalPos = self.parser.getObjPos(self.__ballGraph, self.ballFinalPos)       
        except Exception as e:
            pass
            # print("-----BALL POS EXCEPTION-----:")
            # print(e)

        #PLAYERS POSITIONS
        try:
            self.updatePlayersDict(serverExp)
        except Exception as e:
            pass
            # print("-----PLAYERS POS EXCEPTION-----:")
            # print(e)

        #BALL SPEED
        try:
            if(self.__count == 0):
                self.ballInitPos = self.ballFinalPos
                self.ballInitTime = self.time
            if(self.__count == 9):
                if(len(self.ballInitPos) > 0):
                    self.ballSpeed = sqrt(((self.ballFinalPos[0] - self.ballInitPos[0])**2) + ((self.ballFinalPos[1] - self.ballInitPos[1])**2)) / (self.time - self.ballInitTime)
                self.__count = -1
            self.__count = self.__count + 1
        except Exception as e:
            pass
            # print("------EXCEPTION SPEED---------")
            # print(e)
            # print("---------END EXCEPTION-------")
    
    def staticUpdate(self):
        serverExp = []
        self.trainer.reqFullState()
        self.net.updateSExp()
        serverExp = self.net.serverExp
        self.__serverExpLength = len(serverExp[2])
        
        while(self.ballIndex is 0):    
            try:
                self.trainer.reqFullState()
                self.net.updateSExp()
                serverExp = self.net.serverExp
                self.ballIndex = self.parser.getObjIndex("models/soccerball.obj", serverExp, self.ballIndex, self.__ballNode) #The ball should be initiated along with the server so if the ball is up, everything else should be ready as well.
            except Exception as e:
                pass
                # print("-----BALL INDEX EXCEPTION-----:")
                # print(e)
        
        while(self.__serverExpLength > 36 and self.connectedPlayers == 0):
            try:
                self.trainer.reqFullState()
                self.net.updateSExp()
                serverExp = self.net.serverExp
                self.updatePlayersIndex(serverExp)
            except Exception as e:
                pass
                # print("-----PLAYER INDEX LOOP EXCEPTION-----:")
                # print(e)

        try:
            self.ballIndex = self.parser.getObjIndex("models/soccerball.obj", serverExp, self.ballIndex) #The ball should be initiated along with the server so if the ball is up, everything else should be ready as well.
        except Exception as e:
            pass
            # print("-----BALL INDEX 2 EXCEPTION-----:")
            # print(e)

        #FIELD AND BALL
        try:
            for value in serverExp[0]:
                if type(value) is list:
                    value,args=self.extractTokens(value)
                
                if value=='FieldLength':
                    self.fieldLength = float(args[0])
                elif value=='FieldHeight':
                    self.fieldHeight = float(args[0])
                elif value=='FieldWidth':
                    self.fieldwidth = float(args[0])
                elif value=='GoalWidth':
                    self.goalWidth = float(args[0])
                elif value=='GoalDepth':
                    self.goalDepth = float(args[0])
                elif value=='GoalHeight':
                    self.goalHeight = float(args[0])
                elif value=='BallRadius':
                    self.ballRadius = float(args[0])
                elif value=='BallMass':
                    self.ballMass = float(args[0])
        except Exception as e:
            pass
            # print("-----FIELD/BALL EXCEPTION-----")
            # print(e)

        try:
            #PLAYERS POSITIONS
            self.updatePlayersIndex(serverExp)
        except Exception as e:
            pass
            # print("-----PLAYER INDEX ERROR-----")
            # print(e)
    
    def updatePlayersIndex(self, serverExp):
        playerLeft = 0
        playerRight = 0

        for i in range(0, 12):
            playerLeft, playerRight = self.parser.getObjIndex("matNum{}".format(i), serverExp, self.playersLeftIndex[i], self.playersRightIndex[i], True)
            if(playerLeft != self.playersLeftIndex[i]):
                self.playersLeftIndex[i] = playerLeft
                self.connectedPlayers += 1
            
            if(playerRight != self.playersRightIndex[i]):
                self.playersRightIndex[i] = playerRight
                self.connectedPlayers += 1


    def updatePlayersDict(self, serverExp):

        for i in range(1, 12):
            if(self.playersLeftIndex[i] != 0):
                self.__playerLeftNode = self.parser.getObjNd(serverExp, self.playersLeftIndex[i])
                self.__playerLeftGraph = self.parser.getObjGraph(self.__playerLeftNode, self.__playerLeftGraph)
                self.__playerLeftPos = self.parser.getObjPos(self.__playerLeftGraph, self.__playerLeftPos)
                self.playersLeft[i] = self.__playerLeftPos.copy()
            elif(i in self.playersLeft.keys()):
                del self.playersLeft[i]
                
            
            if(self.playersRightIndex[i] != 0):
                self.__playerRightNode = self.parser.getObjNd(serverExp, self.playersRightIndex[i])
                self.__playerRightGraph = self.parser.getObjGraph(self.__playerRightNode, self.__playerRightGraph)
                self.__playerRightPos = self.parser.getObjPos(self.__playerRightGraph, self.__playerRightPos)
                self.playersRight[i] = self.__playerRightPos.copy()
            elif(i in self.playersRight.keys()):
                del self.playersRight[i]

    def extractTokens(self, lst: list,):
        try:
            if type(lst[0]) is list:
                return self.extractTokens(lst[0])
            elif type(lst[0]) is str:
                return lst[0],lst[1:]
        except Exception as e:
            print("Exception in extratctTokens: ", e)