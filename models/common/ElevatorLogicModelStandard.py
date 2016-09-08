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

        while simulationTimestamp < sortedTimestamps[len(sortedTimestamps) - 1 ]:
            # Any activities at this point?
            if simulationTimestamp in sortedTimestamps:
                self._log.info("Found activity at {0}".format(
                    simulationTimestamp) )

            simulationTime += datetime.timedelta(seconds=1)
            simulationTimestamp = simulationTime.strftime("%Y%m%d %H%M%S")



    def _processElevatorRequest(self, elevatorRequest):
        
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

        # Record button press to record 1+ rider waiting
