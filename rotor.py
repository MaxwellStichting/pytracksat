import serial

class Rotor:
    def __init__(self,port):
        self.ser = serial.Serial(port, 9600, timeout=1) 
         
    def send(self,az,el):
        self.ser.write("AZ%03.1F EL%03.1f\n"%(az,el))

