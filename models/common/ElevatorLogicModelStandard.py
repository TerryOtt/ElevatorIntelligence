#!/usr/bin/python3

import logging
import abc
import models.common.ElevatorLogicModel
import datetime
import collections


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

            # Move elevators
            elevatorBank.moveActiveElevators(simulationTime, timeResolution)

            # Any activities at this point?
            if simulationTimestamp in elevatorTimeline:
                self._log.debug("{0}, found {1} activities".format(
                    simulationTimestamp, len(elevatorTimeline[simulationTimestamp])) )

                for currActivity in elevatorTimeline[simulationTimestamp]:
                    if currActivity['activity_type'] == "Request Elevator":
                        self._processElevatorRequest(currActivity, elevatorBank)

            # If all elevators are idle, warp forward in time
            if elevatorBank.allElevatorsIdle() is True:
                simulationTimestamp = sortedTimestamps.popleft()
                simulationTime = datetime.datetime.strptime( simulationTimestamp, "%Y%m%d %H%M%S" )

                self._log.info("Timewarp forward to {0}".format(simulationTime) )

            # Elevators are active, move one timeslice forward
            else:
                simulationTime += timeResolution
                simulationTimestamp = simulationTime.strftime("%Y%m%d %H%M%S")


    def _processElevatorRequest(self, elevatorActivity, elevatorBank):

        self._log.debug("Processing elevator request at {0}".format(
            elevatorActivity['activity_time']) )
        
        # Create a new person object 
        newPerson = elevatorBank.createNewRiderId()

        self._log.info("Created new rider {0}".format(newPerson))

        # Find out which queue to add them to -- note activity floor indexes and elevator floor indexes are
        #       off by one because I wanted to make life way harder than it needs to be
        startingFloorIndex = elevatorActivity['start_floor'] - 1
        
        # Are they going up or down?
        travelDirection = elevatorActivity['button_pressed']

        # Add them to appropriate elevator queue
        elevatorBank.addRiderToElevatorQueue(
            elevatorActivity['activity_time'], newPerson, startingFloorIndex, 
            travelDirection)

        # If all elevators are idle, we need to activate the one closest to us
        if elevatorBank.allElevatorsIdle() is True:
            elevatorBank.activateClosestIdleElevator(startingFloorIndex)



    def _processElevatorMovement(self, elevatorBank, simulationTime):
        pass        


