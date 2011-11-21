"""
Copyright (c) 2011 Rudy Hardeman (Zarya,PD0ZRY)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "Rudy Hardeman (zarya,PD0ZRY)"

#Private imports
import rotor
import debug
from audiorecord import Audio

#Global imports
import ephem
import math
import os
import sys
import time
import ConfigParser
from time import sleep
import Hamlib
import urllib2
from datetime import date, timedelta

def UpdateTLEs():
    basedate = date.today() - timedelta(days=1)
    try:
        used = os.stat(_config.get('Sats','keplerfile')).st_mtime
        year, day, month = time.localtime(used)[:3]
        lastused = date(year, day, month)
    except:
        lastused = date.today() - timedelta(days=2) 
    if lastused < basedate:
        tles = urllib2.urlopen(_config.get('Sats','keplerurl')).read()
        file = open(_config.get('Sats','keplerfile'), 'w')
        file.write(tles)
        file.close()
        del file
        return True
    else:
        return False

def GetTLEs():
    try:
        file = open(_config.get('Sats','keplerfile'), 'r')
    except:
        UpdateTLEs()
        file = open(_config.get('Sats','keplerfile'), 'r')
    tles = file.readlines()
    tles = [item.strip() for item in tles]
    tles = [tles[i:i+3] for i in xrange(0,len(tles)-2,3)]
    file.close()
    del file
    return tles

def GetSatData():
    file = open(_config.get('Sats','satdata'),'r')
    sats = file.readlines()
    sat_data = {} 
    for sat in sats:
        sat = sat.rstrip()
        sat = sat.split(',')
        if sat[0] != "SAT":
            sat_data[sat[0]]=[sat[1],sat[2],sat[3],sat[4],sat[5],sat[6]]
    file.close()
    del sats
    del file
    del sat
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

def WriteWebfile(string):
    global prev_string

    # Do not write the same data twice
    if string == prev_string:
    	return

    #Open webserver data file
    web_filename = "%s/%s" % (_config.get("Web",'path'), _config.get("Web",'file'))
    web = open("%s.tmp" % web_filename, 'w')
    web.write("Sat,EL,AZ,Upstream,Upstream_Modulation,Downstream,Downstream_Modulation\n")
    web.write(string)
    web.close()
    os.rename("%s.tmp" % web_filename, web_filename)

    prev_string = string

#Start main program
if __name__ == '__main__':
    #Read the config file
    _config = ConfigParser.ConfigParser()
    _config.readfp(open('pytracksat.conf'))

    #Radio location 
    _lat = _config.get('Location', 'lat')
    _lon = _config.get('Location', 'lon')

    #Webfile prev data string
    prev_string = ""

    #Create rotor control object
    Rotor = rotor.Rotor(_config.get('Rotor','port'),_config)

    #Create debug object
    Debug = debug.Debug(_config)

    #Hamlib
    if _config.getboolean('Radio','debug'):
        Hamlib.rig_set_debug (Hamlib.RIG_DEBUG_TRACE)
    else:
        Hamlib.rig_set_debug (Hamlib.RIG_DEBUG_NONE)

    rig = Hamlib.Rig(_config.getint('Radio','model'))
    try:
        rig.set_conf('rig_port',_radioport)
        rig.set_conf('rig_baudrate',_config.get('Radio','baudrate'))
    except:
        pass

    if _config.get('Radio','civaddr') != 0:
        rig.set_conf('rig_civaddr',_config.get('Radio','civaddr'))
    rig.open()


    #INIT RIG
    rig.set_vfo(Hamlib.RIG_VFO_MAIN)
    rig.set_vfo(Hamlib.RIG_VFO_B)
    rig.set_freq(_config.getint('Radio','rest_freq_vfoa'))
    rig.set_mode(SetMode(_config.get('Radio','rest_modulation_vfoa')))
    rig.set_vfo(Hamlib.RIG_VFO_SUB)
    rig.set_vfo(Hamlib.RIG_VFO_A)
    rig.set_freq(_config.getint('Radio','rest_freq_vfob'))
    rig.set_mode(SetMode(_config.get('Radio','rest_modulation_vfob')))

    #Load TLE's
    tles = GetTLEs()

    #Start audio class
    audio = Audio()
    current_sat = ""

    while True:
        observer = ephem.Observer()
        observer.lat = _lat
        observer.long = _lon

        if UpdateTLEs():
            del tles
            tles = GetTLEs()
    
        sat_found = []
        sat_data = GetSatData()
        for tle in tles:
            sat = ephem.readtle(tle[0],tle[1],tle[2])
            sat.compute(observer)
            if math.degrees(sat.alt) > 0 and math.degrees(sat.az) > 0 and math.degrees(sat.alt) < 180:
                if tle[0] in sat_data:
                    sat_found.append([tle[0],math.degrees(sat.alt),math.degrees(sat.az),sat_data[tle[0]][0],sat.range_velocity])
            del sat
        sat_found = sorted(sat_found, key=lambda sat: sat[3], reverse=True)
    
        #If no sats are found
        if len(sat_found) == 0:
            del Rotor
            Rotor = rotor.Rotor(_config.get('Rotor','port'),_config)
            Debug.write("NO SATS FOUND")
            Rotor.send(_config.getint('Rotor','rest_az'),_config.getint('Rotor','rest_el'))
            WriteWebfile("None,%03.1F,%03.1F,%3.4f,%s,%3.4f,%s\n"%
                (_config.getint('Rotor','rest_el'),_config.getint('Rotor','rest_az'),
                float(_config.getint('Radio','rest_freq_vfoa'))/1000000,
                _config.get('Radio','rest_modulation_vfoa'),
                float(_config.getint('Radio','rest_freq_vfob'))/1000000,
                _config.get('Radio','rest_modulation_vfob')))
            rig.set_vfo(Hamlib.RIG_VFO_MAIN)
            rig.set_freq(_config.getint('Radio','rest_freq_vfoa'))
            rig.set_mode(SetMode(_config.get('Radio','rest_modulation_vfoa')))
            rig.set_vfo(Hamlib.RIG_VFO_SUB)
            rig.set_freq(_config.getint('Radio','rest_freq_vfob'))
            rig.set_mode(SetMode(_config.get('Radio','rest_modulation_vfob')))
            del observer
            del sat_data
            del sat_found
            current_sat = ""
            sleep(1)
            continue

        if (current_sat != sat_found[0][0] and audio.run):
            audio.stop()
        if (sat_data[sat_found[0][0]][5] == "yes" and not audio.run):
            audio.start(sat_found[0][0])
     
        Debug.write(sat_found[0][0])
        Debug.write("Rotor: AZ: %03.1f EL: %03.1f" % (sat_found[0][2],sat_found[0][1]))
    
        #Move rotor
        Rotor.send(sat_found[0][2],sat_found[0][1])
    
        #Calculate frequentie information
        VFOA = int(sat_data[sat_found[0][0]][3])
        VFOA_Mhz = float(VFOA)/10000
        VFOA_Dopler = VFOA_Mhz * (1 - (sat_found[0][4] / 1000) / 299792)
    
        VFOB = int(sat_data[sat_found[0][0]][1])
        VFOB_Mhz = float(VFOB)/10000
        VFOB_Dopler = VFOB_Mhz * (1 - (sat_found[0][4] / 1000) / 299792)
    
        Debug.write("Snelheid: %s"%(sat_found[0][4] / 1000))
        Debug.write("Org. Upstream: %3.4f"%(float(VFOA)/10000))
        Debug.write("Org. Downstream: %3.4f"%(float(VFOB)/10000))
        Debug.write("Doppler VFOA: %3.8f %3.8f"%(VFOA_Dopler,1 - sat_found[0][4] / 299792))
        Debug.write("Doppler VFOB: %3.8f %3.8f"%(VFOB_Dopler,1 - sat_found[0][4] / 299792))
        
        #Write sat data to webserver file
        WriteWebfile("%s,%03.1F,%03.1F,%3.4f,%s,%3.4f,%s\n"%\
            (sat_found[0][0],sat_found[0][1],sat_found[0][2],\
            VFOA_Dopler,sat_data[sat_found[0][0]][4],\
            VFOB_Dopler,sat_data[sat_found[0][0]][2]))
    
        if int(sat_data[sat_found[0][0]][3]) != 0:
            rig.set_vfo(Hamlib.RIG_VFO_MAIN)
            rig.set_vfo(Hamlib.RIG_VFO_A)
            rig.set_freq(int(VFOA_Dopler*1000000))
            rig.set_mode(SetMode(sat_data[sat_found[0][0]][4]))

        rig.set_vfo(Hamlib.RIG_VFO_SUB)
        rig.set_vfo(Hamlib.RIG_VFO_B)
        rig.set_freq(int(VFOB_Dopler*1000000))
        rig.set_mode(SetMode(sat_data[sat_found[0][0]][2]))
        del observer
        del sat_data
        del sat_found
        sleep(1)
