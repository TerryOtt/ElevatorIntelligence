#!/usr/bin/python3 

import logging
import pybrain
import pybrain.tools.shortcuts
import pybrain.datasets
import pybrain.supervised.trainers
import pybrain.tools.customxml.networkwriter
import json
import argparse
import math
import os
import json
import datetime
import pprint
import numpy as np
import statistics


def main():
    args = parseArgs()

    # Create network, all neurons/synapses will have random weights
    neuralNet = createNet()

    # Create dataset
    dataset = createDataset(args.json_dir, args.normalization_dir)

    # Start the training phase (saves network when done)
    performTraining(neuralNet, dataset, args.network_dir, args.training_epochs)


def parseArgs():
    argParser = argparse.ArgumentParser(description="Create neural net")
    argParser.add_argument('json_dir', 
        help='Directory with JSON files')
    argParser.add_argument('normalization_dir', 
        help='Direction to save normalization param JSON file')
    argParser.add_argument('network_dir', 
        help='Directory to save neural nets after training')
    argParser.add_argument('training_epochs', 
        help='Number of training epochs to run', type=int)

    return argParser.parse_args()


def createNet():
    (inputNeurons, hiddenNeurons, outputNeurons, networkBias, 
        hiddenClass) = getNetworkParameters()

    return pybrain.tools.shortcuts.buildNetwork(
        inputNeurons,
        hiddenNeurons,
        outputNeurons,
        bias=networkBias,
        hiddenclass=hiddenClass )


def createDataset(jsonDir, normalizationDir):

    (numInputDimensions, ignoreParam, numTargetDimensions, ignoreParam, ignoreParam) = getNetworkParameters()
    
    dataset = pybrain.datasets.SupervisedDataSet( numInputDimensions, numTargetDimensions )

    for currFileName in os.listdir(jsonDir):
        joinedFile = os.path.join(jsonDir, currFileName)
        if os.path.isfile(joinedFile) is False:
            continue

        with open(joinedFile, "r") as currFile:
            dataDictionary = json.load(currFile)

        logging.warn("Read in JSON data from {0}".format(joinedFile) )

        calculatedStats = calculateInputDataStats(dataDictionary)

        normStats = calculateGaussianNormalizationParameters(calculatedStats)

        pprint.pprint(normStats)

        # raise RuntimeError("Break")

        # Write normalization stats out to JSON file for later reference
        persistNormParams(normStats, normalizationDir)

        # Add a sample for each entry
        for timestampString in sorted( calculatedStats.keys() ):

            # Fully-normalized input values
            inputValue = getNormalizedInputValuesFromTimestamp(timestampString, normStats)

            buttonStats = calculatedStats[timestampString]

            # Target numeric values do NOT need to be normalized
            targetValue = ( 
                buttonStats['floor']['q1'],     buttonStats['floor']['med'],     buttonStats['floor']['q3'], 
                buttonStats['nextpress']['q1'], buttonStats['nextpress']['med'], buttonStats['nextpress']['q3'] 
            )

            # print( "Timestamp {0} turned into sample {1} => {2}".format(
            #    timestampString, pprint.pformat(inputValue), 
            #    pprint.pformat(targetValue)) )

            dataset.addSample(inputValue, targetValue)

    return dataset
        

