import argparse
import csv

from skyfield import api
from skyfield.api import EarthSatellite
from skyfield.constants import AU_KM, AU_M
from skyfield.sgp4lib import TEME_to_ITRF
from skyfield.api import Topos, load


# Read TLE file and write key parameters in CSV format
def readTLE(tleFilename):
    # Open TLE filename
    tleFile = open(tleFilename,'r')
    # print("Opened TLE file: ",tleFilename)
    # Read TLEs into catalog
    catalog = []

    line0 = None
    line1 = None
    line2 = None

    for line in tleFile:
        if line[0] == '0':
            line0 = line
        elif line[0] == '1':
            line1 = line
        elif line[0] == '2':
            line2 = line
        else:
            # Error - TLE lines start with 0, 1 or 2
            print("Error: line does not start with 0, 1 or 2: ",line)

        if line1 and line2:
            # Check if object number is same in both line 1 and 2
            catalog.append(EarthSatellite(line1,line2))
            line1 = None;
            line2 = None;
    # print("Read ", len(catalog), "TLEs into catalog")
    return catalog

def writeSatelliteCSV(catalog, tleCSVFilename):
    with open(tleCSVFilename, 'w', newline='') as csvfile:

        fieldnames = ['satnum', 'epochyr', 'epochdays', 'jdsatepoch', 'ndot', \
            'nddot', 'bstar', 'inclination', 'rightascension', 'eccentricity', \
            'argofperigee', 'meanmotion', 'meananomaly']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for satellite in catalog:
            writer.writerow({\
                'satnum':satellite.model.satnum, \
                'epochyr':satellite.model.epochyr, \
                'epochdays':satellite.model.epochdays, \
                'jdsatepoch':satellite.model.jdsatepoch, \
                'ndot':satellite.model.ndot, \
                'nddot':satellite.model.nddot, \
                'bstar':satellite.model.bstar, \
                'inclination':satellite.model.inclo, \
                'rightascension':satellite.model.nodeo, \
                'eccentricity':satellite.model.ecco, \
                'argofperigee':satellite.model.argpo, \
                'meananomaly':satellite.model.mo, \
                'meanmotion':satellite.model.no})

def getUniqueSats(catalog):
    # Just get the first TLE for each satellite from catalog
    # Assumes that the TLE are ordered by satellite number
    uniqueSats = []
    satnum = 0
    for sat in catalog:
        if sat.model.satnum != satnum:
            uniqueSats.append(sat)
            satnum = sat.model.satnum
    return uniqueSats

def computeSchedule(site, catalog, tStart, tEnd):
    tList = []
    eventList = []
    for sat in catalog:
        t, events = sat.find_events(desertLaser, tStart, tEnd, altitude_degrees=5)
        tList.append(t)
        eventList.append(t)
    return tList, eventList

tleFilename = 'catalogTest.txt'
tleCSVFilename = 'catalogTest.csv'
schedFilename = 'catalogSched.csv'

catalog = readTLE(tleFilename)
writeSatelliteCSV(catalog,tleCSVFilename)
uniqueSats = getUniqueSats(catalog)

ts = load.timescale()
tStart = ts.utc(2020,1,1)
tEnd = ts.utc(2020,1,4)
desertLaser = Topos(21.0, 16.5, 100)

eph = load('de421.bsp')

times, events = computeSchedule(desertLaser, uniqueSats, tStart, tEnd)
for i in range(0,len(times)):
    satnum = uniqueSats[i].model.satnum
    difference = uniqueSats[i] - desertLaser
    t = times[i]
    sunlit = uniqueSats[i].at(t).is_sunlit(eph)
    for j in range(0,len(times[i])):
        topocentric = difference.at(t[j])
        alt, az, distance = topocentric.altaz()
        if(sunlit[j]):
            lit = 1
        else:
            lit = 0
        print(f'{satnum:6}',f'{(t[j]-tStart):8.5f}',
              f'{distance.km:8.2f}',
              f'{az.degrees:8.2f}',
              f'{alt.degrees:8.2f}',
              lit)
