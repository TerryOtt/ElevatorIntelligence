#!/usr/bin/python3

import json
import pybrain.tools.customxml.networkreader
import logging
import argparse
import datetime
import pprint
import csv


def main():
    args = parseArgs()

    neuralNet = createNetworkFromFile(args.neuralnet_xml)
    
    stats = writeNetResults(neuralNet, args.simulation_date, args.output_csv)


def parseArgs():
    parser = argparse.ArgumentParser(description="Elevator simulation driver for high rise apts w/ std logic")
    parser.add_argument('neuralnet_xml', help='Input XML file with PyBrain XML neural net definition')
    parser.add_argument('simulation_date', help='Format YYYYMMDD' )
    parser.add_argument('output_csv', help='Output data file')

    return parser.parse_args()



def createNetworkFromFile(neuralNetXmlFile):

    neuralNet = pybrain.tools.customxml.networkreader.NetworkReader.readFrom(neuralNetXmlFile)

    print("Read neural net from {0}".format(neuralNetXmlFile) )

    return neuralNet


def writeNetResults(neuralNet, simDate, csvFilename):
    simDate = datetime.datetime.strptime(simDate, "%Y%m%d")
    simTime = datetime.datetime(year=simDate.year, month=simDate.month, day=simDate.month)
    simEndTime = simTime + datetime.timedelta(days=1)

    simStep = datetime.timedelta(minutes=5)

    with open(csvFilename, 'w', newline='') as outputCsv:
        csvWriter = csv.writer(outputCsv)
        csvWriter.writerow( [ "timestamp", "network output" ] )

        while simTime < simEndTime:
             
            simTimestamp = simTime.strftime("%Y%m%d %H%M%S")
            neuralNetResult = activateNet(neuralNet, simTimestamp)

            # Write the data out to the CSV
            csvWriter.writerow(
                [ 
                    simTime.strftime("%H:%M:%S"),
                    neuralNetResult
                ]
            )                

            print( "Simulated time {0}".format(
                simTime.strftime("%H:%M:%S")) )

            # increment time
            simTime += simStep


def activateNet(neuralNet, entryTimestamp):

    inputVector =  convertDatetimeToNormalizedInputVector(entryTimestamp)
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

