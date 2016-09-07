#!/usr/bin/python3

import logging
from models.HighRiseApartments.ApartmentBuilding import ApartmentBuilding
import datetime
import argparse
import os.path


def parseArgs():
    parser = argparse.ArgumentParser(description="Elevator simulation driver for high rise apts") 
    parser.add_argument('json_dir', help="Directory for JSON output")
    return parser.parse_args()


def main():
    args = parseArgs()
    
    if os.path.isdir(args.json_dir) is False:
        raise ValueError("{0} is not a valid directory for JSON output".format(
            args.json_dir) )

    timeToRun = datetime.timedelta(days=365)

    currDate = datetime.date( 2016, 12, 15 )
    with open( os.path.join(args.json_dir, "{0}{1}{2}.json".format(
            currDate.year, currDate.month, currDate.day)), "w") as outfile:
        bldg = ApartmentBuilding( "High Rise Apts", "Anywhere, USA" )
        bldg.runModel ( currDate, currDate + timeToRun, outfile )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
