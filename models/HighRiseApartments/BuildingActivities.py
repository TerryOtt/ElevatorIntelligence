#!/usr/bin/python3

import logging
from models.common.ScheduledActivity import ScheduledActivity
import random
import datetime


class ParkCar(ScheduledActivity):

    def __init__(self, carParkTime):
        ScheduledActivity.__init__(self, carParkTime, carParkTime)
        self._parkingFloor = ParkCar.getRandomParkingFloor()


    def getType(self):
        return "Park Car"


    def getDescription(self):
        return "Park car on " + self.getParkingFloor()


    def getParkingFloor(self):
        return self._parkingFloor


    @staticmethod
    def getRandomParkingFloor():
        # In this building, floors 2 and 1 are more heavily used than floor G
        #
        # 30% park on floor 2
        # 45% park on floor 1
        # 25% park on floor G
        randomValue = random.random()

        if randomValue < 0.25:
            return "Floor G"
        elif randomValue < 0.25 + 0.45:
            return "Floor 1"
        else:
            return "Floor 2"


class RequestElevator(ScheduledActivity):

    def __init__(self, buttonPressTime, startFloorIndex, destinationFloorIndex):
        ScheduledActivity.__init__(self, buttonPressTime, buttonPressTime)
        self._startFloorIndex = startFloorIndex
        self._destinationFloorIndex = destinationFloorIndex
        
        floorDelta = destinationFloorIndex - startFloorIndex
        if floorDelta > 0:
            self._buttonPressed = "UP"
        else:
            self._buttonPressed = "DOWN"


    def getType(self):
        return "Request Elevator"


    def getDescription(self):
        return "Pressed {1} button to go from floor index {0} to floor index {2}".format(
            self._startFloorIndex, self._buttonPressed, self._destinationFloorIndex)
        

    def getStartFloor(self):
        return self._startFloorIndex


    def getDestinationFloor(self):
        return self._destinationFloorIndex


    def getButtonPressed(self):
        return self._buttonPressed


    def getJsonDictionary(self):
        return {
            'activity_time':        self.getStartTimeString(),
            'activity_type':        self.getType(),
            'button_pressed':       self.getButtonPressed(),
            'start_floor':          self.getStartFloor(),
            'destination_floor':    self.getDestinationFloor(),
        }
            