def performTraining( neuralNet, trainingDataset, networkSaveDir, numberOfTrainingEpochs ):

    # Make sure we have someplace to save data
    if os.path.isdir(networkSaveDir) is False:
        raise ValueError("Cannot save networks to {0}, not a directory".format(
            networkSaveDir) )

    trainer = pybrain.supervised.trainers.BackpropTrainer(neuralNet, trainingDataset, verbose=True)

    oldError = 0.0
    if numberOfTrainingEpochs > 0:
        for i in range(numberOfTrainingEpochs):
            logging.warn("\nTraining: starting epoch {0} / {1} @ {2}".format(
                i + 1, numberOfTrainingEpochs, datetime.datetime.utcnow()) )
            epochError = trainer.train()
            if oldError < 0.000000001:
                logging.warn("Training epoch complete, error = {0:1.010f}, time = {1}".format(
                    epochError, datetime.datetime.utcnow()) )
            else:
                logging.warn("Training epoch complete, error = {0:1.010f}, error delta = {1:2.010f}, time = {2}".format(
                    epochError, epochError - oldError, datetime.datetime.utcnow()) )

            # Save off data so far
            persistNetwork(neuralNet, networkSaveDir)

            # Update error so we can show change
            oldError = epochError

    else:
        logging.warn("Training: starting training @ {0}, running to convergence".format(
            datetime.datetime.utcnow()) )
        trainer.trainUntilConvergence(verbose=True, maxEpochs=500)
        logging.warn("Training: network converted @ {0}".format(
            datetime.datetime.utcnow()) )


def persistNetwork(neuralNet, networkSaveDir):
    currentDatetime = datetime.datetime.utcnow()
    filename = os.path.join( networkSaveDir, "ElevatorIntelligence-net-{0}.xml".format(
        currentDatetime.strftime("%Y%m%d%H%M%S")) )

    pybrain.tools.customxml.networkwriter.NetworkWriter.writeToFile( neuralNet, 
        filename )

    logging.warn("Wrote network to file {0}".format(filename) )


def persistNormParams(params, paramSaveDir):
    currentDatetime = datetime.datetime.utcnow()
    filename =  os.path.join( paramSaveDir, "ElevatorIntelligence-normparams-{0}.json".format(
        currentDatetime.strftime("%Y%m%d%H%M%S")) )

    with open(filename, 'w') as outputJson:
        json.dump(params, outputJson)




def calculateGaussianNormalizationParameters(buttonStats):
    normalizationParameters = {}

    sortedTimestamps = sorted(buttonStats.keys())
    numberButtonPresses = len(sortedTimestamps)

    print( "Number of button presses: {0}".format(len(sortedTimestamps)) )

    # Create the numpy arrays of appropriate size
    stats = {}
    for numericInputValue in [ 'year', 'dayOfYear', 'secondOfDay', 
            'floor_q1',     'floor_med',     'floor_q3', 
            'nextpress_q1', 'nextpress_med', 'nextpress_q3' ]:
        print( "Creating values array for {0}".format(numericInputValue) )
        stats[ numericInputValue ] = { 'values': np.zeros( numberButtonPresses ) }

    # Populate the value arrays
    currentEntryNumber = 0
    for timestampString in sortedTimestamps:

        (year, dayOfYear, secondOfDay, dayOfWeek) = getOriginalInputValuesFromTimestamp(
            timestampString )

        currStats = buttonStats[timestampString]

        stats[ 'year'         ]['values'][currentEntryNumber] = year
        stats[ 'dayOfYear'    ]['values'][currentEntryNumber] = dayOfYear
        stats[ 'secondOfDay'  ]['values'][currentEntryNumber] = secondOfDay
        stats[ 'floor_q1'     ]['values'][currentEntryNumber] = currStats['floor']['q1']
        stats[ 'floor_med'    ]['values'][currentEntryNumber] = currStats['floor']['med']
        stats[ 'floor_q3'     ]['values'][currentEntryNumber] = currStats['floor']['q3']
        stats[ 'nextpress_q1' ]['values'][currentEntryNumber] = currStats['nextpress']['q1']
        stats[ 'nextpress_med']['values'][currentEntryNumber] = currStats['nextpress']['med']
        stats[ 'nextpress_q3' ]['values'][currentEntryNumber] = currStats['nextpress']['q3']

        currentEntryNumber += 1

    # Calculate the gaussian parameters, then drop references as they're no longer needed
    for numericInputValue in ( 'year', 'dayOfYear', 'secondOfDay', 
            'floor_q1', 'floor_med', 'floor_q3', 
            'nextpress_q1', 'nextpress_med', 'nextpress_q3' ):
        inputValue = stats[ numericInputValue ]
        values = inputValue['values']
        inputValue[ 'mean'  ] = np.mean( values )
        inputValue[ 'stdev' ] = np.std( values )

        # Remove data from array as we no longer want/need it
        inputValue.pop('values', None)

        print( "Numeric Input Value = {0}, mean = {1:8.5f}, standard dev = {2:8.5f}".format(
            numericInputValue, inputValue[ 'mean' ], inputValue[ 'stdev' ]) )        

    return stats


