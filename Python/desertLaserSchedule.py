# -*- coding: utf-8 -*-

import json

# -*- coding: utf-8 -*-
import sys, getopt
import argparse

from skyfield import api
from skyfield.api import EarthSatellite
from skyfield.api import Topos, load
from skyfield import almanac

MAXDISTANCE = 1000000000.0

def findVisibility(eph, satellite, site, times, passes, trajectory):

    satellitePasses = []
    satelliteObservations = []
    aboveHorizon = False
    ts = load.timescale()
    riseTime = 0.
    setTime = 0.
    maxEl = 0.
    maxDistance = 0.
    minDistance = MAXDISTANCE

    difference = satellite - site
    topocentric = difference.at(times)
    geocentric = satellite.at(times)


    el, az, distance = topocentric.altaz()
    
    illuminated = False

    for i in range(len(el.degrees[:])):
        time = times[i].tt
        if el.degrees[i] > 0.0:
            sunlit = satellite.at(times[i]).is_sunlit(eph)
            if(sunlit):
                illuminated = True
            satelliteObservations.append((satellite.model.satnum, time,
                                          sunlit,
                                          distance.km[i], az.degrees[i], el.degrees[i],
                                          geocentric.position.km[0,i],
                                          geocentric.position.km[1,i],
                                          geocentric.position.km[2,i]))
            if(trajectory):
                print("Visible: ", f"{satellite.model.satnum:6d}", \
                    f"{distance.km[i]:10.3f}", f"{az.degrees[i]:7.2f}", f"{el.degrees[i]:7.2f}", \
                    times[i].tt, 
                    sunlit,
                      geocentric.position.km[0,i],
                      geocentric.position.km[1,i],
                      geocentric.position.km[2,i])
            if el.degrees[i] > maxEl:
                maxEl = el.degrees[i]
                maxEl_az = az.degrees[i]
                maxEl_range = distance.km[i]
            if aboveHorizon == False:
                # Satellite just rose above horizon
                riseTime = time
                riseAz = az.degrees[i]
            aboveHorizon = True
            if distance.km[i] < minDistance:
                minDistance = distance.km[i]
            if distance.km[i] > maxDistance:
                maxDistance = distance.km[i]
        else:
            if aboveHorizon == True:
                # Satellite just set
                setTime = time
                setAz = az.degrees[i]
                satellitePasses.append((satellite.model.satnum, \
                                        riseTime, (setTime-riseTime), \
                                            illuminated,
                                        int(maxEl+0.5), int(maxEl_az+0.5),\
                                        int(maxEl_range), int(riseAz+0.5), \
                                        int(setAz+0.5), int(minDistance), \
                                        int(maxDistance)))


                if(passes):
                    print("Pass:    ", f"{satellite.model.satnum:6d}", riseTime, \
                        f"{1440*(setTime-riseTime):7.2f}", \
                            illuminated,
                        int(maxEl+0.5), int(maxEl_az+0.5),\
                        int(maxEl_range), int(riseAz+0.5), \
                        int(setAz+0.5), int(minDistance), \
                        int(maxDistance))

                riseTime = 0.
                setTime = 0.
                maxEl = 0.
                aboveHorizon = False
                maxDistance = 0.
                minDistance = MAXDISTANCE
    return satellitePasses, satelliteObservations

def computeSchedule(eph, catalog,groundStation, times, passes, trajectory):
    passes = []
    observations = []
    for i in range(len(catalog)):
        satellitePasses, satelliteObservations = findVisibility(eph, catalog[i],
            groundStation, times, passes, trajectory)
        passes.append(satellitePasses)
        observations.append(satelliteObservations)
    return passes, observations

def readTLE(tleFilename):
    # Open TLE filename
    tleFile = open(tleFilename,'r')
    print("Opened TLE file: ",tleFilename)
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
            if line1[1:6] == line2[1:6]:
                catalog.append(EarthSatellite(line1,line2))
                line1 = None;
                line2 = None;
            else:
                print("Error: Satnumber in line 1 not equal to line 2",line1,line2)

    print("Read ", len(catalog), "TLEs into catalog")
    return catalog

def main(argv):

    # Defaults
    inputFile = 'catalogTest.txt'
    outputFile = 'scheduleTest.txt'
    start = "20200601"
    observerLatitude = 0.0
    observerLongitude = 0.0
    passes = True
    trajectory = True

    ts = api.load.timescale(builtin=True)
    eph = api.load('de421.bsp')

    groundStation = Topos(observerLatitude, observerLongitude)

    ts = load.timescale()
    times = ts.utc(2020, 6, 1, 18, range(700))
    print("Times: ",times[0], len(times), times[-1])
    
    catalog = readTLE(inputFile)
    passes, observations = computeSchedule(eph, catalog, groundStation, times, passes, trajectory)
    
    print("Passes:      ",len(passes))
    print("Observations:",len(passes))
    # print(json.dumps(passes))
    # print(json.dumps(observations))

if __name__ == "__main__":
   main(sys.argv[1:])

