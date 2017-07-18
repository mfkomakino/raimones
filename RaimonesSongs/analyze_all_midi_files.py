f#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 10:17:57 2017

Analyze the Ramones MIDI files

@author: mfrey
"""

from music21 import *
import numpy as np
import music21 as m21
import os

import pandas as pd



def get_key_analyzed(parsed_stream):
    ## read file and get the key from the music file 
    ##
    return parsed_stream.analyze('key')


def get_key(parsed_stream):
    ## read file and get the key from the music file 
    ##
    if len(parsed_stream[0].getKeySignatures()) > 0:
        return parsed_stream[0].getKeySignatures()[0]
    else:
        return None    



def get_list_of_instruments(parsed_stream):
    #    returns the list of instruments in the given stream
    
    instr_list = []

    for ii in range(len(parsed_stream)):
        if "Instrument" in str(ram_stream[ii][0].show):
            instr_list.append(parsed_stream[ii][0].bestName())

    return instr_list   
  

def get_list_of_instruments_numeric(parsed_stream):
    # returns the list of instruments in the given stream 
    # in numerica midi form
    
    instr_list = []

    for ii in range(len(parsed_stream)):
        if "Instrument" in str(ram_stream[ii][0].show):
            instr_list.append(parsed_stream[ii][0].midiProgram) #instrumentID

    return instr_list   
 

def get_Quarter_BPM(parsed_stream):
    # returns the list of quarter-BPMs from a stream

    quarter_bpm = []
    for bpm in ram_stream.flat:
        if "Metronome" in str(bpm): 
            quarter_bpm.append(bpm.getQuarterBPM())
    return quarter_bpm




#dirname = '/Users/mfrey/Documents/DSR/Raimones-Documents/MIDI/'
dirname = './/Raimones-Documents/MIDI-saved/'


#fullfilename = dirname+filename





#mf = m21.midi.MidiFile()
#mf.open(fullfilename)
#mf.read()
#mf.close()

#ram_stream = m21.midi.translate.midiFileToStream(mf)

#ticks_per_16th =  mf.ticksPerQuarterNote // 4


# get all file names 

#filenames = os.listdir(path)

dirnames = []
for (_, dn ,_) in os.walk(dirname):
    dirnames.extend(dn)
    break

#midi_files = [[]]
#for ii in range(len(dirnames)):
#    midi_files.append ( [f for f in os.listdir(dirname+dirnames[ii]) if f.endswith('.mid')])




ramones_midi_data =   []   # pd.DataFrame( columns=['fullpath', 'key_analyzed', 'key_read', 'list_of_instruments', 'list_of_instruments_num', 'Quarter_BPM', 'ticks_per_16th'])

for midi_dir in range(len(dirnames)):
    midi_files = [f for f in os.listdir(dirname+dirnames[midi_dir]) if f.endswith('.mid')]
    #print(midi_files)
    for midi_file in range(len(midi_files)):
        midi_fullfilename = dirname + dirnames[midi_dir]+ "/" + midi_files[midi_file]
        print(midi_fullfilename)

        mf = m21.midi.MidiFile()
        mf.open(midi_fullfilename)
        mf.read()
        mf.close()
        
        ram_stream = m21.midi.translate.midiFileToStream(mf)
        
        midi_fullfilename
        ticks_per_16th =  mf.ticksPerQuarterNote // 4
        key_analyzed = get_key_analyzed(ram_stream)
        key = get_key(ram_stream)
        
        quarterBPM = get_Quarter_BPM(ram_stream)
        list_of_instruments = get_list_of_instruments(ram_stream)
        list_of_instruments_num = get_list_of_instruments_numeric(ram_stream)
        ticks_per_16th =  mf.ticksPerQuarterNote // 4

        stream_durations = []
        stream_lengths = []
        for jj in range(len(ram_stream)):
            stream_durations.append( ram_stream[jj].duration.quarterLength )
            stream_lengths.append( len(ram_stream[jj].flat)  )
            
            
        ramones_midi_data.append( [ midi_fullfilename, key_analyzed, key, list_of_instruments, list_of_instruments_num, quarterBPM, ticks_per_16th, stream_lengths, stream_durations ])
           




ramones_midi_data_DF = pd.DataFrame( ramones_midi_data, columns= [ 'midi_fullfilename', 'key_analyzed', 'key', 'list_of_instruments', 'list_of_instruments_num', 'quarterBPM', 'ticks_per_16th', 'stream_lengths', 'stream_durations'  ] )

ramones_midi_data_DF.to_pickle('ramones_midi_data_updated2')



ramones_midi_data_DF = pd.read_pickle('ramones_midi_data')


