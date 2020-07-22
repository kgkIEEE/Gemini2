# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 07:24:58 2020

@author: 17816
"""
import sys, getopt
import argparse

from skyfield import api
from skyfield.api import EarthSatellite
from skyfield.api import Topos, load
from skyfield import almanac

observerLatitude = 0.0
observerLongitude = 0.0
ts = api.load.timescale(builtin=True)
eph = api.load('de421.bsp')

groundStation = Topos(observerLatitude, observerLongitude)

# Find start and end of astronomical twilight on specified day
print("Get local astromical dusk and dawn")
times = ts.utc(2020, 6, 1, 12, range(2*1440))
t0 = times[0] # Start time
t1 = times[-1] # End time
print("Times: ",t0.tt,t1.tt,len(times))
f = almanac.dark_twilight_day(eph, groundStation)
t, y = almanac.find_discrete(t0, t1, f)
for ti, yi in zip(t, y):
    print(yi, ti.tt, ti.utc, ' Start of', almanac.TWILIGHTS[yi])