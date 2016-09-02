#!/usr/bin/python

from common.Actor import Actor
import HighRiseApartments.BuildingActivities 
import logging
import datetime
import random
import pprint


class BuildingResident(Actor):


    def __init__(self, apartmentNumber, apartmentResidentID, currDate):

        self._apartmentNumber = apartmentNumber
        self._apartmentResidentID = apartmentResidentID
        self._homeFloor = "Floor {0}".format(
            self._apartmentNumber[0] )
        self._parkingFloor = None

        Actor.__init__(self, "RES {0}-{1}".format(
            apartmentNumber, apartmentResidentID), currDate )


    def _createActivities(self):
        self._log.debug("Creating activities for {0} on date {1}".format(
            self.getName(), self.getDate().isoformat()) )

        # Starting location for a building resident will either be in apt or
        #   significant others' residence
        self.setLocation( random.choice( 
            [ self._getHomeFloor(), "Not In Building" ]) )

        self._log.debug("Starting location for {0} on date {1}: {2}".format(
            self.getName(), self.getDate().isoformat(), self.getLocation()) )

        # All logic depends on day of the week
        if self._isWeekday():
            self._createWeekdayActivities()
        else:
            self._createWeekendActivities()

        self._log.debug("Created activities for {0} on date {1}".format(
            self.getName(), self.getDate().isoformat()) )


    def startDailyActivities(self, todaysDate):
        self._setDate(todaysDate)
        self._log.info("Starting daily activities for " + self.getName() +
           " on " + self._getDate().strftime("%A, %Y-%m-%d"))


    def getApartmentNumber(self):
        return self._apartmentNumber


    def _getHomeFloor(self):
        return self._homeFloor


    def _createWeekdayActivities(self):
        self._log.debug("Creating weekday activities for {0} on {1} ({2})".format(
            self.getName(), self.getDate(), self._getDayOfWeekString()) )

        currDate = self.getDate()

        # Handle case where resident need to come home first
        if self.getLocation() != self._getHomeFloor():

            # Set a reasonable time to park and come to home floor (6-9am)
            returnTime = datetime.datetime(
                currDate.year, currDate.month, currDate.day,
                random.randint(6, 8),
                random.randint(0, 59),
                random.randint(0, 59)
            )

            self._log.debug("Resident {0} returning at {1}".format(
                self.getName(), returnTime) )

            parkActivity = HighRiseApartments.BuildingActivities.ParkCar(returnTime)
            self._addPendingActivity(parkActivity)

            # Now they need to ride the elevator to their floor
            


        # We started out at home
        else:
            # self._parkCar()
            pass
            
        
    def _createWeekendActivities(self):
        self._log.debug("Creating weekend activities for {0} on {1} ({2})".format(
            self.getName(), self.getDate(), self._getDayOfWeekString()) )


    def _getParkingFloor(self):
        return self._parkingFloor


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resident = BuildingResident( "819", 1, datetime.date(2016, 12, 15) )
    resident.startDailyActivities()
