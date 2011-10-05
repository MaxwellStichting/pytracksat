import serial

class Rotor:
    def __init__(self,port,_config):
        self.ser = serial.Serial(port, 9600, timeout=1) 
        self._config = _config
 
    def send(self,az,el):
        if not self._config.getboolean('General','test'):
            self.ser.write("AZ%03.1F EL%03.1f\n"%(az,el))
        else:
            print "Rotor: AZ%03.1F EL%03.1f"%(az,el)

