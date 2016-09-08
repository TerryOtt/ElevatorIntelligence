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
        self._riderId = 0

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


    def processActivities(self, activitiesList):
        self._log.info("{0} processing activity list".format(
            self.getName()) )

        # Perform things in chronological order
        sortedTimestamps = sorted( activitiesList.keys() )

        for currTimestamp in sortedTimestamps:

            # Get list of activities at this time
            for currActivity in activitiesList[currTimestamp]:

                # Is it one we care about?
                if currActivity.getType() == "Request Elevator":
                    # Pass to bank logic which will call back into us with responses
                    self._bankLogic.addActivity(currActivity, self)

    def createNewRiderId(self):
        self._riderId += 1

        returnRiderId = "{0} Rider {1:06d}".format(
            self.getName(), self._riderId) 

        self._log.info("Created new rider {0}".format(returnRiderId))

        return returnRiderId


    def addRiderToElevatorQueue(self, timeEnterQueue, riderName, startingFloorIndex, travelDirection):

        if travelDirection == "UP":
            queueName = "elevatorQueueUp"
        else:
            queueName = "elevatorQueueDown"

        buildingFloorName = self._floorNameLookup[startingFloorIndex]
        buildingFloor = self._floors[ buildingFloorName ]
        buildingFloorQueue = buildingFloor[ queueName ]

        # Sanity check that they aren't in queue already
        if riderName in buildingFloorQueue:
            raise ValueError("Could not add {0} to floor {1} queue {2}, already in it!".format(
                riderName, buildingFloorName, queueName) )

        # Add to end of queue -- with time person entered
        buildingFloorQueue.append( (timeEnterQueue, riderName) )

        self._log.info("{0}: added {1} to floor {2}/{3} queue".format(
            timeEnterQueue, riderName, startingFloorIndex, travelDirection) )


        
