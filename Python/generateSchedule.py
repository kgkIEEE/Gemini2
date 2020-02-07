# -*- coding: utf-8 -*-

from skyfield import api
from skyfield.api import EarthSatellite
from skyfield.api import Topos, load

MAXDISTANCE = 1000000000.0

def findVisibility(satellite, site, times):

    satellitePasses = []
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

    for i in range(len(el.degrees[:])):
        if el.degrees[i] > 0.0:
            print("Visible: ", f"{satellite.model.satnum:6d}", times[i].utc_iso(), \
                f"{distance.km[i]:10.3f}", f"{az.degrees[i]:7.2f}", f"{el.degrees[i]:7.2f}", \
                times[i], geocentric.position.km[:,i])
            if el.degrees[i] > maxEl:
                maxEl = el.degrees[i]
                maxEl_az = az.degrees[i]
                maxEl_range = distance.km[i]
            if aboveHorizon == False:
                # Satellite just rose above horizon
                riseTime = times[i]
                riseAz = az.degrees[i]
            aboveHorizon = True
            if distance.km[i] < minDistance:
                minDistance = distance.km[i]
            if distance.km[i] > maxDistance:
                maxDistance = distance.km[i]
        else:
            if aboveHorizon == True:
                # Satellite just set
                setTime = times[i]
                setAz = az.degrees[i]
                if riseAz > 90 and riseAz < 270 and (setAz < 90 or setAz > 270):
                    direction = 'NB'
                elif setAz > 90 and setAz < 270 and (riseAz < 90 or riseAz > 270):
                    direction = 'SB'
                else:
                    direction = 'NA'
                satellitePasses.append((satellite.model.satnum, \
                                        riseTime, (setTime-riseTime), \
                                        direction, \
                                        int(maxEl+0.5), int(maxEl_az+0.5),\
                                        int(maxEl_range), int(riseAz+0.5), \
                                        int(setAz+0.5), int(minDistance), \
                                        int(maxDistance)))

                print("Pass:    ", f"{satellite.model.satnum:6d}", riseTime.utc_iso(), \
                    f"{1440*(setTime-riseTime):7.2f}", \
                    direction, \
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
    return satellitePasses

def computeSchedule(catalog,groundStation, times):
    passes = []
    for i in range(len(catalog)):
        passes.append(findVisibility(catalog[i],groundStation, times))
    return passes

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

groundStation = Topos('8.7 N', '167.7 W')
ts = load.timescale()
times = ts.utc(2020, 1, 1, 0, range(0,1440))

catalog = readTLE('catalogTest.txt')
schedule = computeSchedule(catalog, groundStation, times)

print("Schedule length:",len(schedule))
