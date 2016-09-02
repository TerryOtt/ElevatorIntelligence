#!/usr/bin/python3

import abc
import logging

class Building:

    __metaclass__ = abc.ABCMeta

    def __init__(self, buildingName, buildingLocation):
        self._log = logging.getLogger(__name__)
        self._buildingName = buildingName
        self._buildingLocation = buildingLocation


    def getName(self):
        return self._buildingName


    def getLocation(self):
        return self._buildingLocation


    def runModel(self, startDate, endDate, knownLocations):
        if endDate < startDate:
            raise ValueError('End date cannot be before start date')

        for currDate in range(startDate, endDate):
            # NOTE: each days' simulation is independent. Should be its own thread
            _simulateDailyActivities(self, currDate)


    def _simulateDailyActivities(self, currDate):
        locations = _getBuildingLocations(self)
        elevatorModel = _getElevatorModel(self)

        # Each actor will add him or herself to the location model upon instantiation
        actorList = _createActorsForDay(self, currDate, locations)


    @abc.abstractmethod
    def _getBuildingLocations(self):
        return


    @abc.abstractmethod
    def _getElevatorModel(self):
        return


    @abc.abstractmethod
    def _createActorsForDay(self, currDate, buildingLocations):
        return

