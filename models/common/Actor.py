#!/usr/bin/python3

import abc
import logging

class Actor:

    __metaclass__ = abc.ABCMeta

    def __init__(self, actorID):
        self._log = logging.getLogger(__name__)
        self._actorID = None
        self._setActorID(actorID)


    def _setActorID(self, actorId):
        self._actorID = actorId


    def getActorID(self):
        return self._actorID


    @abc.abstractmethod
    def startDailyActivities(self, todaysDate):
        return
