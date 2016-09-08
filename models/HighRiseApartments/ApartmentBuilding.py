#!/usr/bin/python3

import logging
from models.common.Building                         import Building
from models.HighRiseApartments.BuildingResident     import BuildingResident
from models.common.Location                         import Location
import models.common.ElevatorModel                    
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
        eModel = models.common.ElevatorModel.ElevatorModel( "High Rise Apts", "Anywhere, USA" )
        floorList = [
            "Floor G",
            "Floor 1",
            "Floor 2",
            "Floor 3",
            "Floor 4",
            "Floor 5",
            "Floor 6",
            "Floor 7",
            "Floor 8"
        ]

        logicModel = models.common.ElevatorLogicModelStandard.ElevatorLogicModelStandard()

        eModel.createElevatorBank( "Elevator Bank - Middle", logicModel, [ "Middle Elevator" ], floorList )

        return eModel



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
        
