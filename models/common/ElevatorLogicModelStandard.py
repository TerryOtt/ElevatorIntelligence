#!/usr/bin/python3

import logging
import abc
import models.common.ElevatorLogicModel
import datetime
import collections
import math


class ElevatorLogicModelStandard(models.common.ElevatorLogicModel.ElevatorLogicModel):
    def __init__(self):
        self._name = "Logic Model - Standard"
        self._log = logging.getLogger(__name__)

    def simulateElevators(self, elevatorBank):
        # Get the starting timeline (just request elevator events so far)
        elevatorTimeline = elevatorBank.getElevatorTimeline()

        sortedTimestamps = collections.deque( sorted(elevatorTimeline.keys()) )

        # Time resolution is one second per turn -- NOTE! has to be an even number of seconds
        timeResolution = datetime.timedelta(seconds=1)

        # Start with first event of the list
        simulationTimestamp = sortedTimestamps.popleft()
        simulationTime = datetime.datetime.strptime( simulationTimestamp, "%Y%m%d %H%M%S" )


        while len(sortedTimestamps) > 0:

            # Move elevators that are eligible
            elevatorBank.moveActiveElevators(simulationTime, timeResolution)

            # Make progress on unloading/loading operations underway, if any
            elevatorBank.continueUnloadingLoadingOperations(simulationTime, timeResolution)

            # Any activities at this point?
            if simulationTimestamp in elevatorTimeline:
                self._log.debug("{0}, found {1} activities".format(
                    simulationTimestamp, len(elevatorTimeline[simulationTimestamp])) )

                for currActivity in elevatorTimeline[simulationTimestamp]:
                    if currActivity['activity_type'] == "Request Elevator":
                        self._processElevatorRequest(simulationTimestamp, currActivity, elevatorBank)

            # If all elevators are idle, warp forward in time
            if elevatorBank.allElevatorsIdle() is True:
                simulationTimestamp = sortedTimestamps.popleft()
                simulationTime = datetime.datetime.strptime( simulationTimestamp, "%Y%m%d %H%M%S" )

                self._log.info("Timewarp forward to {0}".format(simulationTime) )

            # Elevators are active, move one timeslice forward
            else:
                simulationTime += timeResolution
                simulationTimestamp = simulationTime.strftime("%Y%m%d %H%M%S")


    def _processElevatorRequest(self, simulationTimestamp, elevatorActivity, elevatorBank):

        self._log.debug("Processing elevator request at {0}".format(
            elevatorActivity['activity_time']) )
        
        # Create a new person object 
        newPerson = elevatorBank.createNewRiderId()

        self._log.info("Created new rider {0}".format(newPerson))

        # Find out which queue to add them to -- note activity floor indexes and elevator floor indexes are
        #       off by one because I wanted to make life way harder than it needs to be
        startingFloorIndex = elevatorActivity['start_floor'] - 1

        # Find destination floor cause that matters too -- yup, off by one
        destinationFloorIndex = elevatorActivity['destination_floor'] - 1
        
        # Are they going up or down?
        travelDirection = elevatorActivity['button_pressed']

        # Add them to appropriate elevator queue
        elevatorBank.addRiderToElevatorQueue(
            elevatorActivity['activity_time'], newPerson, startingFloorIndex, 
            destinationFloorIndex, travelDirection)

        # If all elevators are idle, we need to activate the one closest to us
        if elevatorBank.allElevatorsIdle() is True:
            elevatorBank.activateClosestIdleElevator(simulationTimestamp, startingFloorIndex)


    def shouldStopToLoadUnload(self, elevator, elevatorBank, simulationTimeslice):

        timespanInSeconds = simulationTimeslice.seconds

        # Get current floor number
        currentFloorIndex = elevator.getFloorIndex()

        # Calculate where elevator will be in next time slice if we let it keep moving
        projectedFloorIndex = elevator.projectFloorIndex(simulationTimeslice)

        self._log.info("{0} will be moving from floor index {1:2.02f} to {2:2.02f} in {3} seconds".format(
            elevator.getName(), currentFloorIndex, projectedFloorIndex,
            timespanInSeconds) )

        # Would the elevator cross a floor that has a pending request or they have a passenger 
        #       who wants out there?
        (crossesFloorIndex, crossesFloorDirection) = self._calculateCrossedFloor(
            currentFloorIndex, projectedFloorIndex)

        if crossesFloorIndex != None: 
          
            # If elevator has riders who want off at this floor, it's a no brainer
            if elevator.carryingPassengersWithDestinationFloor(crossesFloorIndex):
                self._log.info("{0} is stopping at floor index {1} to offload passengers".format(
                    elevator.getName(), crossesFloorIndex) )

                return (True, crossesFloorIndex)

            if elevatorBank.ridersQueuedOnFloor(crossesFloorIndex) and \
                    self._meetsStopCriteria(crossesFloorIndex, 
                        crossesFloorDirection, elevator, 
                        elevatorBank) is True:

                self._log.info("{0} stopping at floor index {1} due to matching criteria".format(
                    elevator.getName(), crossesFloorIndex) )

                return (True, crossesFloorIndex)

        # Definitely don't stop
        return (False, None)



    def _meetsStopCriteria(self, candidateFloor, travelDirection, 
        elevator, elevatorBank):

        # Known true:
        #
        #   Request pending on this floor
        #
        # Times we will stop for loading/unloading at current 
        #
        #   1. No more requests pending beyond this floor in current direction of travel
        #   2. There are riders queued at current floor who want to go in the current 
        #       direction of travel

        meetsStopCriteria = False

        # Handle case 1
        if elevatorBank.pendingStopsFurtherAlongTravelDirection( candidateFloor, 
                travelDirection) is False:

            self._log.info("Potential stop at floor {0} meets 'no further stops in {1} dir'".format(
                candidateFloor, travelDirection) )

            meetsStopCriteria = True

        # Handle case 2
        elif elevatorBank.requestsOnThisFloorGoingCurrentDirection( candidateFloor,
                travelDirection) is True:

            self._log.info("Potential stop at floor {0} meets 'people queued going {1}' criteria".format(
                candidateFloor, travelDirection) )

            meetsStopCriteria = True

        return meetsStopCriteria


    def _calculateCrossedFloor(self, currentFloorIndex, projectedFloorIndex):

        # Would the elevator cross a floor with a pending request they can service?
        integerCurrentIndex = math.trunc(currentFloorIndex)
        integerProjectedIndex = math.trunc(projectedFloorIndex)
        crossesFloorIndex = None
        crossesFloorDirection = None

        # ***NOTE*** this logic assumes you can only cross ONE FLOOR PER TIMESLICE
        #       If there's ever an elevator that can move more than one floor per
        #       timeslice, need to adjust logic accordingly

        # Do we cross a floor going up?
        if integerProjectedIndex   > integerCurrentIndex:
            crossesFloorIndex = integerProjectedIndex
            crossesFloorDirection = "UP"

        # Do we cross it going down?
        elif integerProjectedIndex < integerCurrentIndex:
            crossesFloorIndex = integerCurrentIndex
            crossesFloorDirection = "DOWN"

        return (crossesFloorIndex, crossesFloorDirection)
