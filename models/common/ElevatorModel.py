#/usr/bin/python3 

import logging
import models.common.ElevatorBank
import models.common.Elevator
import models.common.ElevatorLogicModelStandard

class ElevatorModel:

    def __init__(self, buildingName, buildingLocation):
        self._buildingName = buildingName
        self._buildingLocation = buildingLocation
        self._elevatorBanks = {}


    def createElevatorBank(self, bankName, bankLogic, elevatorList, floorList ):
        if bankName in self._elevatorBanks:
            raise ValueError("Cannot add bank {0}, already exists in model".format(
                bankName) )

        # Create the elevators specified
        newElevators = []
        for elevatorName in elevatorList:
            newElevators.append(models.common.Elevator.Elevator(elevatorName))

        self._elevatorBanks[bankName] = models.common.ElevatorBank.ElevatorBank(
            bankName, bankLogic, newElevators, floorList) 

    def processBankActivityList(self, bankName, activityList):
        self._log.info("Instructed to start processing activities for bank {0}".format(
            bankName) ) 

        self._elevatorBanks[bankName].processActivities(activityList)



if __name__ == "__main__":
    import random
    random.seed()
    logging.basicConfig(level=logging.DEBUG)
    eModel = ElevatorModel( "High Rise Apts", "Anywhere, USA" )
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

