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

class Parser(object):
    """
    Class to parse S-Expression from server
    """

    def __init__(self):
        self.mutex = Lock()

    def parse(self, string:str):       
        parsedString = []       
        with self.mutex:
            parsedString = str2sexpr(string)    
        return parsedString

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