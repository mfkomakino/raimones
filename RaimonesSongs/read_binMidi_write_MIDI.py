#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 12:17:46 2017

@author: mfrey
"""

import numpy as np
import music21 as m21
import os

import pandas as pd

DEBUGmode = True 


def init_gtrbass_streams():
    # initialize two parts and one stream
    
    
    stream1 = m21.stream.Stream()
    stream1.keySignature = m21.key.Key('C', 'major')
    stream1.timeSignature = m21.meter.TimeSignature('4/4')
    stream1.insert(m21.tempo.MetronomeMark(number=165))

#guitar
    gtr_part    = m21.stream.Part()
    gtr_part.id = 'Guitar Stream'
    gtr_part.insert(m21.instrument.ElectricGuitar())
    gtr_part.clef = m21.clef.TrebleClef()  
    
#Bass     
    bass_part    = m21.stream.Part()
    bass_part.id = 'Bass Guitar Stream'
    bass_part.insert(m21.instrument.ElectricBass())
    bass_part.clef = m21.clef.BassClef()  
    
    return (stream1, gtr_part, bass_part)





def read_bin_data_make_stream(bin_midi_data, tracks_per_instrument):
#    bin_midi_data, numpy array 
#    tracks_per_instruments,  array

    #initialize the stream and two parts: 
    (stream1, gtr_part, bass_part) = init_gtrbass_streams()
    
    
    gtr_tracks  = list(range(0,tracks_per_instrument[0]))
    gtr_mute = tracks_per_instrument[0]
    gtr_hold = tracks_per_instrument[0]+1
    
    bass_tracks = list(range(2+tracks_per_instrument[0],2+tracks_per_instrument[0]+tracks_per_instrument[1] ))
    bass_mute   = tracks_per_instrument[0] + tracks_per_instrument[1] + 2
    bass_hold   = tracks_per_instrument[0] + tracks_per_instrument[1] + 3


    previous_hold_gtr  = False 
    previous_hold_bass = False 
    
    for ii in range(len(bin_midi_data)-1):

        #################
        ### Guitar track:
        #################
        if (not previous_hold_gtr): # previous line was not a hold, 
        # so the chord or note has to be set: 
            gtr_chordnote_full = bin_midi_data[ii, gtr_tracks]
            gtr_chordnote = gtr_chordnote_full[0:tracks_per_instrument[0]-sum(gtr_chordnote_full == 0)]

            gtr_pitch1 = m21.pitch.Pitch()
            
            if (bin_midi_data[ii, gtr_mute] == 0):  # not muted --> not rest
                
                if (len(gtr_chordnote) == 1):  # it's a note (not a chord)
                    gtr_pitch1.ps =  gtr_chordnote[0]
                    gtr_notechord = m21.note.Note( gtr_pitch1.nameWithOctave )
                    gtr_notechord.duration.quarterLength = 0.25
                
                elif (len(gtr_chordnote) > 1): # it's a chord (not a note)
                    gtr_notechord_list = []
                    for jj in range(len(gtr_chordnote)):
                        gtr_pitch1.ps =  gtr_chordnote[jj]
                        gtr_notechord_list.append(gtr_pitch1.nameWithOctave)
                    
                    gtr_notechord = m21.chord.Chord(gtr_notechord_list)
                    gtr_notechord.duration.quarterLength = 0.25
                    
                else: #it's a rest   (mute bit is not used)
                    gtr_notechord = m21.note.Rest()
                    gtr_notechord.duration.quarterLength = 0.25
                    
            else: # muted  --> rest (this could be removed as we're also 
                                     # checking for number of 0's for notes)
                gtr_notechord = m21.note.Rest()
                gtr_notechord.duration.quarterLength = 0.25  
    
        else: ## previous_hold_gtr == True
            gtr_notechord.duration.quarterLength = gtr_notechord.duration.quarterLength + 0.25  
            
        if (bin_midi_data[ii, gtr_hold] == 0):  # not hold --> write note/chord
            gtr_part.append(gtr_notechord)
            previous_hold_gtr = False
        else:
            previous_hold_gtr = True
        
        
        
        ###############
        ### BASS GUITAR 
        ###############
        if (not previous_hold_bass): # previous line was not a hold, 
        # so the chord or note has to be set: 
            bass_chordnote_full = bin_midi_data[ii, bass_tracks]
            bass_chordnote = bass_chordnote_full[0:tracks_per_instrument[1]-sum(bass_chordnote_full == 0)]
            bass_pitch1 = m21.pitch.Pitch()
            
            #Guitar track:
            if (bin_midi_data[ii, bass_mute] == 0):  # not muted --> not rest
                
                if (len(bass_chordnote) == 1):  # it's a note (not a chord)
                    bass_pitch1.ps =  bass_chordnote[0]
                    bass_notechord = m21.note.Note( bass_pitch1.nameWithOctave )
                    bass_notechord.duration.quarterLength = 0.25
                
                elif (len(bass_chordnote) > 1): # it's a chord (not a note)
                    bass_notechord_list = []
                    for jj in range(len(bass_chordnote)):
                        bass_pitch1.ps =  bass_chordnote[jj]
                        bass_notechord_list.append(bass_pitch1.nameWithOctave)
                    
                    bass_notechord = m21.chord.Chord(bass_notechord_list)
                    bass_notechord.duration.quarterLength = 0.25
                    
                else: #it's a rest   (mute bit is not used)
                    bass_notechord = m21.note.Rest()
                    bass_notechord.duration.quarterLength = 0.25
                    
            else: # muted  --> rest (this could be removed as we're also 
                                     # checking for number of 0's for notes)
                bass_notechord = m21.note.Rest()
                bass_notechord.duration.quarterLength = 0.25  
            
    
        else: ## previous_hold_bass == True
            bass_notechord.duration.quarterLength = bass_notechord.duration.quarterLength + 0.25  
           
        ## hold_bass --> write chord/note or not     
        if (bin_midi_data[ii, bass_hold] == 0):  # not hold --> write note/chord
            bass_part.append(bass_notechord)
            previous_hold_bass = False
        else:
            previous_hold_bass = True

    stream1.insert(0, gtr_part)
    stream1.insert(0, bass_part)

    return stream1

    



def test_write_midi():
    stream1 = m21.stream.Stream()
#    stream1.number = 10
    stream1.keySignature = m21.key.Key('C', 'major')
    stream1.timeSignature = m21.meter.TimeSignature('4/4')

#guitar
    gtr_part    = m21.stream.Part()
    gtr_part.id = 'Guitar Stream'
    gtr_part.insert(m21.instrument.ElectricGuitar())
    gtr_part.clef = m21.clef.TrebleClef()  
    
#Bass     
    bass_part    = m21.stream.Part()
    bass_part.id = 'Bass Guitar Stream'
    bass_part.insert(m21.instrument.ElectricBass())
    bass_part.clef = m21.clef.BassClef()  
    
   
    note_temp = m21.note.Note('B4')
    note_temp.duration.quarterLength = 0.5
    gtr_part.append(note_temp)
    
    note_temp = m21.note.Note('A4')
    note_temp.duration.quarterLength = 1.5
    gtr_part.append(note_temp)
    


    note_temp = m21.chord.Chord(['A4', 'A3', 'B4'])
    note_temp.duration.quarterLength = 2.5
    bass_part.append(note_temp)
    
    note_temp = m21.note.Note('C5')
    note_temp.duration.quarterLength = 2.5
    bass_part.append(note_temp)

    stream1.insert(0, gtr_part)
    stream1.insert(0, bass_part)
    
#    stream1.write('test.mid')
    mf = m21.midi.translate.streamToMidiFile(stream1)
    mf.open('testmidi.mid', 'wb')
    mf.write()
    mf.close()

    return True







ramones_midi_data = pd.read_pickle('ramones_GtrBass_all_data')
ram_scores = ramones_midi_data.as_matrix()

instruments = 2
tracks_per_instruments = [6,1]
midifilename = 'ramones_all.mid'


ramones_stream = read_bin_data_make_stream(ram_scores, tracks_per_instruments)


mf = m21.midi.translate.streamToMidiFile(ramones_stream)
mf.open(midifilename, 'wb')
mf.write()
mf.close()




## most frequent guitar chords: 

gtrbass = [[45, 52, 57, 0, 0, 0, 0, 0,0,0,0], [50, 57, 62, 0, 0, 0, 0, 0,0,0,0],[43, 50, 55, 0, 0, 0, 0, 0,0,0,0],[48, 55, 60, 0, 0, 0, 0, 0,0,0,0],[52, 59, 64, 0, 0, 0, 0, 0,0,0,0],[47, 54, 59, 0, 0, 0, 0, 0,0,0,0],[46, 53, 58, 0, 0, 0, 0, 0,0,0,0],[45, 52, 0, 0, 0, 0, 0, 0,0,0,0],[50, 57, 62, 66, 0, 0, 0, 0,0,0,0],[41, 48, 53, 0, 0, 0, 0, 0,0,0,0],[43, 50, 0, 0, 0, 0,0,0,0,0,0]]
gtrbass_np = np.asarray(gtrbass)
gtrstream = read_bin_data_make_stream(gtrbass_np, [6,1])

instruments = 2
tracks_per_instruments = [6,1]
midifilename = 'most_freq_gtr.mid'

mf = m21.midi.translate.streamToMidiFile(gtrstream)
mf.open(midifilename, 'wb')
mf.write()
mf.close()

