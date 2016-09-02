#!/usr/bin/python3

import abc
import logging

class Actor:

    __metaclass__ = abc.ABCMeta

    def __init__(self, actorName, currDate):
        self._log = logging.getLogger(__name__)
        self._actorName = actorName
        self._currDate = currDate
        self._currLocation = None
        self._completedActivities = {} 
        self._pendingActivities = self._createActivities()

        self._log.info("Instantiated actor " + self.getName() )


    def getName(self):
        return self._actorName


    def getDate(self):
        return self._currDate


    def setLocation(self, location):
        self._currLocation = location


    def getLocation(self):
        return self._currLocation


    @abc.abstractmethod
    def _createActivities(self, currDate):
        return


    @abc.abstractmethod
    def startDailyActivities(self):
        return
