#!/usr/bin/python3

import logging
import abc
import models.common.ElevatorLogicModel
import datetime


class ElevatorLogicModelStandard(models.common.ElevatorLogicModel.ElevatorLogicModel):
    def __init__(self):
        self._name = "Logic Model - Standard"
        self._log = logging.getLogger(__name__)

    def simulateElevators(self, elevatorBank):
        # Get the starting timeline (just request elevator events so far)
        elevatorTimeline = elevatorBank.getElevatorTimeline()

        sortedTimestamps = sorted( elevatorTimeline.keys() )

        # Walk time through and handle events as we find them
        simulationTime = datetime.datetime.strptime( sortedTimestamps[0], "%Y%m%d %H%M%S" )

        simulationTimestamp = sortedTimestamps[0]

        # Time resolution is 1.0 second per turn
        timeResolution = 1.0

        while simulationTimestamp < sortedTimestamps[len(sortedTimestamps) - 1 ]:
            # Move elevators
            elevatorBank.moveActiveElevators(timeResolution)

            # Any activities at this point?
            if simulationTimestamp in sortedTimestamps:
                self._log.debug("{0}, found {1} activities".format(
                    simulationTimestamp, len(elevatorTimeline[simulationTimestamp])) )

                for currActivity in elevatorTimeline[simulationTimestamp]:
                    if currActivity.getType() == "Request Elevator":
                        self._processElevatorRequest(currActivity, elevatorBank)


            simulationTime += datetime.timedelta(seconds=1)
            simulationTimestamp = simulationTime.strftime("%Y%m%d %H%M%S")

    def _processElevatorRequest(self, elevatorActivity, elevatorBank):

        self._log.debug("Processing elevator request at {0}".format(
            elevatorActivity.getStartTimeString()) )
        
        # Create a new person object 
        newPerson = elevatorBank.createNewRiderId()

        self._log.info("Created new rider {0}".format(newPerson))

        # Find out which queue to add them to -- note activity floor indexes and elevator floor indexes are
        #       off by one because I wanted to make life way harder than it needs to be
        startingFloorIndex = elevatorActivity.getStartFloor() - 1
        
        # Are they going up or down?
        travelDirection = elevatorActivity.getButtonPressed()

        # Add them to appropriate elevator queue
        elevatorBank.addRiderToElevatorQueue(
            elevatorActivity.getStartTime(), newPerson, startingFloorIndex, 
            travelDirection)

        # If all elevators are idle, we need to activate the one closest to us
        if elevatorBank.allElevatorsIdle() is True:
            elevatorBank.activateClosestIdleElevator(startingFloorIndex)



    def _processElevatorMovement(self, elevatorBank, simulationTime):
        pass        


