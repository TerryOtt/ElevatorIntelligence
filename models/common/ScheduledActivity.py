#!/usr/bin/python3

import logging
import abc

class ScheduledActivity():

    __metaclass__ = abc.ABCMeta

    def __init__(self, activityStartTime, activityEndTime):
        self._log = logging.getLogger(__name__)
        self._activityStartTime = activityStartTime
        self._activityEndTime = activityEndTime
        self._activityDuration = activityEndTime - activityStartTime


    def getStartTime(self):
        return self._activityStartTime


    def getEndTime(self):
        return self._activityEndTime


    def getDuration(self):
        return self._activityDuration


    @abc.abstractmethod
    def getType(self):
        return
