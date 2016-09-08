#!/usr/bin/python3 

import logging
import abc

class ElevatorLogicModel:

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        return

    def getName(self):
        return self._name
