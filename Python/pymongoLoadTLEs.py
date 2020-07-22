# -*- coding: utf-8 -*-
import sys, getopt
import argparse
from skyfield import api
from skyfield.api import EarthSatellite
import pymongo
from pymongo import MongoClient

def importCatalog(filename):

    tleInserts = 0
    writeConcernError = 0
    writeError = 0
    print('Open ',filename)
    fp = open(filename,"r")
    if not fp:
        print('Error opening TLE file')
        exit()

    client = MongoClient()
    gemini2db = client['Gemini2']
    tle_collection = gemini2db['tle_collection']

    print('Read TLEs from',filename)
    while True:
        line1 = fp.readline()
        if line1:
            line2 = fp.readline()
            if line2:
                satellite = EarthSatellite(line1,line2)
                tleData = {"satnum":str(satellite.model.satnum),\
                "epochyr":satellite.model.epochyr,\
                "epochdays":satellite.model.epochdays,\
                "jdsatepoch":satellite.model.jdsatepoch,\
                "ndot":satellite.model.ndot,\
                "nddot":satellite.model.nddot,\
                "bstar":satellite.model.bstar,\
                "inclo":satellite.model.inclo,\
                "nodeo":satellite.model.nodeo,\
                "ecco":satellite.model.ecco,\
                "argpo":satellite.model.argpo,\
                "mo":satellite.model.mo,\
                "no":satellite.model.no, \
                "line1":line1, \
                "line2":line2}
                try:
                    tle_id = tle_collection.insert_one(tleData).inserted_id
                    tleInserts += 1
                except WriteConcernError as wce:
                    writeConcernError += 1
                    print(wce)
                except WriteError as we:
                    writeError += 1
                    print(we)
            else:
                break
        else:
            break

    return tleInserts, writeConcernError, writeError


def main(argv):

    # Defaults
    inputFile = 'C:\\Users\\17816\\Documents\\GitHub\\Gemini2\\Python\\catalogTest.txt' 
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('pymongoLoadTLEs.py -i <inputFile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('pymongoLoadTLEs.py -i <inputFile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFile = arg
    
    print('Insert TLEs from ',inputFile,' into MongoDB')
    
    tleInserts, writeConcernError, writeError = importCatalog(inputFile)
    print('Inserted ',tleInserts,' TLEs')
    print('Got ',writeConcernError,' write concern errors')
    print('Got ',writeError,' write errors')

if __name__ == "__main__":
   main(sys.argv[1:])