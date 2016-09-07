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


    def getStartTimeString(self):
        return self.getStartTime().strftime("%Y%m%d %H%M%S")


    @abc.abstractmethod
    def getType(self):
        return
    

    @abc.abstractmethod
    def getDescription(self):
        return


    @abc.abstractmethod
    def getJsonDictionary(self):
        return
