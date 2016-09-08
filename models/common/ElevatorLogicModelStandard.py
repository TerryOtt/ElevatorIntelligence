#!/usr/bin/python3

import logging
import abc
import models.common.ElevatorLogicModel

class ElevatorLogicModelStandard(models.common.ElevatorLogicModel.ElevatorLogicModel):
    def __init__(self):
        self._name = "Logic Model - Standard"
