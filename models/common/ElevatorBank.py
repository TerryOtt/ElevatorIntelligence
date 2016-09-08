#!/usr/bin/python3

import logging
import random

class ElevatorBank:
    
    def __init__(self, bankName, bankLogic, elevatorList, floorList):
        self._log = logging.getLogger(__name__)
        self._name = bankName
        self._bankLogic = bankLogic
        self._elevators = elevatorList
        self._numElevatorsInBank = len(self._elevators)
        self._floors = {}

        self._log.info("Created new elevator bank {0} with logic {1} containing {2} elevators".format(
            self.getName(), self.getBankLogicName(), self._numElevatorsInBank) )

        floorIndex = 0
        self._log.info("Floors:")
        self._floorNameLookup = []
        for currFloor in floorList:
            self._floors[currFloor] = { 
                'floorIndex': floorIndex,
                'elevatorQueueUp': [],
                'elevatorQueueDown': [],
            }

            # Reverse lookup table, floor index to name
            self._floorNameLookup.append( currFloor )

            floorIndex += 1
            self._log.info("\t{0} => floor index {1}".format(
                currFloor, self._floors[currFloor]['floorIndex']) )


        self._log.info("Elevators:")
        for currElevator in self._elevators:
            # Set random floors for the elevators in the bank
            currElevator.setFloorIndex( random.randint(0, len(self._floorNameLookup)) )

            self._log.info("\tElevator {0} initialized at floor {1}".format(
                currElevator.getName(), self._floorNameLookup[currElevator.getFloorIndex()]) )


            
    def getName(self):
        return self._name

    def getBankLogicName(self):
        return self._bankLogic.getName()
        
