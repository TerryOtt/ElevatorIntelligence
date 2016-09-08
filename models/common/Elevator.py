#!/usr/bin/python3

import logging

class Elevator:
    
    def __init__(self, elevatorLogicModel, elevatorName=None ):
        self._log = logging.getLogger(__name__)
        self._name = elevatorName
        self._logicModel = elevatorLogicModel

    def getName(self):
        return self._name

    def getLogicModelName(self):
        return self._logicModel.getName()
