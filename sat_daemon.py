# Script to see wat sats are in range 
#
# Rudy Hardeman (Zarya)
# with tnx to Joseph Armbruster for making the example

__author__ = "Rudy Hardeman (zarya)"

#Private imports
import rotor

#Global imports
import ephem
import math
import os
import sys
import time
import urllib2
import ConfigParser

#Hamlib
import Hamlib

_config = ConfigParser.ConfigParser()
_config.readfp(open('sat_daemon.conf'))

_latlong = (_config.get('Location', 'lat'),_config.get('Location', 'lon')) # user lat/long
#_radio = Hamlib.RIG_MODEL_IC910
_radio = Hamlib.RIG_MODEL_DUMMY
_radioport = _config.get('Radio','port') 

def GetTLEs():
    #tles = urllib2.urlopen('http://www.amsat.org/amsat/ftp/keps/current/nasabare.txt').readlines()
    tles = open(_config.get('Sats','keplerfile'), 'r').readlines()
    tles = [item.strip() for item in tles]
    tles = [tles[i:i+3] for i in xrange(0,len(tles)-2,3)]
    return tles

def GetSatData():
    sats = open(_config.get('Sats','satdata'),'r').readlines()
    sat_data = {} 
    for sat in sats:
        sat = sat.rstrip()
        sat = sat.split(',')
        if sat[0] != "SAT":
            sat_data[sat[0]]=[sat[1],sat[2],sat[3],sat[4],sat[5]]
    return sat_data        

def SetMode(mde):
    if mde == "LSB": 
        return Hamlib.RIG_MODE_LSB
    elif mde == "USB":
        return Hamlib.RIG_MODE_USB
    elif mde == "CW":
        return Hamlib.RIG_MODE_CW
    elif mde == "FM":
        return Hamlib.RIG_MODE_FM
    else:
        return Hamlib.RIG_MODE_AM


if __name__ == '__main__':

    #Hamlib
    # Uncomment this line for debug into from hamlib
    #Hamlib.rig_set_debug (Hamlib.RIG_DEBUG_TRACE)

    # Set for no debug output from hamlib
    Hamlib.rig_set_debug (Hamlib.RIG_DEBUG_NONE)

    rig = Hamlib.Rig(_radio)
    try:
        rig.set_conf(_radioport)
    except:
        pass 
    rig.open()
    

    #ephem
    observer = ephem.Observer()
    observer.lat = _latlong[0]
    observer.long = _latlong[1]
    tles = GetTLEs()

    #Create rotor control object
    Rotor = rotor.Rotor(_config.get('Rotor','port'))

    sat_found = []
    sat_data = GetSatData()
    for tle in tles:
        sat = ephem.readtle(tle[0],tle[1],tle[2])
        try:
            rt, ra, tt, ta, st, sa = observer.next_pass(sat)
        except:
            continue
        sat.compute(observer)
        if math.degrees(sat.alt) > 0 and math.degrees(sat.az) > 0:
            if tle[0] in sat_data:
                sat_found.append([tle[0],math.degrees(sat.alt),math.degrees(sat.az),sat_data[tle[0]][0],sat.range_velocity])
    sat_found = sorted(sat_found, key=lambda sat: sat[3], reverse=True)
    if len(sat_found) == 0:
        print "NO SATS FOUND"
        sys.exit()
    print sat_found[0][0]
    print "Rotor: %4.1f %5.1f" % (sat_found[0][1],sat_found[0][2])

    #Move rotor
    Rotor.send(sat_found[0][1],sat_found[0][2])

    #PROGRAM RADIO

    #VFOA == Upstream
    #VFOB == Downstream
    
    VFOA = int(sat_data[sat_found[0][0]][3])
    VFOB = int(sat_data[sat_found[0][0]][1])

    #Dopler calculation
    VFOA_Mhz = float(VFOA)/10000
    VFOB_Mhz = float(VFOB)/10000

    print "Snelheid: %s"%(sat_found[0][4] / 1000)
    print "Org. Upstream: %3.4f"%(float(VFOA)/10000)
    print "Org. Downstream: %3.4f"%(float(VFOB)/10000)
    print "Doppler VFOA: %3.4f %3.4f"%(VFOA_Mhz * (1 - (sat_found[0][4] / 1000) / 299792),1 - sat_found[0][4] / 299792)
    print "Doppler VFOB: %3.4f %3.4f"%(VFOB_Mhz * (1 - (sat_found[0][4] / 1000) / 299792),1 - sat_found[0][4] / 299792)

    VFOA = int(VFOA_Mhz * (1 - (sat_found[0][4] / 1000) / 299792) * 10000)
    VFOB = int(VFOB_Mhz * (1 - (sat_found[0][4] / 1000) / 299792) * 10000)

    rig.set_vfo(Hamlib.RIG_VFO_A)
    rig.set_freq(VFOA)
    rig.set_mode(SetMode(sat_data[sat_found[0][0]][4]))

    rig.set_vfo(Hamlib.RIG_VFO_B)
    rig.set_freq(VFOB)
    rig.set_mode(SetMode(sat_data[sat_found[0][0]][2]))

