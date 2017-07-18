#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 20:37:44 2017

@author: mfrey
"""

from music21 import *
import numpy as np
import music21 as m21



dirname = '/Users/mfrey/Documents/DSR/Raimones-Documents/MIDI/freemidi.org/'
#filename = 'SurfinBird.mid'

filename = 'BeatontheBrat.mid'
#filename = 'WereAHappyFamily.mid'
#filename = 'TakeitasitComes.mid'


fullfilename = dirname+filename
    
    
mf = m21.midi.MidiFile()
mf.open(fullfilename)
mf.read()
mf.close()

ram_stream = m21.midi.translate.midiFileToStream(mf)

ticks_per_16th =  mf.ticksPerQuarterNote // 4

for n in ram_stream.flat.notes:
    if n.isChord: 
        ii=1 #  print("Note: %s%d %0.1f" % (n.name, 4*n.duration.quarterLength))
    else: 
        print("Note: %s%d %0.1f" % (n.pitch.name, n.pitch.octave, 4*n.duration.quarterLength))
        


for n in ram_stream[2].notesAndRests: 
    if n.isChord:
        chordlist = []
        chordlist_num = []
        for jj in range(len(n.pitches)):
            chordlist.append(n.pitches[jj].name + str(n.pitches[jj].octave))    
            chordlist_num.append(n.pitches[jj].midi )
        chordlist_num = sorted(chordlist_num)    
        print(int(1+np.trunc(n.midiTickStart / ticks_per_16th /16.0)), '-', n.midiTickStart / ticks_per_16th, " - ","Chord: ", chordlist, " ",  n.beat," ** ", int(np.round(4.0 * n.duration.quarterLength, 0)), 
              " ",  chordlist_num) 
    elif n.isRest: 
        print("               ", "Rest: ", n.duration.quarterLength, " - ", int(np.round(4.0 * n.duration.quarterLength, 0) ))
    else: 
        print(int(1+np.trunc(n.midiTickStart / ticks_per_16th /16.0)), '-',  n.midiTickStart / ticks_per_16th, " - ","Note: ", n.pitch.name, n.pitch.octave, " ",int(np.round(4.0 * n.duration.quarterLength, 0)), 
              " ",  n.pitch.midi)



ram_stream[1].flat.sorted.notesAndRests.show('text')



print('Instruments:')
ii=0
for i in ram_stream.flat.recurse().getInstruments():
    print(ii, ': ', i)
    print(type(i))
    ii+=1
    
