"""
Copyright (c) 2011 Rudy Hardeman (Zarya,PD0ZRY)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "Rudy Hardeman (zarya,PD0ZRY)"

import pyaudio
import wave
import sys 
from multiprocessing import Process, Queue
from time import time, sleep
import os

class Audio:
    def __init__(self,config):
        self.run = False
        self.config = config
 
    def start(self,sat):
        filename = "%s%s-%s" % (self.config.get('Recording','path'),sat,time())
        self.filename = filename
        self.q = Queue()
        self.run = True
        self.p = Process(target=Wav, args=(self,filename,self.q))
        #self.p.daemon = True
        self.p.start()

    def stop(self):
        self.q.put("STOP")
        self.p.join()
        sleep(1) 
        self.run = False
        self.q.close()
        os.rename("%s" % self.filename, "%s.wav" % self.filename)
        sleep(1)


def Wav(audio,filename,q):
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
        channels = 1,
        rate = 44100,
        input = True,
        frames_per_buffer = 1024)
    wf = wave.open(filename, 'wb')
    wf.setframerate(44100)
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    run = True
    while run != "STOP":
        wf.writeframes(stream.read(1024))
        try:
            run = q.get(False)
        except:
            continue
    stream.close()
    p.terminate()
    wf.close()

