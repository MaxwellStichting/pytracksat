"""
Copyright (c) 2011 Rudy Hardeman (Zarya,PD0ZRY)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "Rudy Hardeman (zarya,PD0ZRY)"

import serial

class Rotor:
    def __init__(self,port,_config):
        self.ser = serial.Serial(port, 9600, timeout=1) 
        self._config = _config
        self.az = 0
        self.el = 0
 
    def send(self,az,el):
        if el > 89.9:
            return
        if abs(float(self.az) - float(az)) > self._config.getfloat('Rotor','margin_az') or abs(float(self.el) - float(el)) > self._config.getfloat('Rotor','margin_el'):
            az_hondert = int(floor(az/100))
            az_tien = int(floor((az-100*az_hondert)/10))
            az_getallen = int(floor((az-100*az_hondert)-(az_tien*10)))

            el_hondert = int(floor(el/100))
            el_tien = int(floor((el-100*el_hondert)/10))
            el_getallen = int(floor((el-100*el_hondert)-(el_tien*10)))

            command = "573%s3%s3%s30013%s3%s3%s30012F20" % (az_hondert,az_tien,az_getallen,el_hondert,el_tien,el_getallen)

            if not self._config.getboolean('General','test'):
                self.ser.write(command.decode('hex'))

            if self._config.getboolean('Debug','debug'):
                print command
                print "Moving rotor to: AZ: %03.1F EL: %03.1f"%(az,el)
            self.az = "%03F" % az
            self.el = "%03F" % el

