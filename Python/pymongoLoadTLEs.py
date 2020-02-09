# -*- coding: utf-8 -*-

from skyfield import api
from skyfield.api import EarthSatellite
# from skyfield.constants import AU_KM, AU_M
# from skyfield.sgp4lib import TEME_to_ITRF
# from skyfield.api import Topos, load

import pymongo
from pymongo import MongoClient

def importCatalog(filename):
    fp = open(filename,"r")

    client = MongoClient()
    gemini2db = client['gemini2']
    tle_collection = gemini2db['tle_collection']

    while True:
        line1 = fp.readline()
        line2 = fp.readline()
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
        tle_id = tle_collection.insert_one(tleData).inserted_id

# Read a default file of satellite element sets into catalog[]
tleFilename = "/Users/kevinkelly/Desktop/Elsets/tle-2020-005.txt"
catalog = importCatalog(tleFilename)
