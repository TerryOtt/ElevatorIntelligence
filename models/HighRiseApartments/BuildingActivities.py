#!/usr/bin/python3

import logging
from common.ScheduledActivity import ScheduledActivity
import random


class ParkCar(ScheduledActivity):

    def __init__(self, carParkTime):
        self._log = logging.getLogger(__name__)
        ScheduledActivity.__init__(self, carParkTime, carParkTime)
        self._parkingFloor = ParkCar._getRandomParkingFloor()


    def getType(self):
        return "Park Car"


    def getDescription(self):
        return "Park car on " + self.getParkingFloor()


    def getParkingFloor(self):
        return self._parkingFloor


    @staticmethod
    def _getRandomParkingFloor():
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

