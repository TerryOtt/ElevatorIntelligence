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


    def runModel(self, startDate, endDate):
        if endDate < startDate:
            raise ValueError('End date cannot be before start date')

        for currDate in range(startDate, endDate):
            # NOTE: each days' simulation is independent. Should be its own thread
            _simulateDailyActivities(self, currDate)


    def _simulateDailyActivities(self, currDate):
        floors = _getBuildingFloors(self)
        elevatorModel = _getElevatorModel(self)
        actorList = _getActorsForDay(self, currDate)

        # Add each actor to their starting position
        for currActor in actorList:
            
        
            
    @abc.abstractmethod
    def _getElevatorModel(self):
        return


    @abc.abstractmethod
    def _createActorsForDay(self):
        return
