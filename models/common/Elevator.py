#!/usr/bin/python3

import logging

class Elevator:
    
    def __init__(self, elevatorName=None ):
        self._log = logging.getLogger(__name__)
        self._name = elevatorName
        self._floorIndex = -1

    def getName(self):
        return self._name

    def setFloorIndex(self, newFloorIndex):
        self._log.debug("Setting floor index for elevator {0} to {1}".format(
            self.getName(), newFloorIndex) )

        self._floorIndex = newFloorIndex

    def getFloorIndex(self):
        return self._floorIndex
