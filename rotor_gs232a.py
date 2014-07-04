"""
Copyright (c) 2011 Rudy Hardeman (Zarya,PD0ZRY)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "Rudy Hardeman (zarya,PD0ZRY)"

import serial
from math import floor

class Rotor:
    def __init__(self,port,_config):
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
        except:
            try:
                self.ser = serial.Serial("%s1" % (port[:-1]), timeout=1)
            except:
                self.ser = serial.Serial("%s2" % (port[:-1]), timeout=1)
        self._config = _config
        self.az = 0
        self.el = 0
 
    def send(self,az,el):
        elold = 1
        if el > 89.9:
            return
        if el <= 0:
            elold = el
            el = 0
        if abs(float(self.az) - float(az)) > self._config.getfloat('Rotor','margin_az') or abs(float(self.el) - float(el)) > self._config.getfloat('Rotor','margin_el'):

            command = "W%03d %03d" % (az,el)

            if not self._config.getboolean('General','test'):
                self.ser.write("%s\n\r" % command)

            if self._config.getboolean('Debug','debug'):
                print command
                print "Moving rotor to: AZ: %03.1F EL: %03.1f"%(az,el)
            if elold <= 0:
                el = elold
            self.az = "%03F" % az
            self.el = "%03F" % el

