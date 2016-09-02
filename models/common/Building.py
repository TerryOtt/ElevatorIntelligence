#!/usr/bin/python3

import abc
import logging
import pprint
import datetime


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


    def runModel(self, startDate, endDate):
        if endDate < startDate:
            raise ValueError('End date cannot be before start date')

        currDate = startDate
        while currDate <= endDate:
            # NOTE: each days' simulation is independent. Should be its own thread
            self._simulateDailyActivities(currDate)
            currDate += datetime.timedelta(days=1)


    def _simulateDailyActivities(self, currDate):
        locations = self._getBuildingLocations()
        elevatorModel = self._getElevatorModel()

        # Each actor will add him or herself to the location model upon instantiation
        actorList = self._createActorsForDay(currDate, locations)


    @abc.abstractmethod
    def _getBuildingLocations(self):
        return


    @abc.abstractmethod
    def _getElevatorModel(self):
        return


    @abc.abstractmethod
    def _createActorsForDay(self, currDate, buildingLocations):
        return

