import time
from time import sleep
import os
import urllib2
import socket
from gpiozero import PhaseEnableMotor
from threading import Thread
import threading

class Console(object):
    def __init__(self, transpose = 0):
        print "Initializing console object."
        self.__transpose = transpose

    def play(self, note):
        print note + self.__transpose

    def stop(self, note):
        print '-', note + self.__transpose

class Ring(object):
    __noteMap = {}
    __transpose = 0

    def __init__(self, hostMap, transpose = 0, dupes = False):
        print "Initializing beep object and performing name lookup."
        self.__transpose = transpose
        self.__dupes = dupes
        for host, notes in hostMap.items():
            try:
                name = socket.gethostbyname(host)
                i = 0
                for n in notes:
                    self.__noteMap[n] = 'http://'+name+'/'+str(i)
                    i += 1
            except:
                print "could not resolve " + host

        print self.__noteMap
        self.wake()
        time.sleep(2)

    def wake(self):
        for note, url in sorted(self.__noteMap.items()):
            self.play(note, transpose=False)

    def play(self, note, transpose=True):
        if transpose:
            note += self.__transpose

        if (note > 127 or note < 0):
            print "Note number out of range! " + str(note)
            return

        if note in self.__noteMap:
            response = urllib2.urlopen(self.__noteMap[note])
        else:
            print "No bell for note " + str(note)

    def stop(self, note):
        pass

class Beep(object):
    __transpose = 0
    __available = []
    __notes = {n: [] for n in range(128)}
    __dupes = False
    __hosts = None

    def __init__(self, hosts, transpose = 0, dupes = False):
        print "Initializing beep object and performing name lookup."
        self.__transpose = transpose
        self.__dupes = dupes
        for h in hosts:
            try:
                name = socket.gethostbyname(h)
                self.__available.append(name)
            except:
                print "could not resolve " + h

        self.__hosts = list(self.__available) # make copy for __del__

    def wake(self):
        for h in self.__hosts:
            response = urllib2.urlopen("http://" + h + "/?note=0")

    def play(self, note):
        note += self.__transpose
        #print note
        if (note > 127 or note < 0):
            print "Note number out of range! " + str(note)
            return

        if len(self.__available) > 0:
            if len(self.__notes[note]) == 0 or self.__dupes:
                device = self.__available.pop(0)
                self.__notes[note].append(device)

                f = int((2 ** ((note - 69.0)/12)) * 440)
                response = urllib2.urlopen("http://" + device + "/?note=" + str(f))
                #    print device + "/?note=" + str(f)
            else:
                pass
                #print "dupe not allowed for " + str(note)
        else:
            pass
            #print "not enough beacons (" + str(note) + ")"

    def stop(self, note):
        note += self.__transpose
        if (note > 127 or note < 0):
            print "Cannot play note number out of range! " + str(note)
            return
        
        if len(self.__notes[note]) > 0:
            device = self.__notes[note].pop()
            response = urllib2.urlopen("http://" + device + "/?note=0")
            self.__available.append(device)

            #print device + "/?note=0"

        else:
            pass
            #print "not playing (" + str(note) + ")"

    def __del__(self):
        for h in self.__hosts:
            response = urllib2.urlopen("http://" + h + "/?note=0")

class Swing(object):
    __noteMap = {}
    __transpose = 0

    def __init__(self, transpose = 0, dupes = False):
        print "Initializing swing object and setting up motors."
        self.__transpose = transpose
        self.__dupes = dupes
        motor1 = PhaseEnableMotor(17, 4)
        motor2 = PhaseEnableMotor(27, 18)
        motor3 = PhaseEnableMotor(23, 22)
        motor4 = PhaseEnableMotor(25, 24)
        motor5 = PhaseEnableMotor(6, 5)
        motor6 = PhaseEnableMotor(13, 12)
        motor7 = PhaseEnableMotor(16, 19)
        motor8 = PhaseEnableMotor(20, 26)
        self.__noteMap[110] = {"motor": motor1, "direction": "forward"}
        self.__noteMap[93] =  {"motor": motor1, "direction": "backward"}
        self.__noteMap[98] =  {"motor": motor2, "direction": "forward"}
        self.__noteMap[100] = {"motor": motor2, "direction": "backward"}
        self.__noteMap[104] = {"motor": motor3, "direction": "forward"}
        self.__noteMap[102] = {"motor": motor3, "direction": "backward"}
        self.__noteMap[114] = {"motor": motor4, "direction": "forward"}
        self.__noteMap[103] = {"motor": motor4, "direction": "backward"}
        self.__noteMap[116] = {"motor": motor5, "direction": "forward"}
        self.__noteMap[105] = {"motor": motor5, "direction": "backward"}
        self.__noteMap[117] = {"motor": motor6, "direction": "forward"}
        self.__noteMap[107] = {"motor": motor6, "direction": "backward"}
        self.__noteMap[115] = {"motor": motor7, "direction": "forward"}
        self.__noteMap[109] = {"motor": motor7, "direction": "backward"}
        self.__noteMap[112] = {"motor": motor8, "direction": "forward"}
        self.__noteMap[111] = {"motor": motor8, "direction": "backward"}
                                       
        #for motornum, notes, gpio in self.notes():
            #try:
                #print "tryblock"
            #except:
                #print "Error mapping motor"

        print self.__noteMap
        self.wake()
        time.sleep(2)

    def wake(self):
        for note, url in sorted(self.__noteMap.items()):
            self.play(note, transpose=False)

    def play(self, note, transpose=True):
        if transpose:
            note += self.__transpose
            print str(self.__transpose)

        if (note > 127 or note < 0):
            print "Note number out of range! " + str(note)
            return

        if note in self.__noteMap:
            event = threading.Event()
            print "would play a note here " + str(self.__noteMap[note])
            print str(self.__noteMap[note]['motor'])
            if self.__noteMap[note]['direction'] == 'forward':
                self.__noteMap[note]['motor'].forward()
            else:
                self.__noteMap[note]['motor'].backward()  
            event.wait(.05)
            self.__noteMap[note]['motor'].stop()
            #self.__noteMap[note].forward()
            #sleep(.1)
            #self.__noteMap[note].stop()
        else:
            print "No bell for note " + str(note)

    def stop(self, note):
        pass
