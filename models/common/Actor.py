#!/usr/bin/python3

import abc
import logging

class Actor:

    __metaclass__ = abc.ABCMeta

    def __init__(self, actorName, startingLocation):
        self._log = logging.getLogger(__name__)
        self._actorName = actorName
        self._currLocation = startingLocation


    def getName(self):
        return self._actorName


    def getLocation(self):
        return self._currLocation


    @abc.abstractmethod
    def startDailyActivities(self, todaysDate):
        return
