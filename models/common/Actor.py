#!/usr/bin/python3

import abc
import logging
import datetime
import pprint


class Actor:

    __metaclass__ = abc.ABCMeta

    def __init__(self, actorName, currDate):
        self._log = logging.getLogger(__name__)
        self._actorName = actorName
        self._currDate = currDate
        self._currLocation = None
        self._completedActivities = {} 
        self._pendingActivities = {}
        self._daysOfWeekNames = {
            'Monday'    : 1,
            'Tuesday'   : 2,
            'Wednesday' : 3,
            'Thursday'  : 4,
            'Friday'    : 5,
            'Saturday'  : 6,
            'Sunday'    : 7
        }
        self._earliestStartTime = datetime.datetime(currDate.year, currDate.month, currDate.day, 0,0,0)

        self._createActivities()

        self._log.info("Instantiated actor {0} on {1}".format( 
            self.getName(), currDate) )


    def getName(self):
        return self._actorName


    def getDate(self):
        return self._currDate


    def setLocation(self, location):
        self._currLocation = location


    def getLocation(self):
        return self._currLocation


    def _isWeekday(self):
        return self.getDate().isoweekday() < self._daysOfWeekNames["Saturday"]

   
    def _isWeekend(self):
        return not self._isWeekday()


    def _getDayOfWeekString(self):
        return self.getDate().strftime("%A")


    def _getEarliestStartTime(self):
        return self._earliestStartTime


    def _setEarliestStartTime(self, newStartTime):
        if newStartTime < self._earliestStartTime:
            raiseValueError("Cannot set earliest start time backwards")

        self._earliestStartTime = newStartTime
        self._log.debug("Earliest start time for {0} on {1} updated to {2}".format(
            self.getName(), self.getDate(), self._getEarliestStartTime()) )


    def _addPendingActivity(self, newActivity):
        # Make sure we're not overwriting something at the same time
        if newActivity.getStartTime() <= self._getEarliestStartTime():
            raise ValueError("Can't add event {0} for {1} at {2}; scheduling conflict, earliest start is {3}!".format(
                newActivity.getType(), self.getName(), newActivity.getStartTime(),
                self._getEarliestStartTime()) )

        self._pendingActivities[newActivity.getStartTime()] = newActivity

        # Update next possible time this person will be able do anything
        self._earliestStartTime = newActivity.getEndTime() + \
            datetime.timedelta(seconds=1)

        self._log.debug("\"{1}\" added activity \"{2}\", starting @ {0} until {3}, duration = {4}".format(
            newActivity.getStartTime(), self.getName(), newActivity.getDescription(), newActivity.getEndTime(),
            newActivity.getDuration()) )


        self._log.debug(pprint.pformat(self._pendingActivities))


    @abc.abstractmethod
    def _createActivities(self, currDate):
        return


    @abc.abstractmethod
    def startDailyActivities(self):
        return
