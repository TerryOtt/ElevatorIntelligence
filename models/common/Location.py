#!/usr/bin/python3

import logging

class Location:

    def __init__(self, locationName):
        self._log = logging.getLogger(__name__)
        self._name = locationName
        self._actors = {}


    def getName(self):
        return self._name


    def getActors(self):
        return self._actors


    def getActorCount(self):
        return len(self._actors)


    def addActorToLocation(self, actor):
        self._log.debug("Adding actor {0} to location {1}".format(
            actor.getName(), self.getName()) )

        if actor.getName() in self._actors:
            raise ValueError("Actor {0} already in location {1}!".format(
                actor.getName(), self.getName()) )

        self._actors[actor.getName()] = actor
        
        self._log.info("Successfully added actor {0} to location {1}".format(
            actor.getName(), self.getName()) )
