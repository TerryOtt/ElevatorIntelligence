#!/usr/bin/python3

import logging

class Elevator:
    
    def __init__(self, elevatorMaxCapacity, doorOpenCloseTime, secondsPerFloor, elevatorName=None ):
        self._log = logging.getLogger(__name__)
        self._name = elevatorName
        self._floorIndex = -1
        self._travelDirection = 0
        self._elevatorMaxCapacity = elevatorMaxCapacity
        self._elevatorCurrentOccupants = 0
        self._doorOpenCloseTime = doorOpenCloseTime
        self._secondsPerFloor = secondsPerFloor


    def getName(self):
        return self._name


    def setFloorIndex(self, newFloorIndex):
        self._log.debug("Setting floor index for elevator {0} to {1:2.02f}".format(
            self.getName(), newFloorIndex) )

        self._floorIndex = newFloorIndex


    def getFloorIndex(self):
        return self._floorIndex


    def floorDelta(self, floorIndex):
        return floorIndex - self.getFloorIndex()


    def isIdle(self):
        return self._travelDirection == 0


    def isActive(self):
        return not self.isIdle()


    def getTravelDirection(self):
        return self._travelDirection


    def setTravelDirection(self, direction):
        if abs(self._travelDirection) != abs(direction):
            self._travelDirection = direction
        else:
            raise ValueException("Either tried to set direction of active elevator, or stop one that was stopped")


    def getFloorsPerSecond(self):
        return 1.0 / self._secondsPerFloor


    def projectFloorIndex(self, simulationTimeslice):

        timespanInSeconds = simulationTimeslice.seconds

        # Calculate where elevator will be in next time slice if we let it keep moving
        return self.getFloorIndex() + \
            (self.getTravelDirection() * self.getFloorsPerSecond() * timespanInSeconds)

