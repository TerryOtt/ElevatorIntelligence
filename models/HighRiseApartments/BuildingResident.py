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

        # These are things that residents do at MOST once per day
        self._dailyActivities = {
            'checkMail': { 
                'completed':    False, 
                'probability':  0.25
            },

            'retrievePackages': {
                'completed':    False,
                'probability':  0.05
            },

            'workOut': {
                'completed':    False,
                'probability':  0.40
            },

            'goShopping': {
                'completed':    False,
                'probability':  0.10
            },

            'primaryActivityWeekday': {
                'completed':    False,
                'probability':  0.98
            },

            'earnPaycheckWeekend': {
                'completed':    False,
                'probability':  0.05
            },
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
            "Leasing Office":   5,
            "Mail":             4,
            "Gym":              3,
        }

        self._buildingPedestrianEntranceExitFloors = [
            'Floor 4',
            'Floor 3' ]

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
            # Initialize car to a sane floor
            self._parkingFloor = HighRiseApartments.BuildingActivities.ParkCar.getRandomParkingFloor()

            self._log.debug("Starting out at home, car has been warped to {0}".format(
                self._parkingFloor) )

            # Set their start time to a sane time
            self._earliestStartTime += datetime.timedelta(
                hours =     random.randint(5, 10),
                minutes =   random.randint(0, 59),
                seconds =   random.randint(0, 59) )

        # Common path -- person's at home, starting a weekday

        # Should we go to the gym first thing?
        if self._testDailyActivity('workOut') is True:
            self._workOut()

        # Do we do our primary activity?
        if self._testDailyActivity('primaryActivityWeekday') is True:
            # What is that primary activity?
            primaryActivity = random.random()

            # Have a job
            if primaryActivity <= 0.80:
                self._goToWork()

            # Stay at home 
            elif primaryActivity <= 0.90:
                self._stayAtHomeParent()
            
            # College student
            elif primaryActivity <= 0.98:
                self._goToClassCollege()
        
            # K12 student
            else:
                self._goToClassK12()

            
        
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

        if willingToCheckMail is True:
            if self._wantToCheckMail() is True:
                self._log.debug("{0} wants to check mail after parking before going to the apt".format(
                    self.getName()) )
                self._checkMail(currFloorIndex, willingToTakeStairs)
                currFloorIndex = self._servicesFloorIndex[ "Mail" ]
            elif self._wantToRetrievePackages() is True:
                self._log.debug("{0} wants to retrive packages after parking before going to the apt".format(
                    self.getName()) )
                self._retrievePackages(currFloorIndex, willingToTakeStairs)
                currFloorIndex = self._servicesFloorIndex[ "Leasing Office" ]

        self._goToApartment(currFloorIndex, willingToTakeStairs)


    def _wantToCheckMail(self):
        return self._testDailyActivity('checkMail')


    def _wantToRetrievePackages(self):
        return self._testDailyActivity('retrievePackages')


    def _wantToWorkOut(self):
        return self._testDailyActivity('workOut')
     

    def _testDailyActivity(self, dailyActivity):
        # If we've done the task today already, definitely not
        if self._dailyActivities[dailyActivity]['completed'] is True:
            return False

        # See if we do the activity now
        elif random.random() <= self._dailyActivities[dailyActivity]['probability']:
            # Mark it complete
            self._dailyActivities[dailyActivity]['completed'] = True
            return True

        else:
            return False



    def _checkMail(self, startingFloorIndex, willingToTakeStairs):
        # Do we even have to change floors?
        if startingFloorIndex == self._servicesFloorIndex[ "Mail" ]:
            # Just add some time for walking
            self._earliestStartTime += datetime.timedelta(minutes=random.randint(3, 5))

        else:
            self._changeFloors(startingFloorIndex, self._servicesFloorIndex[ "Mail" ])

        # Show we've checked mail and add some time
        self._earliestStartTime += datetime.timedelta(minutes=random.randint(1, 10))


    def _retrievePackages(self, startingFloorIndex, willingToTakeStairs):
        self._goToLeasingOffice(startingFloorIndex, willingToTakeStairs)

        # Add time to check packages
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(1, 5),
            seconds=random.randint(0,59))


    def _goToLeasingOffice(self, startingFloorIndex, willingToTakeStairs):
        # Do we even have to change floors?
        if startingFloorIndex == self._servicesFloorIndex[ "Leasing Office" ]:
            # Just add some time for walking
            self._earliestStartTime += datetime.timedelta(minutes=random.randint(3, 5))

        else:
            self._changeFloors(startingFloorIndex, self._servicesFloorIndex[ "Leasing Office" ])


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
        if willingToTakeStairs is True and random.random() <= 1.0/(4 * abs(floorIndexDelta)):
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
        self._log.debug("Resident {0} returning by car at {1}".format(
            self.getName(), returnTime) )

        # Do we do any shopping on way home?
        if self._testDailyActivity('goShopping'):
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
                if i == (unloadingTrips - 1 ):
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


    def _walkHomeGoToApartment(self, returnTime):
        self._log.debug("Resident {0} returning by foot at {1}".format(
            self.getName(), returnTime) )

        self._goFromWalkingEntranceToApt(returnTime)


    def _goFromWalkingEntranceToApt(self, returnTime, willingToCheckMail=True, willingToTakeStairs=True):
        # See where we come in
        currFloorIndex = self._floorIndex[ random.choice( self._buildingPedestrianEntranceExitFloors ) ]

        if willingToCheckMail is True:
            if self._wantToCheckMail() is True:
                self._log.debug("{0} wants to check mail after walking home before going to the apt".format(
                    self.getName()) )
                self._checkMail(currFloorIndex, willingToTakeStairs)
                currFloorIndex = self._servicesFloorIndex[ "Mail" ]
            elif self._wantToRetrievePackages() is True:
                self._log.debug("{0} wants to retrive packages after walking home before going to the apt".format(
                    self.getName()) )
                self._retrievePackages(currFloorIndex, willingToTakeStairs)
                currFloorIndex = self._servicesFloorIndex[ "Leasing Office" ]

        self._goToApartment(currFloorIndex, willingToTakeStairs)


    def _goFromAptToCar(self, willingToCheckMail=True, willingToTakeStairs=True):
        
        # See if we want to check mail first?
        currFloorIndex = self._floorIndex[ self._homeFloor ]

        if willingToCheckMail is True:
            if self._wantToCheckMail() is True:
                self._log.debug("{0} wants to check mail on way from apt to car".format(
                    self.getName()) )
                self._checkMail(currFloorIndex, willingToTakeStairs)
                currFloorIndex = self._servicesFloorIndex[ "Mail" ]

            if self._wantToRetrievePackages() is True:
                self._log.debug("{0} wants to retrieve packages on way from apt to car".format(
                    self.getName()) )
                self._retrievePackages(currFloorIndex, willingToTakeStairs)
                currFloorIndex = self._servicesFloorIndex[ "Leasing Office" ]

        self._goToCar(currFloorIndex, willingToTakeStairs)


    def _goToCar(self, startingFloorIndex, willingToCheckMail=True, willingToTakeStairs=True):
        self._changeFloors(startingFloorIndex, self._floorIndex[self._parkingFloor],
            willingToTakeStairs)


    def _workOut(self):
        self._log.debug("{0} is doing their daily workout".format(
            self.getName()) )

        # Get changed into gym clothes
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(1,10),
            seconds=random.randint(0,59) )

        self._changeFloors(self._floorIndex[self._homeFloor], 
            self._servicesFloorIndex[ "Gym" ],
            willingToTakeStairs=True)

        # Workout will be 20-90 minutes
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(20,89),
            seconds=random.randint(0,59) )

        # Go back to apt
        self._changeFloors(
            self._servicesFloorIndex[ "Gym" ],
            self._floorIndex[self._homeFloor],
            willingToTakeStairs=True)

        # Get cleaned up
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(5,20),
            seconds=random.randint(0,59) )


    def _goToWork(self):
        self._log.debug("{0} is going to work".format(
            self.getName()) )

        # Stay at work for reasonable amount of time
        returnTime = self._earliestStartTime + \
            datetime.timedelta(
                hours =     random.randint(7,10),
                minutes =   random.randint(0, 59),
                seconds =   random.randint(0, 59) )


        self._leaveBuildingUntilTime(
            self._floorIndex[self._homeFloor],
            returnTime) 


    def _stayAtHomeParent(self):
        self._log.debug("{0} is a stay at home parent".format(
            self.getName()) )


    def _goToClassCollege(self):
        self._log.debug("{0} is a college student".format(
            self.getName()) )

        # Stay at college for reasonable amount of time
        returnTime = self._earliestStartTime + \
            datetime.timedelta(
                hours =     random.randint(3,10),
                minutes =   random.randint(0, 59),
                seconds =   random.randint(0, 59) )

        self._leaveBuildingUntilTime(
            self._floorIndex[self._homeFloor],
            returnTime)


    def _goToClassK12(self):
        self._log.debug("{0} is a K12 student".format(
            self.getName()) )

        currDate = self.getDate()

        # Stay in school until a reasonable amount of time, factor in after school activities
        #   1400 = 2pm, 2000 = 8pm
        returnTime = datetime.datetime(
                currDate.year, currDate.month, currDate.day,         
                random.randint(14, 19),
                random.randint(0, 59),
                random.randint(0, 59) )

        self._leaveBuildingUntilTime(
            self._floorIndex[self._homeFloor], 
            returnTime)


    def _leaveBuildingUntilTime(self, startingFloorIndex, returnTime):
        # Do they take mass transit (bus/metro)?
        if random.random() <= 0.20:
            massTransit = True
        else:
            massTransit = False

        if massTransit is True:
            self._walkOutOfBuilding(startingFloorIndex)
        else:
            self._goFromAptToCar()
            self._parkingFloor = None

        self._log.debug("{0} is coming home at {1}".format(
            self.getName(), returnTime) )

        # Mass transit home?
        if massTransit is True:
            self._walkHomeGoToApartment(returnTime)
        else:
            self._driveHomeGoToApartment(returnTime)



    def _walkOutOfBuilding(self, startingFloorIndex, willingToTakeStairs=True):
        # Find out which floor we're going to 
        exitFloor = random.choice( self._buildingPedestrianEntranceExitFloors )

        self._changeFloors(
            startingFloorIndex,
            self._floorIndex[exitFloor],
            willingToTakeStairs )

        return exitFloor 
 

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resident = BuildingResident( "819", 1, datetime.date(2016, 12, 15) )
    resident.startDailyActivities()
