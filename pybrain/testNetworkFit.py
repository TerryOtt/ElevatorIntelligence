#!/usr/bin/python3

import json
import pybrain.tools.shortcuts
import pybrain.tools.customxml.networkreader
import logging
import argparse
import datetime
import pprint


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

    print("Read activities from {0}".format(activityFile) )

    return activities


def createNetworkFromFile(neuralNetXmlFile):

    neuralNet = pybrain.tools.shortcuts.buildNetwork(7, 4, 1, bias=True)
    pybrain.tools.customxml.networkreader.NetworkReader.readFrom(neuralNetXmlFile)

    print("Read neural net from {0}".format(neuralNetXmlFile) )

    return neuralNet


def testFit(activities, neuralNet):
    timestamps = sorted( activities.keys() )

    stats = {
        'datapoints': 0,
        'totalError': 0.0
    }

    for currTimestamp in timestamps:
        entryTimestamp = datetime.datetime.strptime(currTimestamp, "%Y%m%d %H%M%S")
        # print( "Entry timestamp: {0}".format(entryTimestamp) )

        for currActivity in activities[currTimestamp]:
            # Is it a button press?
            if currActivity['activity_type'] == "Request Elevator":
                print( "Button press at {0} on floor index {1}".format(
                    entryTimestamp, currActivity['start_floor']) )

                neuralNetResult = activateNet(neuralNet, entryTimestamp)

                print( "Neural net result: {0:5.3f}".format(
                   neuralNetResult) )

                break

            break

        break


def activateNet(neuralNet, entryTimestamp):

    inputVector =  convertDatetimeToNormalizedInputVector(entryTimestamp)
    #pprint.pprint(inputVector)
    #return None
    return neuralNet.activate( inputVector )[0]



def convertDatetimeToNormalizedInputVector(entryTimestamp):

    # There are seven values in the input vector
    #
    #   Year        (normalized from 1970-2069)
    #   Month       (normalized from 1-12)
    #   Day         (normalized from 1-31)
    #   Day of week (normalized from 1-7)
    #   Hour        (normalized from 0-23)
    #   Minute      (normalized from 0-59)
    #   Second      (normalized from 0-59)
    return [
        normalizeYear(entryTimestamp.year),
        normalizeMonth(entryTimestamp.month),
        normalizeDay(entryTimestamp.day),
        normalizeWeekday(entryTimestamp.date().weekday()),
        normalizeHour(entryTimestamp.hour),
        normalizeMinute(entryTimestamp.minute),
        normalizeSecond(entryTimestamp.second)
    ]


def normalizeYear(year):
    return (year - 1970) / 100.0


def normalizeMonth(month):
    return (month - 1) / 1.0


def normalizeDay(day):
    return (day - 1) / 31.0


def normalizeWeekday(weekday):
    return weekday / 6.0


def normalizeHour(hour):
    return hour / 23.0


def normalizeMinute(minute):
    return minute / 59.0


def normalizeSecond(second):
    return second / 59.0



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

