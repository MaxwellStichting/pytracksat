# Script to see wat sats are in range 
#
# Rudy Hardeman (Zarya)
# Part of the code from Joseph Armbruster reused

import re
from dateutil import parser
from datetime import timedelta
import datetime
import ephem
import math
import os
import sys
import time
import urllib2

_latlong = ('51.44915','5.48776') # user lat/long
_notify = 30 # let us know this many minutes in advance to a pass
_usevoice = False # use voice?
_statussleep = 1 # how many minutes to sleep between status updates

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
    now = datetime.datetime.now()

    # iterate through all the two line element sets
    for tle in tles:
        try:
            f = open('satdata/%s.txt'%(re.sub('[^-a-zA-Z0-9_.() ]+', '',tle[0])),'r')
        except:
            f = open('satdata/%s.txt'%(re.sub('[^-a-zA-Z0-9_.() ]+', '',tle[0])),'w')
            f.close()
            continue
        sat = ephem.readtle(tle[0],tle[1],tle[2])
        try:
            rt, ra, tt, ta, st, sa = observer.next_pass(sat)
            localrisetime = ephem.localtime(rt)
        except:
            continue
        timeuntilrise = localrisetime-now
        minutesaway = timeuntilrise.seconds/60.0
        sat.compute(observer)
        sat_data = f.readlines()
        sat_data = [item.strip() for item in sat_data]
        f.close()
        try:
            sat_data[0] = parser.parse(sat_data[0])
        except: 
            f = open('satdata/%s.txt'%(re.sub('[^-a-zA-Z0-9_.() ]+', '',tle[0])),'w')
            f.write(str(ephem.localtime(rt)))
            f.write('\n')
            f.write(str(ephem.localtime(tt)))
            f.write('\n')
            f.write(str(ephem.localtime(st)))
            f.write('\n')
            f.close()
            continue
        if sat_data[0] < ephem.localtime(rt):
            if sat_data[0] < now and parser.parse(sat_data[2]) > now:
                sat.compute(observer)
                rt, ra, tt, ta, st, sa = observer.next_pass(sat)
                print tle[0]
                print ' Rise Time: ', str(sat_data[0]) 
                print ' Transit Time: ', sat_data[1]
                print ' Set Time: ', sat_data[2]
                print "%4.1f %5.1f" % (math.degrees(sat.alt),math.degrees(sat.az))
        else:
            f = open('satdata/%s.txt'%(re.sub('[^-a-zA-Z0-9_.() ]+', '',tle[0])),'w')
            f.write(str(ephem.localtime(rt)))
            f.write('\n')
            f.write(str(ephem.localtime(tt)))
            f.write('\n')
            f.write(str(ephem.localtime(st)))
            f.write('\n')
            f.close()
