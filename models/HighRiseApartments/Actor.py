#!/usr/bin/python

import abc
import logging

class Actor:

    __metaclass__ = abc.ABCMeta

    def __init__(self, actorID):
        self._log = logging.getLogger(__name__)
        self._date = None
        self._actorID = None
        self._setActorID(actorID)


    def _setDate(self, todaysDate):
        self._today = todaysDate


    def _getDate(self):
        return self._today


    def _setActorID(self, actorId):
        self._actorID = actorId


    def getActorID(self):
        return self._actorID


    @abc.abstractmethod
    def startDailyActivities(self):
        return
