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
import os
import subprocess
import time
from bahiart_gym.terminate import killEnv




def startEnv():
    
    proxyPort=3800
    serverPort=3100
    monitorPort=3200
    #Reading config.ini in current working directory
    cfgfile=open("config.ini","r")
    options=cfgfile.readlines()
    cfgfile.close()
 
    
    for opt in options:
        optsplit = opt.split("=")
        if(optsplit[0]=='TRAINING_COMMAND'):
            trainingCommand=optsplit[1].split("\n")[0].split(" ")
        elif(optsplit[0]=="TEAM_COMMAND"):
            teamCommand=optsplit[1].split("\n")[0]
        elif(optsplit[0]=="TEAM_FOLDER"):
            teamFolder=optsplit[1].split("\n")[0]
        elif(optsplit[0]=="PROXY_PORT"):
            proxyPort=int(optsplit[1].split("\n")[0])
        elif(optsplit[0]=="SERVER_PORT"):
            serverPort=int(optsplit[1].split("\n")[0])
        elif(optsplit[0]=="MONITOR_PORT"):
            monitorPort=int(optsplit[1].split("\n")[0])
    
    trainingCommand.append(str(proxyPort))
    trainingCommand.append(str(serverPort))
    trainingCommand.append(str(monitorPort))
     
    
    serverCommand = "rcssserver3d"
    
    serverProcess = subprocess.Popen(serverCommand)
    
    time.sleep(6)
    
    trainingProcess = subprocess.Popen(trainingCommand)
    
    
    proxyAvailable=False
      
    while not proxyAvailable:
        try:
            output=subprocess.check_output("lsof -i:"+str(proxyPort), shell=True)
            proxyAvailable=True
        except subprocess.CalledProcessError:
            pass

    
    cwd = os.getcwd()
    os.chdir(teamFolder)
    teamProcess = subprocess.Popen(teamCommand,cwd=teamFolder, shell=True)
    os.chdir(cwd)
    
    return serverProcess.pid, trainingProcess.pid, teamProcess.pid
    
    
#Main Function

if __name__ == '__main__':
    p1, p2, p3= startEnv()
    time.sleep(30)
    killEnv(p1,p2,p3)
    
    
   