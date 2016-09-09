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

    # There are seven values in the input vector
    #   
    #   Year        (normalized from 1970-2069)
    #   Month       (normalized from 1-12)
    #   Day         (normalized from 1-31)
    #   Day of week (normalized from 1-7)
    #   Hour        (normalized from 0-23)
    #   Minute      (normalized from 0-59)
    #   Second      (normalized from 0-59)
    inputNeurons = 7

    # There is one value in output vector
    #
    # Floor prediction (in range 0-1, need to multiply by number of floors to de-normalize)
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
    numInputDimensions = 7
    numTargetDimensions = 1
    
    dataset = pybrain.datasets.SupervisedDataSet( numInputDimensions, numTargetDimensions )

    for currFileName in os.listdir(jsonDir):
        joinedFile = os.path.join(jsonDir, currFileName)
        if os.path.isfile(joinedFile) is False:
            continue

        with open(joinedFile, "r") as currFile:
            dataDictionary = json.load(currFile)
            logging.warn("Read in JSON data from {0}".format(joinedFile) )

            # Add a sample for each entry
            for timestampString in dataDictionary.keys(): 
                currDateTime = datetime.datetime.strptime( timestampString, "%Y%m%d %H%M%S" )

                for currActivity in dataDictionary[timestampString]:

                    dataset.addSample(
                        # Input (timestamp of button press)
                        (
                            # Year (normalized from 0.0 = 1970 to 1.0 = 2069)
                            (currDateTime.year - 1970) / 100.0, 

                            # Month (normalized from 0.0 = Jan to 1.0 = Dec
                            (currDateTime.month - 1) / 1.0,

                            # Day (normalized from 0.0 = 1 to 1.0 = 31)
                            (currDateTime.day - 1) / 31.0,

                            # Day of month (normalized from 0.0 = Monday to 1.0 = Sunday)
                            currDateTime.date().weekday() / 6.0,

                            # Hour (normalized from 0.0 = 00:xx to 1.0 = 23:xx)
                            currDateTime.hour / 23.0,

                            # Minute (normalized from 0.0 = xx:00 to 1.0 = xx:59)
                            currDateTime.minute / 59.0,

                            # Second (normalized from 0.0 = xx:xx:00 to 1.0 = xx:xx:59)
                            currDateTime.second / 59.0
                        ),

                        # Target (floor of button press)
                        (
                            # Floor (normalized from G = 0.0 to floor 8 = 1.0)
                            (currActivity['start_floor'] - 1) / 8.0
                        )
                    )

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




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

