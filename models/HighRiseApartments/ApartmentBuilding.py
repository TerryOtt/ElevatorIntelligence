#!/usr/bin/python3

import logging
from models.common.Building                        import Building
from models.HighRiseApartments.BuildingResident    import BuildingResident
from models.common.Location                        import Location
import datetime
import pprint
import random


class ApartmentBuilding(Building):


    def __init__(self, buildingName, buildingLocation):
        self._log = logging.getLogger(__name__)
        Building.__init__(self, buildingName, buildingLocation)


    def _getBuildingLocations(self):

        buildingLocations = {
            "Floor 8": Location("Floor 8"),
            "Not In Building": Location("Not In Building")
        }

        return buildingLocations

  
    def _getElevatorModel(self):
        return None


    def _createActorsForDay(self, currDate, buildingLocations):
        self._log.debug("Building {0} creating actors for date {1}".format(
            self.getName(), currDate.isoformat()) )

        # resident = BuildingResident("819", 1, currDate)

        # buildingLocations[resident.getLocation()].addActorToLocation(
        #    resident, datetime.datetime(currDate.year, currDate.month, currDate.day))

        # Add residents by floor
        actorList = {}
        for currFloor in range(2, 9):
            # Determine number of residents on this floor
            numberResidentsOnFloor = random.randint(10, 30)

            for currFloorResident in range(1,numberResidentsOnFloor + 1):
                newResident = BuildingResident( "{0}{1:02d}".format(
                    currFloor, currFloorResident), 1, currDate)

                actorList[ newResident.getName() ] = newResident

        return actorList



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    building = ApartmentBuilding("High Rise Apts", "Anywhere, USA")
    building.runModel( datetime.date(2016, 12, 15), datetime.date(2016, 12, 15) )
        
