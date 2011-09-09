#!/usr/bin/python

import sys
import math
import ephem

obs = ephem.Observer()
obs.lat = '51.44915'
obs.long = '5.48776'

tles = open('nasabare.txt', 'r').readlines()
tles = [item.strip() for item in tles]
tles = [(tles[i],tles[i+1],tles[i+2]) for i in xrange(0,len(tles)-2,3)]

for tle in tles:
    if sys.argv[1] in tle[0]:
        sat = ephem.readtle(tle[0],tle[1],tle[2])
        tr, azr, tt, altt, ts, azs = obs.next_pass(sat)
#        print tle[0]
#        print ' Rise Time: ', ephem.localtime(tr)
#        print ' Rise Azimuth: ', math.degrees(azr)
#        print ' Transit Time: ', ephem.localtime(tt)
#        print ' Transit Altitude: ', math.degrees(altt)
#        print ' Set Time: ', ephem.localtime(ts)
#        print ' Set Azimuth: ', azs
        print """Date/Time (UTC)       Alt/Azim   Lat/Long  Elev"""
        print """====================================================="""
        while tr < ts:
            obs.date = tr
            sat.compute(obs)
            print "%s | %4.1f %5.1f | %4.1f %+6.1f | %5.1f" % \
                (ephem.localtime(tr),
                math.degrees(sat.alt),
                math.degrees(sat.az),
                math.degrees(sat.sublat),
                math.degrees(sat.sublong),
                sat.elevation/1000.)
            tr = ephem.Date(tr + 20.0 * ephem.second)
        print 
        obs.date = tr + ephem.minute
