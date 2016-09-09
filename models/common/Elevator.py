#!/usr/bin/python3

import logging
import random


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
        self._passengersByFloor = {}


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
        return (self._travelDirection == 0 and self.isLoadingEvolutionInProcess() is False)


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

        self._log.info("{0} has been set to start doors opening on next logic iteration".format(
            self.getName()) )


    def isLoadingEvolutionInProcess(self):
        return self._loadingEvolutionPhase != None


    def continueLoadingEvolution(self, simulationTime, simulationTimeslice, elevatorBank):
        secondsRemaining = simulationTimeslice.seconds

        self._log.info("{0} continuing loading evolution at {1}".format(
            self.getName(), simulationTime) )

        while abs(secondsRemaining) > 0.001 and self._loadingEvolutionPhaseTimeRemaining != None:
            timeSpent = min(secondsRemaining, self._loadingEvolutionPhaseTimeRemaining)

            self._loadingEvolutionPhaseTimeRemaining -= timeSpent
            secondsRemaining -= timeSpent

            self._log.info("{0} performed {1:4.2f} seconds of loading phase {2}, {3:4.2f} seconds remain".format(
                self.getName(), timeSpent, self._loadingEvolutionPhase, self._loadingEvolutionPhaseTimeRemaining) )

            # Did we complete the current phase
            if abs(self._loadingEvolutionPhaseTimeRemaining) < 0.001:
                self._log.info("{0} completed loading phase {1}".format(
                    self.getName(), self._loadingEvolutionPhase) )

                self._transitionToNextLoadingPhase(elevatorBank)

                # If we just switched to loading phase, hand off to 
                #       elevator to add people (which adds time     
                #       to loading phase per person)
                if self._loadingEvolutionPhase == 'Loading':
                    elevatorBank.loadPassengers(simulationTime, self)


    def _transitionToNextLoadingPhase(self, elevatorBank):
        oldPhase = self._loadingEvolutionPhase

        if self._loadingEvolutionPhase == "DoorsOpening":
            self._loadingEvolutionPhase = "Unloading"

            if self.getFloorIndex() not in self._passengersByFloor:
                self._passengersByFloor[self.getFloorIndex()] = []

            numberUnloading = len( self._passengersByFloor[self.getFloorIndex()])

            self._log.info("{0} people getting off on this floor".format(
                numberUnloading) )

            self._elevatorCurrentOccupants -= numberUnloading

            self._log.info("{0} occupants remain in elevator".format(
                self._elevatorCurrentOccupants) )

            # 1-2 seconds per person to get off elevator
            self._loadingEvolutionPhaseTimeRemaining = \
                (1.0 + random.random()) * numberUnloading

            self._passengersByFloor[self.getFloorIndex()] = []

        elif self._loadingEvolutionPhase == "Unloading":
            self._loadingEvolutionPhase = "Loading"

            # Don't set time for this phase -- this is done by elevator bank 

        elif self._loadingEvolutionPhase == "Loading":
            self._loadingEvolutionPhase = "DoorsClosing"

            self._loadingEvolutionPhaseTimeRemaining = self._doorOpenCloseTime

        elif self._loadingEvolutionPhase == "DoorsClosing":
            self._loadingEvolutionPhase = None
            self._loadingEvolutionPhaseTimeRemaining = None

        if self._loadingEvolutionPhase != None:
            self._log.info("{0} transitioned from {1} to {2}, {3:4.2f} seconds remaining".format(
                self.getName(), oldPhase, self._loadingEvolutionPhase,
                self._loadingEvolutionPhaseTimeRemaining) )
        else:
            self._log.info("{0} completed loading/unloading evolution".format(
                self.getName()) )


    def getAvailablePassengerCapacity(self):
        return self._elevatorMaxCapacity - self._elevatorCurrentOccupants


    def loadPassenger(self, simulationTimestamp, passengerId, queueTime, 
            destinationFloorIndex):

        if self.getAvailablePassengerCapacity() < 1:
            raise RuntimeError('Tried to load people onto elevator that was full')

        if destinationFloorIndex not in self._passengersByFloor:
            self._passengersByFloor[destinationFloorIndex] = []

        self._passengersByFloor[destinationFloorIndex].append(
            (simulationTimestamp, passengerId, queueTime) )

        self._elevatorCurrentOccupants += 1


    def carryingPassengersWithDestinationFloor(self, candidateFloorIndex):
        return ( candidateFloorIndex in self._passengersByFloor and
            len(self._passengersByFloor) > 0 )
