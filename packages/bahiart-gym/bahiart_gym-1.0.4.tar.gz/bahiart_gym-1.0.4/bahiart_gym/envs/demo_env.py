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
import gym
import numpy as np
from gym import spaces
from bahiart_gym.server.player import Player
from bahiart_gym.server.trainer import Trainer
from bahiart_gym.server.world import World
from bahiart_gym.agentcomms import AgentComms
from bahiart_gym.agentcomms import InvalidHostAndPortLengths


class DemoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    optPlayer: Player = None

    def __init__(self, monitorPort=3200):
        print("Creating World with monitorPort ",monitorPort,"\n")
        #CREATING WORLD OBJECT AND UPDATING ITS VARIABLES
        self.agents=AgentComms()   
        self.ws = World(monitorPort)
        self.command = self.ws.trainer
        self.ws.staticUpdate()
        self.ws.dynamicUpdate()

        self.episodeInitTime = None
        self.episodeInitBallX = -3.0
        self.goalsScored = 0
        self.episodeMaxTime = 40
        
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(np.array([0, 0]), np.array([60, 300])) #BallDist goes from 0 to 60. BallSpeed goes from 0 to 300.

        self.state = np.array([0.0,0.0])

        self.currentStep = 1 #USED ONLY FOR DEBUGING AT THE MOMENT.

    def step(self, action): 
        """
            Takes an action, whether to stand still, walk towards the ball or kick the ball.
        """
        self.currentStep += 1

        message = str(action)
        self.agents.sendAll(message)
        
        
        # IMPORTANT 
        # 
        # This loop can be used to wait till action has been completed and a flag has been received. 
        # In this way, the next step is only called after the previous action has been fully completed.
        # 
        # The step keeps waiting while the 'actionComplete' flag has been received. (The flag can be changed on the while loop)
        # agentMessages = {}
        # while("actionComplete" not in agentMessages.values()):
        #     self.agents.receiveAll()
        #     agentMessages = self.agents.getAgentMessages()

        # receiveAll receives the messages and stores in a dictionary
        # getAgentMessages returns the dictionary with the messages and clear it on the function call

        self.agents.receiveAll()

        self.command.reqFullState()
        self.ws.staticUpdate()
        self.ws.dynamicUpdate()

        if(self.episodeInitTime is None):
            self.episodeInitTime = self.ws.time
        

        self.ws.dynamicUpdate()
        
        obsBallDist = self.optPlayer.ballPolarPos[0]
        obsBallSpeed = self.ws.ballSpeed
        self.state = np.array([obsBallDist, obsBallSpeed])
        
        #Verify if episode is done either by scoring a goal or having passed 40 seconds since the start of the episode.
        if(self.goalsScored < self.ws.scoreLeft or (self.ws.time - self.episodeInitTime) > self.episodeMaxTime):
            done = True
            currTime = self.ws.time
            elapsedTime = currTime - self.episodeInitTime
            episodeEndBallX = self.ws.ballFinalPos[0]
            ballTravDist = episodeEndBallX - self.episodeInitBallX
            if(ballTravDist < 0.0):
                reward = ballTravDist
            elif(ballTravDist < 5.0):
                reward = ballTravDist*2
            elif(ballTravDist < 10):
                reward = ballTravDist*3
            elif(ballTravDist < 20):
                reward = ballTravDist*4
            self.episodeInitTime = None
            if(self.goalsScored < self.ws.scoreLeft):
                self.goalsScored += 1
                if(elapsedTime < 10):
                    reward = reward*10
                elif(elapsedTime < 15):
                    reward = reward*8
                elif(elapsedTime < 21):
                    reward = reward*5
            print("Elapsed Time: {} / BallTravDist: {} / Reward: {}".format(elapsedTime, ballTravDist, reward))
        else:
            reward = 0
            done = False

        info = {}

        return self.state, reward, done, info

    def reset(self):
        '''
            Resets player and ball to default positions.
            WARNING: GUARANTEE THE PLAYER IS STANDING UP BEFORE RESETING
        '''
        self.ws.staticUpdate()
        self.ws.dynamicUpdate()
        if(self.ws.playMode == 13):
            self.command.changePlayMode("PlayOn") # if playmode is GoalLeft, sets playmode to playOn
        
        #Place the ball in the center of the field
        self.command.beamBall(-3.0, 0.0, 0.0)

        #Place the Player behind the ball
        self.command.beamPlayer(self.optPlayer.getUnum(), "Left", -5.0, 0, 0.3)

        obsBallDist = self.optPlayer.ballPolarPos[0]
        obsBallSpeed = self.ws.ballSpeed
        self.state = np.array([obsBallDist, obsBallSpeed])

        return self.state

    def render(self, mode='human'): # Run roboviz or any monitor in the screen to show the training
        ...
  
    def setPlayer(self, player: Player):
        self.optPlayer = player

    def stayIdleBeforeKickOff(self):
        while True:
            self.ws.dynamicUpdate()
            if(self.ws.playMode != 0):
                break

    def close(self):
        ...
