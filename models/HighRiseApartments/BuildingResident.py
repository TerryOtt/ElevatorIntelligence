#!/usr/bin/python

from common.Actor import Actor
import logging
import datetime
import random

class BuildingResident(Actor):

    def __init__(self, apartmentNumber, apartmentResidentID, currDate):

        self._apartmentNumber = apartmentNumber
        self._apartmentResidentID = apartmentResidentID
        self._homeFloor = "Floor {0}".format(
            self._apartmentNumber[0] )

        Actor.__init__(self, "RES {0}-{1}".format(
            apartmentNumber, apartmentResidentID), currDate )


    def _createActivities(self):
        self._log.debug("Creating activities for {0} on date {1}".format(
            self.getName(), self.getDate().isoformat()) )

        # Starting location for a building resident will either be in apt or
        #   significant others' residence
        self.setLocation( random.choice( 
            [ self._homeFloor, "Not In Building" ]) )

        self._log.debug("Starting location for {0} on date {1}: {2}".format(
            self.getName(), self.getDate().isoformat(), self.getLocation()) )
        
        self._log.debug("Created activities for {0} on date {1}".format(
            self.getName(), self.getDate().isoformat()) )

        return {}


    def startDailyActivities(self, todaysDate):
        self._setDate(todaysDate)
        self._log.info("Starting daily activities for " + self.getName() +
           " on " + self._getDate().strftime("%A, %Y-%m-%d"))


    def getApartmentNumber(self):
        return self._apartmentNumber


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resident = BuildingResident( "819", 1, datetime.date(2016, 12, 15) )
    resident.startDailyActivities()
