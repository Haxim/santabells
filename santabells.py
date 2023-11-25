#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    import midi
except ImportError:
    print("Get louisabraham/python3-midi from github.")
    print()
    raise

import argparse
from gpiozero import Motor
import time
from time import sleep
import threading
from threading import Thread

parser = argparse.ArgumentParser(description='Play santas.')
parser.add_argument('-t', '--transpose', type=int, default=36,
                    help='number of steps to transpose song')
parser.add_argument('filename', help='type 0 midi file to play')
args = parser.parse_args()

pattern = midi.read_midifile(args.filename)
resolution = pattern.resolution

usecsPerQNote = 500000 # default

def calculateSecsPerTick():
    secsPerTick = usecsPerQNote * 0.000001 / resolution
    return secsPerTick

secsPerTick = calculateSecsPerTick()

class Swing(object):
    __noteMap = {}
    __transpose = 0

    def __init__(self, transpose = 0, dupes = False):
        print ("Initializing swing object and setting up motors.")
        self.__transpose = transpose
        self.__dupes = dupes
        motor1 = Motor(4, 17)
        motor2 = Motor(18, 27)
        motor3 = Motor(22, 23)
        motor4 = Motor(24, 25)
        motor5 = Motor(5, 6)
        motor6 = Motor(12, 13)
        motor7 = Motor(19, 16)
        motor8 = Motor(26, 20)
        self.__noteMap[110] = {"motor": motor1, "direction": "forward"}
        self.__noteMap[93] =  {"motor": motor1, "direction": "backward"}
        self.__noteMap[98] =  {"motor": motor2, "direction": "forward"}
        self.__noteMap[100] = {"motor": motor2, "direction": "backward"}
        self.__noteMap[104] = {"motor": motor3, "direction": "forward"}
        self.__noteMap[102] = {"motor": motor3, "direction": "backward"}
        self.__noteMap[114] = {"motor": motor4, "direction": "forward"}
        self.__noteMap[103] = {"motor": motor4, "direction": "backward"}
        self.__noteMap[115] = {"motor": motor5, "direction": "forward"}
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

        print(self.__noteMap)
        #self.wake()
        #time.sleep(2)

    def wake(self):
        for note, url in sorted(self.__noteMap.items()):
            self.play(note, transpose=False)

    def play(self, note, transpose=True):
        if transpose:
            note += self.__transpose
            #print(str(self.__transpose))

        if (note > 127 or note < 0):
            print("Note number out of range! " + str(note))
            return

        if note in self.__noteMap:
            event = threading.Event()
            #print ("would play a note here " + str(self.__noteMap[note]))
            #print (str(self.__noteMap[note]['motor']))
            if self.__noteMap[note]['direction'] == 'forward':
                self.__noteMap[note]['motor'].forward()
            else:
                self.__noteMap[note]['motor'].backward()  
            event.wait(.07)
            self.__noteMap[note]['motor'].stop()
        else:
            print ("No bell for note " + str(note))

    def stop(self, note):
        pass

inst = Swing(args.transpose)

eTime = time.time()
for track in pattern:
    for event in track:
        eTime += (event.tick * secsPerTick)
        if type(event) is midi.SetTempoEvent:
            usecsPerQNote = event.mpqn
            secsPerTick = calculateSecsPerTick()

        if type(event) is midi.NoteOnEvent and event.data[1] != 0:
            while time.time() < eTime:
                calcSleep = eTime - time.time()
                if calcSleep > 0:
                    pass
                    #time.sleep(calcSleep)
            inst.play(event.data[0])
        if type(event) is midi.NoteOffEvent or (type(event) is midi.NoteOnEvent and event.data[1] == 0):
            while time.time() < eTime:
                calcSleep = eTime - time.time()
                if calcSleep > 0:
                    pass
                    #time.sleep(calcSleep)
            inst.stop(event.data[0])
