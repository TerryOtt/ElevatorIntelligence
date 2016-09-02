#!/usr/bin/python3

import logging
from common.Building                        import Building
from HighRiseApartments.BuildingResident    import BuildingResident
from common.Location                        import Location
import datetime
import pprint

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
        resident = BuildingResident("819", 1, currDate)

        buildingLocations[resident.getLocation()].addActorToLocation(resident)
        actorList = { resident.getName(): resident }
        return actorList


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    building = ApartmentBuilding("High Rise Apts", "Anywhere, USA")
    building.runModel( datetime.date(2016, 12, 15), datetime.date(2016, 12, 15) )
        
