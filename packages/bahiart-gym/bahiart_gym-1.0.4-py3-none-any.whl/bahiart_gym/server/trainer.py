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
from bahiart_gym.server.comms import Comms
from bahiart_gym.server.singleton import Singleton

class Trainer(metaclass=Singleton):
    """
    Sends comands to the server as a Trainer program.

    Example:

    # Builds the message
        msg = "(playMode " + playmode + ")"                              

    # Get message length and translate using "Host To Network Long" method. 
        msgLen = socket.htonl(len(msg))                                 
    
    # Converts integer size to bytes in the format 'little', 
    # in the same way it's returned from the server.
        prefix = msgLen.to_bytes(4, 'little')                           

    # Concatenates the prefix with the message,
    # turning the prefix into string(with 'utf-8' encode),
    # avoiding duplication of "b" in byte messages.
        fullmsg = str(prefix, "utf-8") + msg                            

    # Encodes the message and sends it through TCP socket 
        self.socket.send(fullmsg.encode())

    """

    def __init__(self,monitorPort=3200):
        self.net = Comms(port=monitorPort)

    def changePlayMode(self, playmode: str):
        
        msg = "(playMode " + playmode + ")"                              
        self.net.send(msg)

    def beamBall(self, x, y, z):
        msg = "(ball (pos " + str(x) + " " + str(y) + " " + str(z) + "))"
        self.net.send(msg)

    def beamPlayer(self, unum, team, x, y, z=0.3):
        msg = "(agent (unum " + str(unum) + ")(team " + team + ")(pos " + str(x) + " " + str(y) + " " + str(z) + "))"
        self.net.send(msg)

    def reqFullState(self):
        msg = "(reqfullstate)"
        self.net.send(msg)