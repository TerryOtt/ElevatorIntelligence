#!/usr/bin/python3

import logging

class Elevator:
    
    def __init__(self, elevatorMaxCapacity, doorOpenCloseTime, secondsPerFloor, elevatorName=None ):
        self._log = logging.getLogger(__name__)
        self._name = elevatorName
        self._floorIndex = -1
        self._travelDirection = 0
        self._elevatorMaxCapacity = elevatorMaxCapacity
        self._elevatorCurrentOccupants = 0
        self._doorOpenCloseTime = doorOpenCloseTime
        self._secondsPerFloor = secondsPerFloor
        self._loadingEvolutionPhase = None
        self._loadingEvolutionPhaseTimeRemaining = None


    def getName(self):
        return self._name


    def setFloorIndex(self, newFloorIndex):
        self._log.debug("Setting floor index for elevator {0} to {1:2.02f}".format(
            self.getName(), newFloorIndex) )

        self._floorIndex = newFloorIndex


    def getFloorIndex(self):
        return self._floorIndex


    def floorDelta(self, floorIndex):
        return floorIndex - self.getFloorIndex()


    def isIdle(self):
        return self._travelDirection == 0


    def isActive(self):
        return not self.isIdle()


    def getTravelDirection(self):
        return self._travelDirection


    def setTravelDirection(self, direction):
        if abs(self._travelDirection) != abs(direction):
            self._travelDirection = direction
        else:
            raise ValueException("Either tried to set direction of active elevator, or stop one that was stopped")


    def getFloorsPerSecond(self):
        return 1.0 / self._secondsPerFloor


    def projectFloorIndex(self, simulationTimeslice):

        timespanInSeconds = simulationTimeslice.seconds

        # Calculate where elevator will be in next time slice if we let it keep moving
        return self.getFloorIndex() + \
            (self.getTravelDirection() * self.getFloorsPerSecond() * timespanInSeconds)


    def initiateLoadingEvolution(self):
        # Mark that next step is wait for doors to open, but they haven't started yet
        self._loadingEvolutionPhase = "DoorsOpening"
        self._loadingEvolutionPhaseTimeRemaining = self._doorOpenCloseTime

        self._log.info("{0} has been set to start doors opening on next logic iteration")


    def isLoadingEvolutionInProcess(self):
        return self._loadingEvolutionPhase != None


    def continueLoadingEvolution(self, simulationTimeslice, elevatorBank):
        secondsRemaining = simulationTimeslice.seconds

        while abs(secondsRemaining) > 0.001:
            timeSpent = min(secondsRemaining, self._loadingEvolutionPhaseTimeRemaining)

            self._loadingEvolutionPhaseTimeRemaining -= timeSpent
            secondsRemaining -= timeSpent

            self._log.info("{0} performed {1} seconds of loading phase {2}, {3} seconds remain".format(
                self.getName(), timeSpent, self._loadingEvolutionPhase, self._loadingEvolutionPhaseTimeRemaining) )

            # Did we complete the current phase
            if abs(self._loadingEvolutionPhaseTimeRemaining) < 0.001:
                self._log.info("{0} completed loading phase {1}".format(
                    self.getName(), self._loadingEvolutionPhase) )

                self._transitionToNextLoadingPhase(elevatorBank)

                # TODO: if this was boarding phase, need to update queues and update queue wait stats
                if self._loadingEvolutionPhase == 'Loading':
                    pass

                self._transitionToNextLoadingPhase()

    def _transitionToNextLoadingPhase(self, elevatorBank):
        oldPhase = self._loadingEvolutionPhase

        if self._loadingEvolutionPhase == "DoorsOpening":
            self._loadingEvolutionPhase = "Unloading"

            # TODO: this needs to be based on number of people getting off on this floor
            self._loadingEvolutionPhaseTimeRemaining = random.random() * 15.0

        elif self._loadingEvolutionPhase == "Unloading":
            self._loadingEvolutionPhase = "Loading"

            # TODO: this needs to be based on number of people getting on elevator
            self._loadingEvolutionPhaseTimeRemaining = random.random() * 15.0

        elif self._loadingEvolutionPhase == "Loading":
            self._loadingEvolutionPhase = "DoorsClosing"

            # TODO: this needs to be based on number of people boarding
            self._loadingEvolutionPhaseTimeRemaining = self._doorOpenCloseTime

        elif self._loadingEvolutionPhase == "DoorsClosing":
            self._loadingEvolutionPhase = None
            self._loadingEvolutionPhaseTimeRemaining = None

        self._log.info("{0} transitioned from {1} to {2}, {3} seconds remaining".format(
            self.getName(), oldPhase, self._loadingEvolutionPhase,
            self._loadingEvolutionPhaseTimeRemaining) )
