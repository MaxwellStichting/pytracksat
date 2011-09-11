# Script to see wat sats are in range 
#
# Rudy Hardeman (Zarya)
# with tnx to Joseph Armbruster for making the example

import ephem
import math
import os
import sys
import time
import urllib2

_latlong = ('51.44915','5.48776') # user lat/long

def GetTLEs():
    #tles = urllib2.urlopen('http://www.amsat.org/amsat/ftp/keps/current/nasabare.txt').readlines()
    tles = open('nasabare.txt', 'r').readlines()
    tles = [item.strip() for item in tles]
    tles = [(tles[i],tles[i+1],tles[i+2]) for i in xrange(0,len(tles)-2,3)]
    return tles

if __name__ == '__main__':
    observer = ephem.Observer()
    observer.lat = _latlong[0]
    observer.long = _latlong[1]
    tles = GetTLEs()

    sat_data = []
    sat_prio = {
        'OSCAR 8 (AO-8)':0,
        'UOSAT 4 (UO-15)':0, 
        'PHASE 3D (AO-40)':0, 
        'RUBIN-2 & SAFIR-M':6, 
        'SSETI EXPRESS (XO-53)':7,
        'DELFI-C3 (DO-64)':2,
        'HOPE-1 (HO-68)':10,
        'CUBESAT XI-IV (CO-57)':10,
    } 
    print "Sats in range:"
    for tle in tles:
        sat = ephem.readtle(tle[0],tle[1],tle[2])
        try:
            rt, ra, tt, ta, st, sa = observer.next_pass(sat)
        except:
            continue
        sat.compute(observer)
        if math.degrees(sat.alt) > 0 and math.degrees(sat.az) > 0:
            if tle[0] in sat_prio:
                sat_data.append((tle[0],math.degrees(sat.alt),math.degrees(sat.az),sat_prio[tle[0]]))
            else:
                sat_data.append((tle[0],math.degrees(sat.alt),math.degrees(sat.az),0))
            print "%s:\t\t %4.1f %5.1f" % (tle[0],math.degrees(sat.alt),math.degrees(sat.az))
    sat_data = sorted(sat_data, key=lambda sat: sat[3], reverse=True)
    print "Best sat in range:"
    print sat_data[0]