def gaussianNormalizeNumericInput(valueType, originalValue, stats):
    if valueType not in stats:
        raise ValueError("Value type of {0} is not known!".format(valueType) )

    # Gaussian normalization - subtract mean from value (center on zero), then divide by
    #       std deviation 
    #
    # This results in values from roughly -10 to 10, centered on zero

    inputValueStats = stats[valueType]

    if inputValueStats['stdev'] != 0.0:
        retVal = (originalValue - inputValueStats['mean']) / inputValueStats['stdev'] 
    else:
        retVal = 0.0

    return retVal


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


def getNormalizedInputValuesFromTimestamp(timestampString, normalizationStats):

    # Normalize all inputs to run through net
    #
    # For explanation of Gaussian normalization and 
    #   "one-of-(C-1) effects-coding", see
    #
    #   https://visualstudiomagazine.com/articles/2014/01/01/how-to-standardize-data-for-neural-networks.aspx

    (year, dayOfYear, secondOfDay, dayOfWeek) = getOriginalInputValuesFromTimestamp(
        timestampString )

    normalizedYear          = gaussianNormalizeNumericInput( 
        'year', year, normalizationStats )
    normalizedDayOfYear     = gaussianNormalizeNumericInput(
        'dayOfYear', dayOfYear, normalizationStats )
    normalizedSecondOfDay   = gaussianNormalizeNumericInput(
        'secondOfDay', secondOfDay, normalizationStats)

    dayOfWeekEncoding = encodeDayOfWeek(dayOfWeek)

    normalizedInputValues = \
        (
            normalizedYear,
            normalizedDayOfYear,
            normalizedSecondOfDay,
            dayOfWeekEncoding[0],
            dayOfWeekEncoding[1],
            dayOfWeekEncoding[2],
            dayOfWeekEncoding[3],
            dayOfWeekEncoding[4],
            dayOfWeekEncoding[5]
        )

    return normalizedInputValues


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
    

def getNetworkParameters():

    # There are nine values in the input vector
    #
    #   Year        (gaussian normalized)
    #   DayOfYear   (gaussian normalized)
    #   SecondOfDay (gaussian normalized)
    #   Day of week (encoded in a 6-bit vector)
    inputNeurons = 9

    # There are six values in output vector 
    #
    #   First three show confidence range of next-floor predictions valid over the next 60 minutes
    #
    #       1st quartile (Q1)
    #       2nd quartile (median, or med)
    #       3rd quartile (Q3)
    #
    #   Last three show confidence range of time until next request (in seconds) over the next 60 mins
    #
    #       1st quartile (Q1)
    #       2nd quartile (median, or med)
    #       3rd quartile (Q3)
    #
    #   Combine the two and system has a prediction of both WHERE and WHEN next request will be
    outputNeurons = 6

    # Number of neurons in hidden layer
    #
    # Per web searching, good heuristic is to average number of input/output neurons
    hiddenNeurons = math.ceil((inputNeurons + outputNeurons) / 2)

    # Do we want a bias?
    networkBias = True

    # Hidden class (SigmoidLayer or TanhLayer)
    hiddenClass = pybrain.structure.SigmoidLayer

    return (inputNeurons, hiddenNeurons, outputNeurons, networkBias, hiddenClass)


