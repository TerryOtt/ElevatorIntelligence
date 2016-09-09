#!/usr/bin/python3

import abc
import logging
import pprint
import datetime
import random
import json


class Building:

    __metaclass__ = abc.ABCMeta

    def __init__(self, buildingName, buildingLocation):
        self._log = logging.getLogger(__name__)
        self._buildingName = buildingName
        self._buildingLocation = buildingLocation

        # Seed once and only once
        random.seed()


    def getName(self):
        return self._buildingName


    def getLocation(self):
        return self._buildingLocation


    def generateActivityJsonFile(self, startDate, endDate, jsonFilename):
        if endDate < startDate:
            raise ValueError('End date cannot be before start date')

        fullActivityList = {}

        currDate = startDate
        while currDate <= endDate:
            # NOTE: each days' simulation is independent. Should be its own thread
            todaysActivities = self._scheduleDailyActivities(currDate)
            currDate += datetime.timedelta(days=1)

            # Merge into master activitylist
            fullActivityList = { **fullActivityList, **todaysActivities }

        # Write JSON to disk
        with open( jsonFilename, 'w' ) as jsonFile:
            json.dump(fullActivityList, jsonFile, sort_keys=True, indent=4 )

        self._log.info("Activity list for {0} from {1}-{2} written to {3}".format(
            self.getName(), startDate, endDate, jsonFilename) )


    def _scheduleDailyActivities(self, currDate):
        self._log.info("Starting daily activities for {0} on {1}".format(
            self.getName(), currDate.isoformat()) )
        locations = self._getBuildingLocations()
        elevatorModel = self._getElevatorModel()

        # Each actor will add him or herself to the location model upon instantiation
        actorList = self._createActorsForDay(currDate, locations)

        self._log.info(
            "\n----\n" + \
            "---- Creating activities for {0} on {1} ----".format(
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

                dailyActivities[activity.getStartTimeString()].append(activity.getJsonDictionary())

                (timestamp, activity) = currActor.getNextPendingActivity()

        return dailyActivities


    def simulateElevators(self, bankName, bankActivitiesJson, statsFile):
        statistics = self._getElevatorModel().processBankActivityList( bankName, bankActivitiesJson )     

        with open( statsFile, 'w' ) as statsHandle:
            json.dump(statistics, statsHandle, sort_keys=True, indent=4 )
        

    @abc.abstractmethod
    def _getBuildingLocations(self):
        return


    @abc.abstractmethod
    def _getElevatorModel(self):
        return


    @abc.abstractmethod
    def _createActorsForDay(self, currDate, buildingLocations):
        return

