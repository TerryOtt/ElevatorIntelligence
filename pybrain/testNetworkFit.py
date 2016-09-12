#!/usr/bin/python3

import json
import pybrain.tools.customxml.networkreader
import logging
import argparse
import datetime
import pprint
import statistics
import random
import csv


def main():
    random.seed()
    args = parseArgs()

    activities = readActivities(args.activities_file)
    neuralNet = createNetworkFromFile(args.neuralnet_xml)
    stats = testFit(activities, neuralNet, args.output_csv)

    printStats(stats)


def parseArgs():
    parser = argparse.ArgumentParser(description="Elevator simulation driver for high rise apts w/ std logic")
    parser.add_argument('activities_file', help="Input JSON file with activities")
    parser.add_argument('neuralnet_xml', help='Input XML file with PyBrain XML neural net definition')
    parser.add_argument('output_csv', help='Output CSV to run through Excel to get box-whisker chart')

    return parser.parse_args()


def readActivities(activityFile):

    with open(activityFile, 'r') as activitiesJson:
        activities = json.load(activitiesJson)

    print("Read activities from {0}".format(activityFile) )

    return activities


def createNetworkFromFile(neuralNetXmlFile):

    neuralNet = pybrain.tools.customxml.networkreader.NetworkReader.readFrom(neuralNetXmlFile)

    print("Read neural net from {0}".format(neuralNetXmlFile) )

    return neuralNet


def testFit(activities, neuralNet, csvFilename):
    timestamps = sorted( activities.keys() )

    stats = {
        'numDatapoints': 0,
        'totalError': 0.0
    }

    stats['errorList'] = []
  
    with open(csvFilename, 'w', newline='') as outputCsv:
        csvWriter = csv.writer(outputCsv)
        csvWriter.writerow( [ "hour", "expected_output", "neural_net_output" ] )

        for currTimestamp in timestamps:
            entryTimestamp = datetime.datetime.strptime(currTimestamp, "%Y%m%d %H%M%S")
            # print( "Entry timestamp: {0}".format(entryTimestamp) )

            for currActivity in activities[currTimestamp]:
                if currActivity == None or 'activity_type' not in currActivity:
                    continue

                # Is it a button press?
                if currActivity['activity_type'] == "Request Elevator":
                    # print( "Button press at {0} on floor index {1}".format(
                    #     entryTimestamp, currActivity['start_floor']) )

                    neuralNetResult = activateNet(neuralNet, currTimestamp )
                    #neuralNetResult = (random.random() * 8) + 1

                    # print( "\tNeural net result: {0:5.3f}".format(
                    # neuralNetResult) )

                    # Write the data out to the CSV
                    csvWriter.writerow(
                        [ 
                            "Hour {0:02d}00".format(entryTimestamp.hour),
                            currActivity['start_floor'],
                            neuralNetResult
                        ]
                    )                

                errorDelta = abs(neuralNetResult - currActivity['start_floor'])

                # print( "\tError delta: {0:5.3f}".format(errorDelta) )

                stats['numDatapoints'] += 1
                stats['errorList'].append(errorDelta)
                stats['totalError'] += errorDelta

    return stats



def activateNet(neuralNet, entryTimestamp):

    inputVector =  convertDatetimeToNormalizedInputVector(entryTimestamp)
    #pprint.pprint(inputVector)
    #return None
    return neuralNet.activate( inputVector )[0]


def getOriginalInputValuesFromTimestamp(timestampString):

    timestamp = datetime.datetime.strptime( timestampString, "%Y%m%d %H%M%S" )

    year = timestamp.year
    dayOfYear = timestamp.timetuple()[7]
    secondOfDay = \
        (timestamp.hour * 3600) + \
        (timestamp.minute * 60) + \
        timestamp.second
    dayOfWeek = timestamp.isoweekday()

    return (year, dayOfYear, secondOfDay, dayOfWeek)


def convertDatetimeToNormalizedInputVector(entryTimestamp):

    # There are nine values in the input vector
    #
    #   Year          (gaussian normalized)
    #   Day of year   (gaussian normalized)
    #   Second of day (gaussian normalized)
    #   Six-bit dummy vector for day of week
    #       (  0  0  0  0  0  1 ) = Monday
    #       (  1  0  0  0  0  0 ) = Saturday
    #       ( -1 -1 -1 -1 -1 -1 ) = Sunday

    (year, dayOfYear, secondOfDay, dayOfWeek) = getOriginalInputValuesFromTimestamp(
        entryTimestamp )

    returnSequence = [
        gaussianNormalizeNumericInput( 'year', year ),
        gaussianNormalizeNumericInput( 'dayOfYear', dayOfYear ),
        gaussianNormalizeNumericInput( 'secondOfDay', secondOfDay ),
    ]

    returnSequence.extend(encodeDayOfWeek(dayOfWeek))

    return returnSequence


def gaussianNormalizeNumericInput( inputType, inputValue ):

    # Pulled from training activities data, 10 year run starting 2016-12-15
    stats = {
        'year': {
            'mean':      2021.45870,
            'stdev':        2.87825
        },

        'dayOfYear': {
            'mean':       182.80361,
            'stdev':      105.36360
        },

        'secondOfDay': {
            'mean':     46422.07271,
            'stdev':    20938.44370
        }
    }

    if inputType not in stats:
        raise ValueError("Unknown numeric stat type {0}".format(
            inputType) )

    relevantStats = stats[inputType]

    return ( (inputValue - relevantStats['mean']) / 
        relevantStats['stdev'] )


def encodeDayOfWeek(dayOfWeek):
    dayOfWeekEncoding = [ 0, 0, 0, 0, 0, 0 ]

    # Using 6-bit "one-of-(C-1) effect-coding" for day of week
    #
    #   ( 0  0  0  0  0  1) = Monday
    #   ( 0  0  0  0  1  0) = Tuesday
    #   ( 0  0  0  1  0  0) = Wednesday
    #   ( 0  0  1  0  0  0) = Thursday
    #   ( 0  1  0  0  0  0) = Friday
    #   ( 1  0  0  0  0  0) = Saturday
    #   (-1 -1 -1 -1 -1 -1) = Sunday


    # Using ISO day of week, so Monday = 1, Sunday = 7)
    if dayOfWeek < 7:
        # Monday needs to be bit 5. 6-1 = 5
        # Saturday is bit 6.        6-6 = 0
        dayOfWeekEncoding[ 6 - dayOfWeek ] = 1
    else:
        for i in range(6):
            dayOfWeekEncoding[i] = -1

    return dayOfWeekEncoding


def printStats(stats):

    numDatapoints   = stats['numDatapoints']
    totalError      = stats['totalError']
    minError        = min(stats['errorList'])
    meanError       = statistics.mean( stats['errorList'] )
    medianError     = statistics.median( stats['errorList'] ) 
    maxError        = max(stats['errorList'])

    # Measures of spread
    populationStdDev        = statistics.pstdev(stats['errorList'])
    #populationVariance      = statistics.pvariance(stats['errorList'])

    print( "Data points: {0:6d}\n".format(numDatapoints) )
    print( "Error:")
    print( "\t    Min: {0:6.3f}".format(minError) )
    print( "\t   Mean: {0:6.3f}".format(meanError) )
    print( "\t Median: {0:6.3f}".format(medianError) )
    print( "\t    Max: {0:6.3f}".format(maxError) )
    print( "\tStd dev: {0:6.3f}".format(populationStdDev) )
    #print( "\tVariance: {0:10.7f}".format(populationVariance) )



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

