#!/usr/bin/python3

import logging
import random
import math
import pprint


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
            currElevator.setFloorIndex( random.randint(0, len(self._floorNameLookup) - 1) )

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


    def addRiderToElevatorQueue(self, timeEnterQueue, riderName, startingFloorIndex, 
            destinationFloorIndex, travelDirection):

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

        # Add to end of queue -- with time person entered and their destination floor
        buildingFloorQueue.append( (timeEnterQueue, riderName, destinationFloorIndex) )

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


    def activateClosestIdleElevator(self, simulationTimestamp, requestFloorIndex):
        self._log.info("{0} request on floor {1}, finding best idle elevator to serve".format(
            simulationTimestamp, self._floorNameLookup[requestFloorIndex]) )

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

        # May already be on target floor
        if smallestFloorDelta == 0:
            self._log.info("Dumb luck, elevator {0} was already idle at that floor")

            self.initiateElevatorLoadingEvolution(simulationTimestamp, activatingElevator)

        else:
            self._log.info("Activating elevator {0}, currently on {1}, to service request on {2}".format(
                activatingElevator.getName(), self._floorNameLookup[activatingElevator.getFloorIndex()],
                self._floorNameLookup[requestFloorIndex]) )

            if activatingElevator.floorDelta(requestFloorIndex) > 0:
                activatingElevator.setTravelDirection(1)
            else:
                activatingElevator.setTravelDirection(-1)


    def moveActiveElevators(self, simulationTime, simulationTimeslice):
        timespanInSeconds = simulationTimeslice.seconds

        for currElevator in self._elevators:
            if self._isElevatorEligibleToMove(currElevator) is True:

                self._log.info("{0}: {1} is eligible to move".format(
                    simulationTime, currElevator.getName()) )

                # Determine if we need to make a stop
                #(shouldStop, whereStop) = self._bankLogic.shouldStopToLoadUnload(currElevator,
                #    self, simulationTimeslice)

                (shouldStop, whereStop) = self._bankLogic.shouldStopToLoadUnload(currElevator,
                    self, simulationTimeslice)

                if shouldStop is True:
                    self._log.info("{0} told to stop at {1} to load or unload".format(
                        currElevator.getName(), self._floorNameLookup[whereStop]) )

                    currElevator.setFloorIndex(whereStop)

                    self.initiateElevatorLoadingEvolution(simulationTime, currElevator)
                     
                    
                else:
                    currElevator.setFloorIndex(
                        currElevator.projectFloorIndex(simulationTimeslice))
                    self._log.info("{0}: {1} moved to floor index {2:2.02f}".format(
                        simulationTime, currElevator.getName(), 
                        currElevator.getFloorIndex()) )


    def ridersQueuedOnFloor(self, floorIndex):
        return \
            len(self._floors[self._floorNameLookup[floorIndex]]['elevatorQueueUp']) > 0 or \
            len(self._floors[self._floorNameLookup[floorIndex]]['elevatorQueueDown']) > 0


    def pendingStopsFurtherAlongTravelDirection( self, currentFloor, 
            currentTravelDirection ):

        if currentTravelDirection == "UP":
            searchStartIndex = currentFloor + 1
            searchEndIndex = len(self._floors) 
        else:
            searchStartIndex = 0
            searchEndIndex = currentFloor 

        pendingStops = False

        for searchIndex in range( searchStartIndex, searchEndIndex ):
            if self.ridersQueuedOnFloor(searchIndex) is True:
                pendingsStops = True
                break

        return pendingStops


    def requestsOnThisFloorGoingCurrentDirection( self, currentFloor, 
            currentTravelDirection ):

        if currentTravelDirection == "UP":
            searchQueue = "ElevatorQueueUp"
        else:
            searchQueue = "ElevatorQueueDown"

        return len(self._floors[self._floorNameLookup[floorIndex]][searchQueue]) > 0


    def initiateElevatorLoadingEvolution(self, simulationTimestamp, elevator):

        self._log.info("{0} starting elevator loading evolution on {1}".format(
            elevator.getName(), self._floorNameLookup[elevator.getFloorIndex()]) )

        # Elevator is stopped at a floor and about to load people on, we can now
        #   tell if we need to flip direction of the elevator.  The direction
        #   of the elevator tells it what queue to pull from when loading

        buildingFloor = self._floors[self._floorNameLookup[elevator.getFloorIndex()]]
        
        # Was elevator chilling at this floor idle when button was pressed
        if elevator.getTravelDirection() == 0:
            # Set direction to first button press on this floor
            upQueueTime  = simulationTimestamp
            downWaitTime = simulationTimestamp

            if len(buildingFloor['elevatorQueueUp']) > 0:
                upQueueTime = buildingFloor['elevatorQueueUp'][0][0]

            if len(buildingFloor['elevatorQueueDown']) > 0:
                downQueueTime = buildingFloor['elevatorQueueDown'][0][0]

            # Which timestamp is smaller? Up wins ties cause... gotta do something
            if upQueueTime <= downQueueTime:
                elevator.setTravelDirection(1)
            else:
                elevator.setTravelDirection(-1)

        else:
            # If there's nobody in the queue for the current direction of travel,
            #       flip direction

            if ( elevator.getTravelDirection() == -1 and \
                    len(buildingFloor['elevatorQueueDown']) == 0):
                self._log.info("{0} flipping direction to up; nobody in down queue on this floor".format(
                    elevator.getName()) )
                elevator.setTravelDirection(1)

            elif ( elevator.getTravelDirection() == 1 and \
                    len(buildingFloor['elevatorQueueUp']) == 0):
                self._log.info("{0} flipping direction to down; nobody in up queue on this floor".format(
                    elevator.getName()) )
                elevator.setTravelDirection(-1)


        elevator.initiateLoadingEvolution()


    def _isElevatorEligibleToMove(self, elevator):

        return (elevator.isActive() is True and \
            elevator.isLoadingEvolutionInProcess() is False)


    def continueUnloadingLoadingOperations(self, simulationTime, timeResolution):
        for currElevator in self._elevators: 
            if currElevator.isLoadingEvolutionInProcess() is True:
                currElevator.continueLoadingEvolution(simulationTime, timeResolution, self)
   

    def loadPassengers(self, simulationTimestamp, elevator):
        # Which floor
        floor = self._floors[self._floorNameLookup[elevator.getFloorIndex()]]

        # Which queue to load from? Elevator direction tells us 
        if elevator.getTravelDirection() == 1:
            loadQueueName = 'elevatorQueueUp'
        elif elevator.getTravelDirection() == -1:
            loadQueueName = 'elevatorQueueDown'
        else:
            raise ValueError("Elevator travel direction should NEVER be zero when loading")

        loadQueue = floor[loadQueueName]

        # How many people can fit on the elevator?
        availableCapacity = elevator.getAvailablePassengerCapacity()

        # Load as many as the elevator can take up to queue size
        peopleBoarding = min( availableCapacity, len(loadQueue) )

        self._log.info("Loading {0} passengers from {1} onto {2}".format(
            peopleBoarding, loadQueueName, elevator.getName()) )

        for i in range(peopleBoarding):
            (queueTime, passengerId, destinationFloorIndex) = loadQueue[i]

            self._log.info("Boarding {0} with queue time {1} and destination {2} onto {3}".format(
                passengerId, queueTime, destinationFloorIndex, elevator.getName()) )

            elevator.loadPassenger(simulationTimestamp, passengerId, queueTime, destinationFloorIndex )


        # Replace the load queue with the subset that DID NOT board
        loadQueue = loadQueue[peopleBoarding:]

