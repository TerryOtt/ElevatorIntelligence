#!/usr/bin/python

from common.Actor import Actor
import logging
import datetime

class BuildingResident(Actor):

    def __init__(self, buildingResidentID, startingLocation):
        Actor.__init__(self, "RES " + buildingResidentID, startingLocation)

        self._log.info("Instantiated actor " + self.getName())

    def startDailyActivities(self, todaysDate):
        self._setDate(todaysDate)
        self._log.info("Starting daily activities for " + self.getName() +
           " on " + self._getDate().strftime("%A, %Y-%m-%d"))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resident = BuildingResident("819-1")
    resident.startDailyActivities(datetime.date(2016, 12, 15))
