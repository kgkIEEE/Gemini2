# This file generates data simulating the breakup of
# a large object in a polar orbit that is struck by a
# smaller debris object

from random import uniform
from numpy.linalg import norm

from astropy import time
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

from skyfield.api import EarthSatellite, Topos, load

from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.spheroid_location import SpheroidLocation

line1 = '1  5398U 71067E   20004.97039155 +.00000142 +00000-0 +43247-4 0  9992'
line2 = '2  5398 087.6227 269.5184 0065476 094.7647 266.1031 14.33848082536070'

satellite = EarthSatellite(line1, line2)
print(satellite.epoch.utc_jpl())

ts = load.timescale()

# run the simulation for 1 day
durationSim = 1.0

tStart = satellite.epoch
tEnd = ts.tt(jd=(tStart.tt + durationSim))
# Get object state vector at time of breakup
# Use the time 12.5% into the evaluation period
tBreakup = ts.tt(jd=(tStart.tt + ((tEnd.tt - tStart.tt)/8)))

sensor = Topos('0.0 N', '0.0 W')
difference = satellite - sensor
print(difference)

# Start and end times
topocentric = difference.at(tBreakup)
alt, az, distance = topocentric.altaz()

# Simulate a number of pieces that are ejected randomly from the main body
nPieces = 4
nTimeSteps = 10
timeStep = 100
ejectionVelocity = 0.4 # km/sec

geocentric = satellite.at(tBreakup)
r = geocentric.position
v = geocentric.velocity
print('Breakup state vector', r, v)
print('Satnum:          ',satellite.model.satnum)
print('Epoch year:      ',satellite.model.epochyr) # Full four-digit year of this element set’s epoch moment.
print('Epoch days:      ',satellite.model.epochdays) # Fractional days into the year of the epoch moment.
print('JD sat epoch:    ',satellite.model.jdsatepoch)
print('NDot:            ',satellite.model.ndot)
print('NDDot:           ',satellite.model.nddot)
print('BStar:           ',satellite.model.bstar) # Ballistic drag coefficient B* in inverse earth radii.
print('Inclination:     ',satellite.model.inclo) # Inclination in radians.
print('Right Ascension: ',satellite.model.nodeo) # Right ascension of ascending node in radians.
print('Eccentricity:    ',satellite.model.ecco) # Eccentricity.
print('Arg of perigee:  ',satellite.model.argpo) # Argument of perigee in radians.
print('Mean anomaly:    ',satellite.model.mo) # Mean anomaly in radians.
print('Mean motion:     ',satellite.model.no) # Mean motion in radians per minute.

# Poliastro r and v vectors for the main body
rVector = [r.km[0], r.km[1], r.km[2]] * u.km
# vVector = [v.km_per_s[0], v.km_per_s[1], v.km_per_s[2]] * u.km/u.s

pieces = []
tB = Time(tBreakup.tt,format='jd',scale='utc')

for i in range(0,nPieces):
    # Get 3 random values
    randomVelocityDelta = [uniform(-1.,1.), uniform(-1.,1.), uniform(-1.,1.)]
    # Compute length and scale factor
    scale = ejectionVelocity/norm(randomVelocityDelta)
    scaledVelocityDelta = [scale*randomVelocityDelta[0], \
        scale*randomVelocityDelta[1], scale*randomVelocityDelta[2]]
    # Add the 3 random values to the velocity vector of the main body
    vVector = [(v.km_per_s[0]+scaledVelocityDelta[0]),\
        (v.km_per_s[1]+scaledVelocityDelta[1]), \
        (v.km_per_s[2]+scaledVelocityDelta[2])] * u.km/u.s
    pieces.append(Orbit.from_vectors(Earth, rVector, vVector, epoch=tB))

# Generate orbital element sets for the pieces
print('Pieces')
for piece in pieces:
    print('Piece:',piece)

pieceOrbits = []
for piece in pieces:
    rVector = []
    for i in range(0,nTimeSteps):
        rVector.append(piece.propagate(time.TimeDelta(timeStep * i * u.min)))
    print('rVector:',rVector)
    pieceOrbits.append(rVector)

# Find when pieces are visible to the sensor
#observing_time = Time(jd=tBreakup.tt)
#sensor_coordinates = [0.0 * u.deg, 0.0 * u.deg, 0 * u.m]
#sensorLocation = SpheroidLocation(*sensor_coordinates, Earth)
sensorLocation = EarthLocation(lat=45.0, lon=72.0, height=100.0)
angles = []
for i in range(0,nPieces):
    for j in range(0,nTimeSteps):
        r,v = pieceOrbits[i][j].rv()
        tVal = pieceOrbits[i][j].epoch
        # sat_angles = pieceOrbits[i][j].transform_to(\
        #     AltAz(\
        #     representation_type='cartesian',
        #     x=r[0], y=r[1], z=r[2],
        #     frame='gcrs',
        #     obstime=tVal,
        #     location=sensorLocation))
        sky_gcrs=SkyCoord(
            representation_type='cartesian',
            x=r[0], y=r[1], z=r[2],
            frame='gcrs')
        print('sky:',sky_gcrs)
        viewAngle = sky_gcrs.transform_to(AltAz(obstime=tVal,location=sensorLocation))
        angles.append(viewAngle)
        # pos_ecef = sky_gcrs.transform_to('itrs')
        print('Angles:',i,j,int(viewAngle.alt.value),int(viewAngle.az.value),r[0],r[1],r[2])
        # if sat_angles.alt > 0.0:
        #     print('Visible at ',i,j,tVal,sat_angles)
