#!/usr/bin/python3

import logging
import json
import pybrain
import pybrain.tools.shortcuts
import pybrain.tools.customxml.networkreader
import argparse


def main():
    args = parseArgs()

    activities = readActivities(args.activities_file)
    neuralNet = createNetworkFromFile(args.neuralnet_xml)

    testFit(activities, neuralNet)


def parseArgs():
    parser = argparse.ArgumentParser(description="Elevator simulation driver for high rise apts w/ std logic")
    parser.add_argument('activities_file', help="Input JSON file with activities")
    parser.add_argument('neuralnet_xml', help='Input XML file with PyBrain XML neural net definition')

    return parser.parse_args()


def readActivities(activityFile):

    with open(activityFile, 'r') as activitiesJson:
        activities = json.load(activitiesJson)

    logging.info("Read activities from {0}".format(activityFile) )

    return activities


def createNetworkFromFile(neuralNetXmlFile):

    neuralNet = pybrain.tools.shortcuts.buildNetwork(7, 4, 1, bias=True)
    pybrain.tools.customxml.networkreader.NetworkReader.readFrom(neuralNetXmlFile)

    logging.info("Read neural net from {0}".format(neuralNetXmlFile) )

    return neuralNet


def testFit(activities, neuralNet):
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