def calculateInputDataStats(dataDictionary):
    dictionaryKeys = sorted( dataDictionary.keys() )
    stats = {}

    for startKeyIndex in range(len(dictionaryKeys)):

        if (startKeyIndex + 1) % 1000 == 0:
            print( "Processing timestamp {0:6d}/{1:6d}".format(
                startKeyIndex + 1, len(dictionaryKeys)) )

        currKey = dictionaryKeys[startKeyIndex]
        startTime = datetime.datetime.strptime(currKey, "%Y%m%d %H%M%S")

        for currActivity in dataDictionary[currKey]:

            if currActivity == None or 'activity_type' not in currActivity or \
                    currActivity['activity_type'] != 'Request Elevator':
                continue 
            # Find out how many datapoints are within an hour of this button press
            endTime = startTime + datetime.timedelta(hours=1)

            endTimestamp = endTime.strftime("%Y%m%d %H%M%S")

            #print( "\nSearch start time = {0}, end = {1}".format(currKey, endTimestamp) )

            floorArray = []
            nextTimeArray = []
            buttonStats = { 'floor': {}, 'nextpress': {} }

            probeIndex = startKeyIndex 
            probeTimestamp = dictionaryKeys[probeIndex]
            previousTimestamp = probeTimestamp
            while probeIndex < len(dictionaryKeys) and probeTimestamp < endTimestamp:
                probeTimestamp = dictionaryKeys[probeIndex]
                #print( "Found timestamp within range: {0}".format(probeTimestamp) )

                # Find all button presses at this time
                for currActivity in dataDictionary[probeTimestamp]:
                    if currActivity == None or 'activity_type' not in currActivity or \
                            currActivity['activity_type'] != 'Request Elevator':
                        continue

                    floorNumber = currActivity['start_floor']
                    # print("Found button press at {0} on floor index {1}".format(
                    #   probeTimestamp, floorNumber) )
                    floorArray.append(floorNumber)

                    # Add time between last two button presses as long as this isn't
                    #       first in list
                    if probeIndex > startKeyIndex:
                        deltaSeconds = timeDeltaBetweenTimestamps(
                            probeTimestamp, previousTimestamp).total_seconds()
                        nextTimeArray.append(deltaSeconds)
                        # print( "Added time delta between presses of {0} seconds".format(
                        #   deltaSeconds) )

                probeIndex += 1
                previousTimestamp = probeTimestamp

            # Calculate boxplot stats for this period
            statsArray = np.array(floorArray)
            (buttonStats['floor']['q1'], buttonStats['floor']['med'], 
                buttonStats['floor']['q3']) = np.percentile(statsArray, [25, 50, 75])

            if len(nextTimeArray) > 0:
                statsArray = np.array(nextTimeArray)
                (buttonStats['nextpress']['q1'], buttonStats['nextpress']['med'],
                    buttonStats['nextpress']['q3']) = np.percentile(statsArray, [25, 50, 75])
            else:
                (buttonStats['nextpress']['q1'], buttonStats['nextpress']['med'],
                    buttonStats['nextpress']['q3']) = (0, 0, 0)

            stats[ currKey ] = buttonStats

            #printStats(buttonStats)

            #raise RuntimeError("Breakpoint")

    # pprint.pprint(stats)


    return stats


def timeDeltaBetweenTimestamps(timestampOne, timestampTwo):
    tsOne = datetime.datetime.strptime(timestampOne, "%Y%m%d %H%M%S")
    tsTwo = datetime.datetime.strptime(timestampTwo, "%Y%m%d %H%M%S")

    return tsOne - tsTwo


def printStats(stats):
    print( "Q3: {1:6.3f}\nMed: {2:6.3f}\n Q1: {3:6.3f}\nStandard Dev: {4:6.3f}".format(
        stats['q3'], stats['med'], stats['q1']) )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

