#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 10:17:57 2017

Analyze the Ramones MIDI files

@author: mfrey
"""

import numpy as np
import music21 as m21
import os

import pandas as pd

DEBUGmode = False 


def __init_stream(parsed_stream, number_of_voices):
    ## init a matrix of appropriate length & width
    ## 
    
    l_of_a = []
    for ii in range(len(parsed_stream)):
        l_of_a.append(parsed_stream[ii].duration.quarterLength)
        
    length_of_array = int(4 * max(l_of_a)) + 16   
        
    stream_matrix = np.zeros((length_of_array, number_of_voices + 2 ), dtype=np.int)
    
#    time_vect = np.zeros((length_of_array, 1 ), dtype=np.float)   
#    for ii in range(len(time_vect)):
#        time_vect[ii][0] = ii * 0.25
#    
#    return (stream_matrix, time_vect)
    return stream_matrix



# guitar = 01, bass = 10
#
# timestamp, 01, [note1, note2, note3], duration
#  
#
#
#
#
#

def get_track_from_file_num(parsed_stream, track_nr, number_of_voices, ticks_per_16th): 
##output format: array with "nbr_of_voices" + 2 columns 
## extra columns: mute & hold 
    stream_matrix = __init_stream(parsed_stream, number_of_voices)
    
    # GET RID OF VOICES 
    # If the stream has several voices (not chords), only select the one with the most notes:
    lps = len(parsed_stream[track_nr].voices)
    if (len(parsed_stream[track_nr].voices) > 0):
        psvoices = []
        for xx in range(lps):
            psvoices.append(len(parsed_stream[track_nr].voices[xx]))
        
        argmax_voices = np.argmax(psvoices)
        iterable_stream = parsed_stream[track_nr].voices[argmax_voices]
        if DEBUGmode: 
            print('has voices')
        
    else:
        iterable_stream = parsed_stream[track_nr]
        if DEBUGmode: 
            print('no voices')
        

    counter = 0         
#    for step in parsed_stream[track_nr].flat.notes: 
    for step in iterable_stream.notes: 
        
        ## detect breaks/ rests and fill up the matrix: 
        break_duration = int(step.midiTickStart / ticks_per_16th) - counter
        if break_duration > 0: 
            if DEBUGmode: 
                print("Break:  ",    ' -- ', break_duration, " -- ", counter)
            stream_matrix[counter:counter + break_duration-1,number_of_voices+1]  = 1  
            stream_matrix[counter:counter + break_duration, number_of_voices]  = 1  
            counter+=break_duration


        if step.isChord:
        #It's a chord! 
            chord_note_list_num = []
            chord_note_list = []
        
            for jj in range(len(step.pitches)):
                chord_note_list_num.append( int(step.pitches[jj].midi) )
                chord_note_list.append( step.pitches[jj].name + str(step.pitches[jj].octave) )
                
            chord_note_list_num = sorted(chord_note_list_num)
            chord_note_list_num = chord_note_list_num[0 : min(len(chord_note_list_num), number_of_voices)]

            chord_note_list     = sorted(chord_note_list)
            chord_note_list     = chord_note_list[0 : min(len(chord_note_list), number_of_voices)]

            chord_duration      = int(np.round(4.0 * step.duration.quarterLength, 0))
            if DEBUGmode:
                print("Chord:  ", int(step.midiTickStart / ticks_per_16th), '  ', chord_note_list_num,'  ', chord_note_list,' -- ', chord_duration, " -- ", counter)
            
            # fill the matrix with the chords:
            for kk in range(chord_duration):
                stream_matrix[counter + kk,0:len(chord_note_list_num)] = chord_note_list_num
                
            # fill the vector of "hold chord" bits:
            stream_matrix[counter:counter+chord_duration-1, number_of_voices+1]  = 1  
            
            counter+=chord_duration        
            
        else:   
        # It's a single note       

            note_duration = int(np.round(4.0 * step.duration.quarterLength, 0))
            if DEBUGmode: 
                print('Note:   ',  int(step.midiTickStart / ticks_per_16th), "  ", int(step.pitch.midi), "   ", step.pitch.name, step.pitch.octave, " -- ", note_duration, " -- ", counter)

            for kk in range(note_duration):
                stream_matrix[counter + kk,0] = int(step.pitch.midi)

            # fill the vector of "hold chord" bits:
            stream_matrix[counter:counter+note_duration-1, number_of_voices+1]  = 1  
            
            counter+=note_duration

    return stream_matrix
        




def get_track_from_file_to_text(parsed_stream, track_nr, number_of_voices, ticks_per_16th): 
##output format: array with "nbr_of_voices" + 2 columns 
## extra columns: mute & hold 
    stream_matrix = __init_stream(parsed_stream, number_of_voices)
    
     
            
    for step in parsed_stream[track_nr].flat.notesAndRests[0:20]: 
        #It's a chord!
        if step.isChord:
            chord_note_list_num = np.zeros(number_of_voices)
            chord_note_list = []
        
            for jj in range(len(step.pitches)):
                chord_note_list_num[jj] =  int(step.pitches[jj].midi)
                chord_note_list.append( step.pitches[jj].name + str(step.pitches[jj].octave))
                
            chord_note_list = sorted(chord_note_list)
            if DEBUGmode: 
                print("Chord:  ", int(step.midiTickStart / ticks_per_16th), '  ', chord_note_list_num,'  ', chord_note_list,' -- ', int(np.round(4.0 * step.duration.quarterLength, 0)))
            
        # It's a break! 
        elif step.isRest: 
            print("Break:  ",    ' -- ', step.duration.quarterLength * 4, " ",int(np.round(4.0 * step.duration.quarterLength, 0)))
        else:   
            print('Note:   ',  step.midiTickStart, " -- ", step.pitch.name, step.pitch.octave, " ",int(np.round(4.0 * step.duration.quarterLength, 0)), " ",  step.pitch.midi)
            
#    return (stream_matrix, time_vect)
    return stream_matrix
        



def get_Quarter_BPM(parsed_stream):
    # returns the list of quarter-BPMs from a stream

    quarter_bpm = []
    for bpm in ram_stream.flat:
        if "Metronome" in str(bpm): 
            quarter_bpm.append(bpm.getQuarterBPM())
    return quarter_bpm



### MAIN FILE 


#dirname = '/Users/mfrey/Documents/DSR/Raimones-Documents/MIDI/'
#dirname = '/Users/mfrey/Documents/DSR/Raimones-Documents/MIDI-saved/updated/transposed/'
dirname='/home/ubuntu/midi_music/'

# get all file names 

#filenames = os.listdir(path)

ramones_Guitar =   []   
ramones_Bass =   []   
stream_durations = []
stream_lengths = []

ramones_GtrBass_all = []

midi_files = [f for f in os.listdir(dirname) if f.endswith('.mid')]
#print(midi_files)
for midi_file in midi_files:
    print(midi_file)

    mf = m21.midi.MidiFile()
    mf.open(dirname + midi_file)
    mf.read()
    mf.close()

    ram_stream = m21.midi.translate.midiFileToStream(mf)
    ticks_per_16th =  mf.ticksPerQuarterNote // 4

    ramones_Guitar = get_track_from_file_num(ram_stream, 0, 6, ticks_per_16th)
    ramones_Bass   = get_track_from_file_num(ram_stream, 1, 1, ticks_per_16th)
    
    ramones_GtrBass = np.append(ramones_Guitar, ramones_Bass, axis=1)
    
    if len(ramones_GtrBass_all )>0:
        ramones_GtrBass_all = np.append(ramones_GtrBass_all, ramones_GtrBass, axis=0)
    else:
        ramones_GtrBass_all = ramones_GtrBass
            


    for jj in range(len(ram_stream)):
        stream_durations.append( ram_stream[jj].duration.quarterLength )
        stream_lengths.append( len(ramones_Bass) )
            
 

ramones_GtrBass_all_DF = pd.DataFrame( ramones_GtrBass_all, columns= [ 'Gtr0','Gtr1','Gtr2','Gtr3','Gtr4','Gtr5','Gtr_Mute', 'Gtr_Hold', 'Bass1', 'Bass_Mute', 'Bass_Hold'  ] )
ramones_GtrBass_all_DF.to_pickle('ramones_GtrBass_all_data_transposed')




## READ THE DATA AGAIN 
#ramones_midi_data_DF = pd.read_pickle('ramones_GtrBass_all_data')


