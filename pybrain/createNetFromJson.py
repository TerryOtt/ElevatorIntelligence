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


def main():
    args = parseArgs()

    # Create network, all neurons/synapses will have random weights
    neuralNet = createNet()

    # Create dataset
    dataset = createDataset(args.json_dir)

    # Start the training phase (saves network when done)
    performTraining(neuralNet, dataset, args.network_dir, args.training_epochs)


def parseArgs():
    argParser = argparse.ArgumentParser(description="Create neural net")
    argParser.add_argument('json_dir', help='Directory with JSON files')
    argParser.add_argument('network_dir', help='Directory to save neural nets after training')
    argParser.add_argument('training_epochs', help='Number of training epochs to run', type=int)
    return argParser.parse_args()


def createNet():

    # There are nine values in the input vector
    #   
    #   Year        (gaussian normalized)
    #   DayOfYear   (gaussian normalized)
    #   SecondOfDay (gaussian normalized)
    #   Day of week (encoded in a 6-bit dummy vector)
    inputNeurons = 9

    # There is one value in output vector
    #
    # Floor prediction 
    outputNeurons = 1

    # Number of neurons in hidden layer
    #
    # Per web searching, good heuristic is to average number of input/output neurons
    hiddenNeurons = math.ceil((inputNeurons + outputNeurons) / 2)

    logging.info(
        "Creating neural net with {0} input neurons, {1} hidden neurons, {2} output neurons".format(
            inputNeurons, 
            hiddenNeurons, 
            outputNeurons) )

    # Do we want a bias?
    networkBias = True

    # Hidden class (SigmoidLayer or TanhLayer)
    hiddenClass = pybrain.structure.SigmoidLayer 

    # Number of neurons in 
    return pybrain.tools.shortcuts.buildNetwork(
        inputNeurons,
        hiddenNeurons,
        outputNeurons,
        bias=networkBias,
        hiddenclass=hiddenClass )


def createDataset(jsonDir):
    numInputDimensions = 9
    numTargetDimensions = 1
    
    dataset = pybrain.datasets.SupervisedDataSet( numInputDimensions, numTargetDimensions )

    for currFileName in os.listdir(jsonDir):
        joinedFile = os.path.join(jsonDir, currFileName)
        if os.path.isfile(joinedFile) is False:
            continue

        with open(joinedFile, "r") as currFile:
            dataDictionary = json.load(currFile)
            logging.warn("Read in JSON data from {0}".format(joinedFile) )

            stats = calculateGaussianNormalizationParameters(dataDictionary)

            # Add a sample for each entry
            for timestampString in dataDictionary.keys(): 

                for currActivity in dataDictionary[timestampString]:

                    # if the hash is empty or isn't a button press, ignore and try next
                    if currActivity == None or 'activity_type' not in currActivity:
                        continue

                    # Fully-normalized input values
                    inputValue =    getNormalizedInputValuesFromTimestamp(timestampString, stats)

                    targetValue = \
                        ( # Floor (target numerical values do not need to be normalized)
                            currActivity['start_floor'] 
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


def calculateGaussianNormalizationParameters(dataDictionary):
    normalizationParameters = {}

    numberButtonPresses = 0

    # Iterate over data to count button presses (used for numpy array creation
    for timestampString in dataDictionary.keys():
        for currActivity in dataDictionary[timestampString]:
            # if the hash is empty or isn't a button press, ignore
            if currActivity == None or 'activity_type' not in currActivity:
                continue

            else:
                numberButtonPresses += 1

    print( "Number of button presses: {0}".format(numberButtonPresses) )

    # Create the numpy arrays of appropriate size
    stats = {}
    for numericInputValue in [ 'year', 'dayOfYear', 'secondOfDay' ]:
        print( "Creating values array for {0}".format(numericInputValue) )
        stats[ numericInputValue ] = { 'values': np.zeros( numberButtonPresses ) }

    # Populate the value arrays
    currentEntryNumber = 0
    for timestampString in dataDictionary.keys():

        for currActivity in dataDictionary[timestampString]:

            # if the hash is empty or isn't a button press, ignore and try next
            if currActivity == None or 'activity_type' not in currActivity:
                continue

            (year, dayOfYear, secondOfDay, dayOfWeek) = getOriginalInputValuesFromTimestamp(
                timestampString )

            stats[ 'year'        ]['values'][currentEntryNumber] = year
            stats[ 'dayOfYear'   ]['values'][currentEntryNumber] = dayOfYear
            stats[ 'secondOfDay' ]['values'][currentEntryNumber] = secondOfDay

            # print( "Stats entry {0:3d} set to ({1}, {2}, {3})".format(
            #    currentEntryNumber, year, dayOfYear, secondOfDay) )

            currentEntryNumber += 1

    # Calculate the gaussian parameters, then drop references as they're no longer needed
    for numericInputValue in ( 'year', 'dayOfYear', 'secondOfDay' ):
        inputValue = stats[ numericInputValue ]
        values = inputValue['values']
        inputValue[ 'mean'  ] = np.mean( values )
        inputValue[ 'stdev' ] = np.std( values )

        # Drop reference to allow memory to be garbage collected if needed
        values = None

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
    return ( (originalValue - inputValueStats['mean']) / inputValueStats['stdev'] )


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


def getNormalizedInputValuesFromTimestamp(timestampString, stats):

    # Normalize all inputs to run through net
    #
    # For explanation of Gaussian normalization and 
    #   "one-of-(C-1) effects-coding", see
    #
    #   https://visualstudiomagazine.com/articles/2014/01/01/how-to-standardize-data-for-neural-networks.aspx

    (year, dayOfYear, secondOfDay, dayOfWeek) = getOriginalInputValuesFromTimestamp(
        timestampString )

    normalizedYear          = gaussianNormalizeNumericInput( 
        'year', year, stats )
    normalizedDayOfYear     = gaussianNormalizeNumericInput(
        'dayOfYear', dayOfYear, stats )
    normalizedSecondOfDay   = gaussianNormalizeNumericInput(
        'secondOfDay', secondOfDay, stats)

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
        for i in range(7):
            dayOfWeekEncoding[i] = -1

    return dayOfWeekEncoding
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

