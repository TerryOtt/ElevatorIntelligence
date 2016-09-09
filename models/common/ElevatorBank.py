#!/usr/bin/python3

import logging
import random
import math


class ElevatorBank:
    
    def __init__(self, bankName, bankLogic, elevatorList, floorList):
        self._log = logging.getLogger(__name__)
        self._name = bankName
        self._bankLogic = bankLogic
        self._elevators = elevatorList
        self._numElevatorsInBank = len(self._elevators)
        self._floors = {}
        self._riderId = 0
        self._elevatorActivityTimeline = {}
        self._queuedRiders = 0

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

                # If empty or doesn't have type key, ignore
                if isinstance(currActivity, dict) is False or \
                        len(currActivity.keys()) == 0 or \
                        'activity_type' not in currActivity:
                    continue

                # Is it one we care about?
                if currActivity['activity_type'] == "Request Elevator":
                    # Add to our bank's timeline of events
                    self.addEventToElevatorTimeline(currActivity)

        # Use the bank logic to process our timeline, which will call back into us for additional
        #       actions
        self._bankLogic.simulateElevators(self)


    def addEventToElevatorTimeline(self, activity):
        timestamp = activity['activity_time']

        if timestamp not in self._elevatorActivityTimeline:
            self._elevatorActivityTimeline[timestamp] = []

        # Add the event
        self._elevatorActivityTimeline[timestamp].append(activity)


    def getElevatorTimeline(self):
        return self._elevatorActivityTimeline


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

        # Increment count of total queued riders
        self._queuedRidersIncrement()

        self._log.info("{0}: added {1} to {2}/{3} queue".format(
            timeEnterQueue, riderName, self._floorNameLookup[ startingFloorIndex ], travelDirection) )


    def _queuedRidersIncrement(self):
        self._queuedRiders += 1


    def allElevatorsIdle(self):
        for currElevator in self._elevators:
            if currElevator.isIdle() is False:
                return False

        return True


    def activateClosestIdleElevator(self, requestFloorIndex):
        self._log.info("Have a request on floor {0}, activating closest idle".format(
            self._floorNameLookup[requestFloorIndex]) )

        closestElevatorIndex = len(self._elevators)
        smallestFloorDelta = len(self._floors) + 1

        for elevatorIndex in range(len(self._elevators)):
            currElevator = self._elevators[elevatorIndex]
            if currElevator.isIdle() is True and \
                    abs(currElevator.floorDelta(requestFloorIndex)) < smallestFloorDelta:
                # Record as best candidate
                closestElevatorIndex = elevatorIndex
                smallestFloorDelta = abs(currElevator.floorDelta(requestFloorIndex))

        # What's our winner?
        activatingElevator = self._elevators[closestElevatorIndex]
        self._log.info("Activating elevator {0}, currently on {1}, to service request on {2}".format(
            activatingElevator.getName(), self._floorNameLookup[activatingElevator.getFloorIndex()],
            self._floorNameLookup[requestFloorIndex]) )

        if activatingElevator.floorDelta(requestFloorIndex) > 0:
            activatingElevator.setTravelDirection(1)
        else:
            activatingElevator.setTravelDirection(-1)

    def moveActiveElevators(self, timespanInSeconds):
        self._log.info("Moving active elevators distance they can cover in {0} seconds".format(
            timespanInSeconds) )

        for currElevator in self._elevators:
            if currElevator.isActive() is True:

                self._log.info("{0} is active".format(
                    currElevator.getName()) )

                # Get current floor number
                currentFloorIndex = currElevator.getFloorIndex()

                # Calculate where elevator will be in next time slice if we let it keep moving
                projectedFloorIndex = currentFloorIndex + \
                    (currElevator.getTravelDirection() * \
                    currElevator.getFloorsPerSecond() * timespanInSeconds)

                self._log.info("{0} will be moving from floor index {1:2.02f} to {2:2.02f} in {3} seconds".format(
                    currElevator.getName(), currentFloorIndex, projectedFloorIndex, 
                    timespanInSeconds) )

                # Would the elevator cross a floor with a pending request they can service?
                integerCurrentIndex = math.trunc(currentFloorIndex)
                integerProjectedIndex = math.trunc(projectedFloorIndex)
                checkFloorQueue = None
                if integerProjectedIndex > integerCurrentIndex:
                    queueCheckName = 'elevatorQueueUp'
                    checkFloorQueue = integerProjectedIndex
                elif integerProjectedIndex < integerCurrentIndex:
                    queueCheckName = 'elevatorQueueDown'
                    checkFloorQueue = integerCurrentIndex

                if checkFloorQueue != None:
                    self._log.info("{0} crosses floor {1}, checking queue {2}".format(
                        currElevator.getName(), checkFloorQueue, queueCheckName) )

                    if ( len(self._floors[self._floorNameLookup[checkFloorQueue]][queueCheckName]) > 0 ):
                        self._log.info("{0} stopping at floor {1} to service request!".format(
                            currElevator.getName(), checkFloorQueue) )
                        currElevator.setFloorIndex(checkFloorQueue)
                        currElevator.setTravelDirection(0)
                    else:
                        # Keep moving!
                        currElevator.setFloorIndex(projectedFloorIndex)

                else:
                    # Keep moving!
                    currElevator.setFloorIndex(projectedFloorIndex)
