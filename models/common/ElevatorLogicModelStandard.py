#!/usr/bin/python3

import logging
import abc
import models.common.ElevatorLogicModel

class ElevatorLogicModelStandard(models.common.ElevatorLogicModel.ElevatorLogicModel):
    def __init__(self):
        self._name = "Logic Model - Standard"
        self._log = logging.getLogger(__name__)

    def addActivity(self, elevatorActivity, elevatorBank):
        self._log.info("Elevator logic {0} received activity type {1} from bank {2} at {3}".format(
            self.getName(), elevatorActivity.getType(), elevatorBank.getName(),
            elevatorActivity.getStartTime()) )

        if elevatorActivity.getType() == "Request Elevator":
            self._processElevatorRequest(elevatorActivity, elevatorBank)


    def _processElevatorRequest(self, elevatorActivity, elevatorBank):
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
