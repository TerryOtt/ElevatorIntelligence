#!/usr/bin/python3

from models.common.Actor import Actor
import models.HighRiseApartments.BuildingActivities 
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
                'probability':  0.20
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
            "Leasing Office":   self._floorIndex["Floor 4"],
            "Mail":             self._floorIndex["Floor 3"], 
            "Gym":              self._floorIndex["Floor 3"], 
        }

        self._buildingPedestrianEntranceExitFloors = [
            'Floor 4',
            'Floor 3' ]

        self._buildingGrillFloors = [
            'Floor 3',
            'Floor 2' ]

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
            self._parkingFloor = models.HighRiseApartments.BuildingActivities.ParkCar.getRandomParkingFloor()

            self._log.debug("Starting out at home, car has been warped to {0}".format(
                self._parkingFloor) )

            # Set their start time to a sane time
            self._earliestStartTime += datetime.timedelta(
                hours =     random.randint(5, 10),
                minutes =   random.randint(0, 59),
                seconds =   random.randint(0, 59) )

        # Common path -- person's at home, starting a weekday
        self._log.info("Starting day for {0} at {1}".format(
            self.getName(), self._earliestStartTime) )

        # Should we go to the gym first thing?
        if self._testDailyActivity('workOut') is True:
            self._workOut()

        # Get cleaned up and ready for day
        self._earliestStartTime += datetime.timedelta(
            minutes =   random.randint(20, 89),
            seconds =   random.randint(0, 59) )

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

        # Did we do enough stuff to get us to evening hours?  If not, warp ahead
        currDate = self.getDate()
        fivePmToday = datetime.datetime(
            currDate.year, currDate.month, currDate.day, 17, 0, 0)
        if self._getEarliestStartTime() < fivePmToday:
            self._earliestStartTime  = fivePmToday

        # Delay after primary activity.
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint( 5, 60),
            seconds=random.randint( 0, 59))

        # Test if we are going to consider work out before dinner?
        if random.random() < 0.60:
            if self._testDailyActivity('workOut') is True:
               self._workOut()

            self._earliestStartTime += datetime.timedelta(
                minutes=random.randint( 5, 119),
                seconds=random.randint( 0, 59) )

            self._eatMeal()

        else:
            self._eatMeal()

            if self._testDailyActivity('workOut') is True:
                self._earliestStartTime += datetime.timedelta(
                    hours  =random.randint( 1,  2),
                    minutes=random.randint( 0, 59),
                    seconds=random.randint( 0, 59) )

                self._workOut()

        # Are we in for the night?
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint( 5, 119),
            seconds=random.randint( 0, 59) )

        if random.random() < 0.80:
            self._log.info("{0} is in for the night at {1}".format(
                self.getName(), self._getEarliestStartTime()) )
        else:
            self._log.info("{0} is spending the night elsewhere".format(
                self.getName()) )
            self._goFromAptToCar()
                

        
    def _createWeekendActivities(self):
        self._log.debug("Creating weekend activities for {0} on {1} ({2})".format(
            self.getName(), self.getDate(), self._getDayOfWeekString()) )


    def _getParkingFloor(self):
        return self._parkingFloor


    def _parkCarInGarage(self, returnTime):
        self._log.info("{0} is parking car in garage at {1}".format( 
            self.getName(), returnTime) )
        parkActivity = models.HighRiseApartments.BuildingActivities.ParkCar(returnTime)

        # Have to record what floor we parked on to be sane if we leave again later
        self._parkingFloor = parkActivity.getParkingFloor()

        self._addPendingActivity(parkActivity)


    def _goFromCarToApt(self, willingToCheckMail=True, willingToTakeStairs=True):
        
        # Things we know
        #   * We know time we parked with getting earliest start time, so that can
        #       be start time
        #   * Floor we parked on (self._parkingFloor)

        self._log.debug("{0} is going from car to apt, possibly with stops".format(
            self.getName()) )

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
        self._log.info("{0} is checking their mail".format(self.getName()) )
        # Do we even have to change floors?
        if startingFloorIndex == self._servicesFloorIndex[ "Mail" ]:
            # Just add some time for walking
            self._earliestStartTime += datetime.timedelta(
                minutes=random.randint( 3,  5),
                seconds=random.randint( 0, 59 ) )

        else:
            self._changeFloors(startingFloorIndex, self._servicesFloorIndex[ "Mail" ])

        # Show we've checked mail and add some time
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint( 1, 10),
            seconds=random.randint( 0, 59) )


    def _retrievePackages(self, startingFloorIndex, willingToTakeStairs):
        self._log.info("{0} is retrieving packages from leasing office".format(
            self.getName()) )

        self._goToLeasingOffice(startingFloorIndex, willingToTakeStairs)

        # Add time to check packages
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(1, 5),
            seconds=random.randint(0,59))


    def _goToLeasingOffice(self, startingFloorIndex, willingToTakeStairs):
        self._log.debug("{0} is going to leasing office".format( self.getName()) )

        # Do we even have to change floors?
        if startingFloorIndex == self._servicesFloorIndex[ "Leasing Office" ]:
            # Just add some time for walking
            self._earliestStartTime += datetime.timedelta(
                minutes=random.randint( 3, 5 ),
                seconds=random.randint( 0, 59) )

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
        self._log.debug("{0} is going to their apartment".format(self.getName()) )
        self._changeFloors(startingFloorIndex, self._floorIndex[self._homeFloor],
            willingToTakeStairs)


    def _rideElevator(self, startingFloorIndex, endingFloorIndex):
        buttonActivity = models.HighRiseApartments.BuildingActivities.RequestElevator(
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
        self._log.info("Resident {0} returning by car at {1}".format(
            self.getName(), returnTime) )

        # Do we do any shopping on way home?
        if self._testDailyActivity('goShopping'):
            numTripsProb = random.random()
            if numTripsProb   <= 0.50:
                unloadingTrips = 1
            elif numTripsProb <= 0.75:
                unloadingTrips = 2
            elif numTripsProb <= 0.87:
                unloadingTrips = 3
            else:
                unloadingTrips = 4

            self._log.info("Resident {0} went shopping on way home, needs {1}".format(
                self.getName(), unloadingTrips) + " trips from car to unload")
        else:
            unloadingTrips = 0

        self._parkCarInGarage(returnTime)

        # If we didn't do any shopping, only need one trip to apartment, and willing to check mail or
        #       take stairs
        if unloadingTrips == 0:
            self._goFromCarToApt(True, True)

        # We went shopping
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

                # Do we need to return to car?
                if isLastTrip is False:
                    self._goFromAptToCar()

            self._log.info("{0} is done unloading the car at {1}".format(
                self.getName(), self._getEarliestStartTime()) )


    def _walkHomeGoToApartment(self, returnTime):
        self._log.debug("Resident {0} returning by foot at {1}".format(
            self.getName(), returnTime) )

        self._goFromWalkingEntranceToApt(returnTime)


    def _goFromWalkingEntranceToApt(self, returnTime, willingToCheckMail=True, willingToTakeStairs=True,
            startingFloorIndex = random.choice( [ 4, 5 ] ) ):

        self._log.debug("{0} is going to walk in from outside to their apartment".format(
            self.getName()) )

        # See where we come in
        currFloorIndex = startingFloorIndex

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

        self._log.debug("{0} is going to transition from apartment to car, possibly with stops".format(
            self.getName()) )
        
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
        self._log.info("{0} is going to their car, possibly with stops".format(
            self.getName()) )

        self._changeFloors(startingFloorIndex, self._floorIndex[self._parkingFloor],
            willingToTakeStairs)


    def _workOut(self):
        self._log.info("{0} is doing their daily workout at {1}".format(
            self.getName(), self._getEarliestStartTime()) )

        # Get changed into gym clothes
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(1,10),
            seconds=random.randint(0,59) )

        # Do we use the building gym? Seems like hardly any do

        if random.random() < 0.15:
            workOutInBuilding = True
        else:
            workOutInBuilding = False

        workoutDuration = datetime.timedelta(
            minutes=random.randint(20,89),
            seconds=random.randint(0,59) )

        if workOutInBuilding is True:
            self._log.info("{0} is wisely working out in the apartment gym".format(
                self.getName()) )
            self._changeFloors(self._floorIndex[self._homeFloor], 
                self._servicesFloorIndex[ "Gym" ],
                willingToTakeStairs=True)

            self._earliestStartTime += workoutDuration

            # Go back to apt
            self._goToApartment( self._servicesFloorIndex[ "Gym" ] )

        else:
            self._log.info("{0} is heading to their off-site gym".format(
                self.getName()) )

            driveTime = datetime.timedelta(
                minutes=random.randint(5, 30),
                seconds=random.randint(0, 59) )

            self._leaveBuildingUntilTime(
                self._floorIndex[self._homeFloor],
                self._getEarliestStartTime() + (2 * driveTime) + workoutDuration)

        # Get cleaned up after workout
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(5,20),
            seconds=random.randint(0,59) )

        self._log.info("{0} is done with workout and shower at {1}".format(
            self.getName(), self._getEarliestStartTime()) )


    def _goToWork(self):
        self._log.info("{0} is going to work at {1}".format(
            self.getName(), self._getEarliestStartTime()) )

        # Stay at work for reasonable amount of time
        returnTime = self._earliestStartTime + \
            datetime.timedelta(
                hours =     random.randint(7, 11),
                minutes =   random.randint(0, 59),
                seconds =   random.randint(0, 59) )

        self._leaveBuildingUntilTime(
            self._floorIndex[self._homeFloor],
            returnTime) 

        self._log.info("{0} has returned home from work at {1}".format(
            self.getName(), self._getEarliestStartTime()) )


    def _stayAtHomeParent(self):
        self._log.info("{0} is a stay at home parent".format(
            self.getName()) )

        stayHomeActivity = random.random() 

        # Walk the dog/stroller?
        if random.random() < 0.30:
            self._goForWalk() 
           
            # hang out for awhile
            self._earliestStartTime += datetime.timedelta(
                minutes=random.randint(30, 180),
                seconds=random.randint(0, 59)
            )

        # Run some errands?
        if random.random() < 0.80:
            self._log.debug("{0} is running an errand".format(self.getName()) )
            returnTime = self._earliestStartTime + \
                datetime.timedelta(
                    minutes =   random.randint(0, 179),
                    seconds =   random.randint(0, 59) )

            self._leaveBuildingUntilTime(
                self._floorIndex[self._homeFloor],
                returnTime)


        # Eat lunch
        self._eatMeal(useGrill = False)

        # Hit the gym?
        if random.random() < 0.50:
            if self._testDailyActivity('workOut') is True:
                self._workOut()



    def _goToClassCollege(self):
        self._log.info("{0} is a college student, going to class at {1}".format(
            self.getName(), self._getEarliestStartTime()) )

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
        self._log.info("{0} is a K12 student, going to school at {1}".format(
            self.getName(), self._getEarliestStartTime()) )

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
            self._log.debug("{0} is leaving building via mass transit".format(
                self.getName()) )
            massTransit = True
        else:
            self._log.debug("{0} is leaving building by their own car".format(
                self.getName()) )
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

        self._log.debug("{0} is leaving building by a walking exit".format(
            self.getName()) )

        # Find out which floor we're going to 
        exitFloor = random.choice( self._buildingPedestrianEntranceExitFloors )

        self._changeFloors(
            startingFloorIndex,
            self._floorIndex[exitFloor],
            willingToTakeStairs )

        return exitFloor 


    def _goForWalk(self):

        self._log.debug("{0} is leaving the apt and going for a walk".format(
            self.getName()) )

        exitFloor = self._walkOutOfBuilding(self._floorIndex[self._homeFloor])

        # Stay gone for awhile
        returnTime = self._earliestStartTime + datetime.timedelta(
            minutes=random.randint(20, 89),
            seconds=random.randint(0,59))

        # Come back in same door we left from
        self._goFromWalkingEntranceToApt(self, returnTime, 
            startingFloorIndex = exitFloor )


    def _eatMeal(self, useGrill=True):

        self._log.info("{0} is hungry and is going to eat at {1}".format(
            self.getName(), self._getEarliestStartTime()) )

        # Are we eating at a restaurant
        if random.random() <= 0.20:
            self._log.info("{0} is leaving to eat at a restaurant at {1}".format(
                self.getName(), self._getEarliestStartTime()) )
            self._leaveBuildingUntilTime(
                self._floorIndex[self._homeFloor],
                self._earliestStartTime + 
                    datetime.timedelta(
                        minutes =   random.randint(30, 90),
                        seconds =   random.randint(0, 59)) )

            self._log.info("{0} has returned from the restaurant at {1}".format(
                self.getName(), self._getEarliestStartTime()) )

        # eating at home
        else:
            self._log.debug("{0} is eating a meal at home".format(
                self.getName()) )

            # Are we ordering in?
            if random.random() <= 0.05:
                # Generate delivery person behavior
                self._requestDeliveryToApt()

            # Do we need to cook?
            elif random.random() <= 0.50:

                # Does cooking involve grilling in courtyard?
                if useGrill is True and random.random() <= 0.05:
                    self._useCourtyardGrillingStation(self._homeFloor)

                else:
                    # Cooking time
                    self._earliestStartTime += datetime.timedelta(
                        minutes =   random.randint(5, 180),
                        seconds =   random.randint(0, 59) )

            # Eating time
            self._earliestStartTime += datetime.timedelta(
                minutes =   random.randint(20, 89),
                seconds =   random.randint(0, 59) )
 
        self._log.info("{0} is done eating at {1}".format(
            self.getName(), self._getEarliestStartTime()) )


    def _requestDeliveryToApt(self):

        self._log.info("{0} is requesting a delivery to their apartment at {1}".format(
            self.getName(), self._getEarliestStartTime()) )

        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(30, 90),
            seconds=random.randint( 0, 59) )

        # Are they willing to get buzzed in and come up themselves?
        if random.random() <= 0.80:
            self._log.debug("Delivery person for {0} coming to apartment".format(
                self.getName()) )

            self._goToApartment(
                self._floorIndex["Floor 4"], 
                willingToTakeStairs = False)

            # Do delivery
            self._earliestStartTime += datetime.timedelta(
                minutes=random.randint( 2, 9),
                seconds=random.randint( 0, 59) )

            # Go back to car
            self._changeFloors(
                self._floorIndex[self._homeFloor],
                self._floorIndex["Floor 4"],
                willingToTakeStairs = True)

        else:

            self._log.debug("{0} is heading to front entrance to pick up delivery".format(
                self.getName()) )

            # Head to door to pick up delivery
            self._changeFloors(
                self._floorIndex[self._homeFloor],
                self._floorIndex["Floor 4"],
                willingToTakeStairs = True)

            # Deal with money, take delivery
            self._earliestStartTime += datetime.timedelta(
                seconds=random.randint( 30, 180) )

            self._goToApartment(
                self._floorIndex["Floor 4"],
                willingToTakeStairs = False)


    def _useCourtyardGrillingStation(self):
        self._log.info("{0} is going to grill station to cook dinner".format(
            self.getName()) )

        grillFloor = self._goToGrills(self._homeFloor, willingToTakeStairs=False)

        # Cook dinner
        self._earliestStartTime += datetime.timedelta(
            minutes=random.randint(10, 44),
            seconds=random.randint( 0, 59) )

        # Head back to apartment
        self._goToApartment( grillFloor, self._homeFloor )


    def _goToGrills(self, startingFloor, willingToTakeStairs=True):
        grillFloor = random.choice( self._buildingGrillFloors )

        # Head down with uncooked food
        self._changeFloors(
            self._floorIndex[startingFloor],
            self._floorIndex[grillFloor],
            willingToTakeStairs = True)

        return grilFloor
 


    # TODO: need an event for hosting an event -- may involve grilling, going to game room, etc.

 

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    resident = BuildingResident( "819", 1, datetime.date(2016, 12, 15) )
    resident.startDailyActivities()
