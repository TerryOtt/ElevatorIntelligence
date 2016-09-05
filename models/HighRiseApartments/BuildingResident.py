#!/usr/bin/python3

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
        self._checkedMailToday = False

        self._simulationProbabilities = {
            'checkMailAfterParking':    0.25,
            'shoppingOnWayHome':        0.25,
        }

        self._floorIndex = { 
            "Floor 8": 9,
            "Floor 7": 8,
            "Floor 6": 7,
            "Floor 5": 6,
            "Floor 4": 5,
            "Floor 3": 4,
            "Floor 2": 3,
            "Floor 1": 2,
            "Floor G": 1
        }

        self._servicesFloorIndex = {
            "Leasing Office": 5,
            "Mail": 4
        }
        

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

            self._driveHomeGoToApartment(returnTime)
        # We started out at home
        else:
            # self._parkCar()
            pass
            
        
    def _createWeekendActivities(self):
        self._log.debug("Creating weekend activities for {0} on {1} ({2})".format(
            self.getName(), self.getDate(), self._getDayOfWeekString()) )


    def _getParkingFloor(self):
        return self._parkingFloor


    def _parkCarInGarage(self, returnTime):
        parkActivity = HighRiseApartments.BuildingActivities.ParkCar(returnTime)

        # Have to record what floor we parked on to be sane if we leave again later
        self._parkingFloor = parkActivity.getParkingFloor()

        self._addPendingActivity(parkActivity)



    def _goFromCarToApt(self, willingToCheckMail=True, willingToTakeStairs=True):
        
        # Things we know
        #   * We know time we parked with getting earliest start time, so that can
        #       be start time
        #   * Floor we parked on (self._parkingFloor)

        # See if we want to check mail first?
        currFloorIndex = self._floorIndex[ self._getParkingFloor() ]

        if willingToCheckMail is True and self._wantToCheckMail() is True:
            self._log.debug("{0} wants to check mail after parking before going to the apt".format(
                self.getName()) )
            self._checkMail(currFloorIndex, willingToTakeStairs)
            currFloorIndex = self._servicesFloorIndex[ "Mail" ]

        self._goToApartment(currFloorIndex, willingToTakeStairs)


    def _wantToCheckMail(self):
        # If we've checked mail today, definitely not
        if self._haveCheckedMailToday() is True:
            return False

        # If we haven't today, there's still a pretty low chance we want to
        return random.random() <= self._simulationProbabilities['checkMailAfterParking']
            

    def _haveCheckedMailToday(self):
        return self._checkedMailToday


    def _checkMail(self, startingFloorIndex, willingToTakeStairs):
        # Do we even have to change floors?
        if startingFloorIndex == self._servicesFloorIndex[ "Mail" ]:
            # Just add some time for walking
            self._earliestStartTime += datetime.timedelta(minutes=random.randint(3, 5))

        else:
            self._changeFloors(startingFloorIndex, self._servicesFloorIndex[ "Mail" ])

        # Show we've checked mail and add some time
        self._earliestStartTime += datetime.timedelta(minutes=random.randint(1, 10))
        self._checkedMailToday = True


    def _changeFloors(self, startingFloorIndex, endingFloorIndex, willingToTakeStairs=True):
        # Find out if this is a no-op
        if startingFloorIndex == endingFloorIndex:
            return

        # Create inverse mapping of floors
        inv_map = {v: k for k, v in self._floorIndex.items()} 
        self._log.debug("{0} is changing floors from {1} to {2}".format(
            self.getName(), inv_map[startingFloorIndex], inv_map[endingFloorIndex]) )

        startTime = self._getEarliestStartTime()

        # Are they taking stairs? Odds drop with more floors they need to cover
        floorIndexDelta = abs(endingFloorIndex - startingFloorIndex)
        if willingToTakeStairs is True and random.random() <= 1.0/abs(floorIndexDelta):
            self._log.debug("{0} is being hardcore and taking the stairs!".format(
                self.getName()))

            # Let's call it 10-20 seconds per flight
            self._earliestStartTime += \
                datetime.timedelta(seconds=(random.randint(10,20) * floorIndexDelta))

        else:
            self._log.debug("{0} is being smart and taking the elevator".format(
                self.getName()))
            
            self._rideElevator(startingFloorIndex, endingFloorIndex)


    def _goToApartment(self, startingFloorIndex, willingToTakeStairs=True ):
        self._changeFloors(startingFloorIndex, self._floorIndex[self._homeFloor],
            willingToTakeStairs)


    def _rideElevator(self, startingFloorIndex, endingFloorIndex):
        buttonActivity = HighRiseApartments.BuildingActivities.RequestElevator(
            self._getEarliestStartTime() + datetime.timedelta(seconds=1), 
            startingFloorIndex, endingFloorIndex)

        self._addPendingActivity(buttonActivity)

        # Figure out elevator ride time
        floorIndexDelta = abs(endingFloorIndex - startingFloorIndex)
        # Approximating one second per floor
        secondsPerFloor = 1.0  
        elevatorRideTime = datetime.timedelta(seconds=(secondsPerFloor * floorIndexDelta))
        self._earliestStartTime += elevatorRideTime

        


    def _driveHomeGoToApartment(self, returnTime):
        self._log.debug("Resident {0} returning at {1}".format(
            self.getName(), returnTime) )

        # Do we do any shopping on way home?
        if random.random() <= self._simulationProbabilities['shoppingOnWayHome']:
            unloadingTrips = random.randint(1,4)
            self._log.debug("Resident {0} went shopping on way home, needs {1} ".format(
                self.getName(), unloadingTrips) + " trips from car to unload")
        else:
            unloadingTrips = 0

        self._parkCarInGarage(returnTime)

        # If we didn't do any shopping, only need one trip to apartment, and willing to check mail or
        #       take stairs
        if unloadingTrips == 0:
            self._goFromCarToApt(True, True)

        # We went shopping, assuming they won't check mail or use stairs
        else:
            for i in range(unloadingTrips):

                # If this is their last unloading trip they are willing to consider 
                #   using stairs and checking mail
                if i == (unloadingTrips -1 ):
                    isLastTrip = True
                else:
                    isLastTrip = False

                self._goFromCarToApt( isLastTrip, isLastTrip )

                # Take a few minutes to get to/from apt and drop stuff off in apartment
                self._earliestStartTime += datetime.timedelta(
                    minutes=random.randint(1,5),
                    seconds=random.randint(0,59) )

                # Need to return to car
                self._goFromAptToCar()


    def _goFromAptToCar(self, willingToCheckMail=True, willingToTakeStairs=True):
        
       # See if we want to check mail first?
        currFloorIndex = self._floorIndex[ self._homeFloor ]

        if willingToCheckMail is True and self._wantToCheckMail() is True:
            self._log.debug("{0} wants to check mail on way from apt to car".format(
                self.getName()) )
            self._checkMail(currFloorIndex, willingToTakeStairs)
            currFloorIndex = self._servicesFloorIndex[ "Mail" ]

        self._goToCar(currFloorIndex, willingToTakeStairs)


    def _goToCar(self, startingFloorIndex, willingToTakeStairs=True):
        self._changeFloors(startingFloorIndex, self._floorIndex[self._parkingFloor],
            willingToTakeStairs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resident = BuildingResident( "819", 1, datetime.date(2016, 12, 15) )
    resident.startDailyActivities()
