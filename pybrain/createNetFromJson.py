#!/usr/bin/python3 

import logging
import pybrain
import pybrain.tools.shortcuts
import json
import argparse
import math
import os
import json


def main():
    args = parseArgs()

    # Create network, all neurons/synapses will have random weights
    neuralNet = createNet()

    # Create dataset
    dataset = createDataset(args.json_dir)
    


def parseArgs():
    argParser = argparse.ArgumentParser(description="Create neural net")
    argParser.add_argument('json_dir', help='Directory with JSON files')
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

    # Number of neurons in 
    return pybrain.tools.shortcuts.buildNetwork(
        inputNeurons,
        hiddenNeurons,
        outputNeurons )


def createDataset(jsonDir):
    for currFileName in os.listdir(jsonDir):
        joinedFile = os.path.join(jsonDir, currFileName)
        if os.path.isfile(joinedFile) is False:
            continue

        with open(joinedFile, "r") as currFile:
            dataDictionary = json.load(currFile)
            logging.warn("Read in JSON data from {0}".format(joinedFile) )
        


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
