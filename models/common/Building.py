#!/usr/bin/python3

import abc
import logging
import pprint
import datetime
import random


class Building:

    __metaclass__ = abc.ABCMeta

    def __init__(self, buildingName, buildingLocation):
        self._log = logging.getLogger(__name__)
        self._buildingName = buildingName
        self._buildingLocation = buildingLocation

        # Seed PRNG (exactly once)
        random.seed()


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
        self._log.info("Starting daily activities for {0} on {1}".format(
            self.getName(), currDate.isoformat()) )
        locations = self._getBuildingLocations()
        elevatorModel = self._getElevatorModel()

        # Each actor will add him or herself to the location model upon instantiation
        actorList = self._createActorsForDay(currDate, locations)

        self._log.info(
            "\n----\n" + \
            "---- Launching Actors for {0} on {1} ----".format(
            self.getName(), currDate) + \
            "\n----" )

        dailyActivities = {}

        # Get list of scheduled activities for each actor
        for currActorName in actorList:
            self._log.info("Executing activities for {0} actor {1} on {2}".format(
                self.getName(), currActorName, currDate.isoformat()) ) 
            currActor = actorList[currActorName]
            self._log.info("Getting activities for {0}".format(currActor.getName()) )

            (timestamp, activity) = currActor.getNextPendingActivity()
            while timestamp != None:
                self._log.info("\tTime {0}: Activity: {1}".format(
                    timestamp, activity.getType()) )

                # Add to list of daily activities
                if activity.getStartTime() not in dailyActivities:
                    dailyActivities[activity.getStartTimeString()] = []

                dailyActivities[activity.getStartTimeString()].append(activity)

                (timestamp, activity) = currActor.getNextPendingActivity()

        # Pass the day's activity list to the elevator model for simulation
        elevatorModel.processBankActivityList( "Elevator Bank - Middle", dailyActivities )
        


    @abc.abstractmethod
    def _getBuildingLocations(self):
        return


    @abc.abstractmethod
    def _getElevatorModel(self):
        return


    @abc.abstractmethod
    def _createActorsForDay(self, currDate, buildingLocations):
        return

