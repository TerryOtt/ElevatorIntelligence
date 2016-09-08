#!/usr/bin/python3

import logging

class ElevatorBank:
    
    def __init__(self, bankName, elevators, floorList):
        self._log = logging.getLogger(__name__)
        self._name = bankName
        self._elevators = elevators
        self._numElevatorsInBank = len(self._elevators)
        self._floors = {}

        self._log.info("Created new elevator bank {0} containing {1} elevators".format(
            self.getName(), self._numElevatorsInBank) )
        for currElevator in self._elevators:
            self._log.info("\tElevator: {0} with logic model {1}".format(
                currElevator.getName(), currElevator.getLogicModelName()) )

        floorIndex = 0
        self._log.info("Floors:")
        for currFloor in floorList:
            self._floors[currFloor] = floorIndex
            floorIndex += 1
            self._log.info("\t{0} => floor index {1}".format(
                currFloor, self._floors[currFloor]) )

            
    def getName(self):
        return self._name
        
