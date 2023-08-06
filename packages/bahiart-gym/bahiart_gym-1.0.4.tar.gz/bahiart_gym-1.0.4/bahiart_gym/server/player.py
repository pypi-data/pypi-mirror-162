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
from numpy.core.defchararray import array
from bahiart_gym.server.agentParser import AgentParser
from math import fabs, sqrt
import numpy as np
from multiprocessing import Lock

class Player(object):
    """ 
    This class deals with every player instantiated on proxy
    """
    """
    Perceptor Grammar:

    Grammar = (HJ (n <joint_name>) (<angle_in_degrees>))
    Example = (HJ (n raj2) (ax -15.61))

    Joint Names: https://gitlab.com/robocup-sim/SimSpark/-/wikis/Models#physical-properties
    """

    mutex=Lock()

    def pol2cart(self, mag, theta):
        x = mag * np.cos(theta)
        y = mag * np.sin(theta)
        return [x, y]

    def __init__(self, unum):

        #Parser
        self.parser = AgentParser()
        
        #Joints
        self.jointNames = ['hj1', 
                      'hj2', 
                      'llj1', 
                      'rlj1', 
                      'llj2', 
                      'rlj2', 
                      'llj3', 
                      'rlj3',
                      'llj4',
                      'rlj4', 
                      'llj5', 
                      'rlj5', 
                      'llj6', 
                      'rlj6', 
                      'laj1', 
                      'raj1', 
                      'laj2', 
                      'raj2', 
                      'laj3', 
                      'raj3', 
                      'laj4', 
                      'raj4',
                      'llj7',
                      'lrj7']
        self.joints = dict.fromkeys(self.jointNames,0.0)

        #Number/id
        self.unum = unum
        
        #Field side
        self.side=""

        #Vision Perceptor Data
        self.ballPolarPos = []

        #Standing of Fallen State
        self.isFallen = False

        #ACC / GYR
        self.acc = [0.0,]*3
        self.gyro = [0,0]*3

        #Force Perceptors
        self.lf=self.rf=self.lf1=self.rf1=[[0.0,]*3,]*2

        #Game Statistics
        self.cTime=0.0
        self.leftScore=0
        self.rightScore=0
        self.gTime=0.0
        self.playmode="other"

        self.max = 0


    def getUnum(self):
        return self.unum

    
    def getPerceptions(self):
        """
        This function returns a dict of numpy arrays with every perception from the agent.
        
        Dict Keys:
        ---
            'joints', 'acc', 'gyro',\n
            'leftFootResistance', 'leftFootResistanceToes'\n
            'rightFootResistance', 'rightFootResistanceToes'
        """
               
        perceptions = {"joints": {
            'hj1': np.array([self.joints['hj1']]),
            'hj2': np.array([self.joints['hj2']]),
            'llj1': np.array([self.joints['llj1']]),
            'rlj1': np.array([self.joints['rlj1']]),
            'llj2': np.array([self.joints['llj2']]),
            'rlj2': np.array([self.joints['rlj2']]),
            'llj3': np.array([self.joints['llj3']]),
            'rlj3': np.array([self.joints['rlj3']]),
            'llj4': np.array([self.joints['llj4']]),
            'rlj4': np.array([self.joints['rlj4']]),
            'llj5': np.array([self.joints['llj5']]),
            'rlj5': np.array([self.joints['rlj5']]),
            'llj6': np.array([self.joints['llj6']]),
            'rlj6': np.array([self.joints['rlj6']]),
            'laj1': np.array([self.joints['laj1']]),
            'raj1': np.array([self.joints['raj1']]),
            'laj2': np.array([self.joints['laj2']]),
            'raj2': np.array([self.joints['raj2']]),
            'laj3': np.array([self.joints['laj3']]),
            'raj3': np.array([self.joints['raj3']]),
            'laj4': np.array([self.joints['laj4']]),
            'raj4': np.array([self.joints['raj4']]),
            'llj7': np.array([self.joints['llj7']]),
            'lrj7': np.array([self.joints['lrj7']])
        },
            'acc': np.array(self.acc),
            'gyro': np.array(self.gyro),
            'leftFootResistance': (np.array(self.lf[0]), np.array(self.lf[1])),
            'rightFootResistance': (np.array(self.rf[0]), np.array(self.rf[1])),
            'leftFootResistanceToes': (np.array(self.lf1[0]), np.array(self.lf1[1])),
            'rightFootResistanceToes': (np.array(self.rf1[0]), np.array(self.rf1[1]))
        }
        return perceptions

    def getJointAngle(self, joint:str):
        return self.joints[joint]

    def checkFallen(self):
        
        fallen = False

        X_ACEL = self.acc[0]
        Y_ACEL = self.acc[1]
        Z_ACEL = self.acc[2]

        if((fabs(X_ACEL) > Z_ACEL or fabs(Y_ACEL) > Z_ACEL) and Z_ACEL < 5):
            if((Y_ACEL < -6.5 and Z_ACEL < 3) or (Y_ACEL > 7.5 and Z_ACEL < 3) or (fabs(X_ACEL) > 6.5)):
                fallen = True
                #print("FALLEN: " + str([X_ACEL, Y_ACEL, Z_ACEL]) + " time: " + str(self.time))
        else:
            pass
            #print("STANDING: " + str([X_ACEL, Y_ACEL, Z_ACEL]))
        
        return fallen

    
    def extractTokens(self, lst: list,):
        try:
            if type(lst[0]) is list:
                return self.extractTokens(lst[0])
            elif type(lst[0]) is str:
                return lst[0],lst[1:]
        except Exception as e:
            print("Exception in extratctTokens: ", e)
        
    def updateStats(self, agentMsg):
        
        parsedMsg=[]
        self.lf=self.rf=self.lf1=self.rf1=[[0.0,]*3,]*2
        #AGENT MSG
        if len(agentMsg) > 0:
            with self.mutex:
                parsedMsg = self.parser.parse(agentMsg)
        else:
            print("[player.updateStats] Empty agentMsg!")
        
     #   self.logfile.write(str(parsedMsg))
        
        for value in parsedMsg:
            if type(value) is list:
                value,args=self.extractTokens(value)
            # try:
            if value=='HJ':
                name,value=self.parser.getHingePos(args)
                self.joints[name]=value
            elif value=='ACC':
                self.acc=self.parser.getAcc(args)
            elif value=='GYR':
                self.gyr=self.parser.getGyr(args)
            elif value=='time':
                self.cTime=self.parser.getTime(args)
            elif value=='GS':
                gs=self.parser.getGameState(args)
                self.leftScore=gs[0]
                self.rightScore=gs[1]
                self.gTime=gs[2]
                self.playmode=gs[3]
            elif value=='FRP':
                if args[0][1]=='rf':
                    self.rf=self.parser.getFootResistance(args)
                elif args[0][1]=='lf':
                    self.lf=self.parser.getFootResistance(args)
                elif args[0][1]=='lf1':
                    self.lf1=self.parser.getFootResistance(args)
                elif args[0][1]=='lr1':
                    self.lr1=self.parser.getFootResistance(args)
            elif value=='See':
                for token in args:
                    if type(token) is list:
                        token,data=self.extractTokens(token)
                    if token == 'B':
                        self.ballPolarPos = self.parser.getBallVision(data)
            # except Exception as e:
                # print("Erro no updateStats parsing args: ", e)
        
            
            
    
        #CHECK IF PLAYER IS FALLEN
        self.isFallen = self.checkFallen()        
        
        