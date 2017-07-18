# -*- coding: utf-8 -*-

# Import MIDI files and analyze 


from __future__ import print_function

import music21 as m21
from collections import defaultdict, OrderedDict
import numpy as np
#from itertools import groupby, izip_longest
#from grammar import *

dirname = '/Users/mfrey/Documents/DSR/Raimones-Documents/MIDI/freemidi.org/'
#filename = 'SurfinBird.mid'

#filename = 'BeatontheBrat.mid'
#filename = 'WereAHappyFamily.mid'
filename = 'TakeitasitComes.mid'


fullfilename = dirname+filename


#----------------------------from https://github.com/jisungk/deepjazz.git ---
#----------------------------'deepjazz/preprocess.py' ----------------------------------#


''' Helper function to get the grammatical data from given musical data. '''
def __get_abstract_grammars(measures, chords):
    # extract grammars
    abstract_grammars = []
    for ix in xrange(1, len(measures)):
        m = m21.stream.Voice()
        for i in measures[ix]:
            m.insert(i.offset, i)
        c = m21.stream.Voice()
        for j in chords[ix]:
            c.insert(j.offset, j)
        parsed = parse_melody(m, c)
        abstract_grammars.append(parsed)

    return abstract_grammars



''' Get corpus data from grammatical data '''
def get_corpus_data(abstract_grammars):
    corpus = [x for sublist in abstract_grammars for x in sublist.split(' ')]
    values = set(corpus)
    val_indices = dict((v, i) for i, v in enumerate(values))
    indices_val = dict((i, v) for i, v in enumerate(values))

    return corpus, values, val_indices, indices_val


#def get_musical_data(data_fn):
#    measures, chords = __parse_midi(data_fn)
#    abstract_grammars = __get_abstract_grammars(measures, chords)
#
#    return chords, abstract_grammars

def __parse_midi(data_fn):
    # Parse the MIDI data for separate melody and accompaniment parts.
    midi_data = m21.converter.parse(data_fn)
    # Get melody part, compress into single voice.
    melody_stream = midi_data[5]     # For Metheny piece, Melody is Part #5.
    melody1, melody2 = m21.melody_stream.getElementsByClass(stream.Voice)
    for j in melody2:
        melody1.insert(j.offset, j)
    melody_voice = melody1

    for i in melody_voice:
        if i.quarterLength == 0.0:
            i.quarterLength = 0.25

    # Change key signature to adhere to comp_stream (1 sharp, mode = major).
    # Also add Electric Guitar. 
    melody_voice.insert(0, instrument.ElectricGuitar())
    melody_voice.insert(0, key.KeySignature(sharps=1, mode='major'))

    # The accompaniment parts. Take only the best subset of parts from
    # the original data. Maybe add more parts, hand-add valid instruments.
    # Should add least add a string part (for sparse solos).
    # Verified are good parts: 0, 1, 6, 7 '''
    partIndices = [0, 1, 6, 7]
    comp_stream = m21.stream.Voice()
    comp_stream.append([j.flat for i, j in enumerate(midi_data) 
        if i in partIndices])

    # Full stream containing both the melody and the accompaniment. 
    # All parts are flattened. 
    full_stream = m21.stream.Voice()
    for i in xrange(len(comp_stream)):
        full_stream.append(comp_stream[i])
    full_stream.append(melody_voice)

    # Extract solo stream, assuming you know the positions ..ByOffset(i, j).
    # Note that for different instruments (with stream.flat), you NEED to use
    # stream.Part(), not stream.Voice().
    # Accompanied solo is in range [478, 548)
    solo_stream = m21.stream.Voice()
    for part in full_stream:
        curr_part = m21.stream.Part()
        curr_part.append(part.getElementsByClass(instrument.Instrument))
        curr_part.append(part.getElementsByClass(tempo.MetronomeMark))
        curr_part.append(part.getElementsByClass(key.KeySignature))
        curr_part.append(part.getElementsByClass(meter.TimeSignature))
        curr_part.append(part.getElementsByOffset(476, 548, 
                                                  includeEndBoundary=True))
        cp = curr_part.flat
        solo_stream.insert(cp)

    # Group by measure so you can classify. 
    # Note that measure 0 is for the time signature, metronome, etc. which have
    # an offset of 0.0.
    melody_stream = solo_stream[-1]
    measures = OrderedDict()
    offsetTuples = [(int(n.offset / 4), n) for n in melody_stream]
    measureNum = 0 # for now, don't use real m. nums (119, 120)
    for key_x, group in groupby(offsetTuples, lambda x: x[0]):
        measures[measureNum] = [n[1] for n in group]
        measureNum += 1

    # Get the stream of chords.
    # offsetTuples_chords: group chords by measure number.
    chordStream = solo_stream[0]
    chordStream.removeByClass(note.Rest)
    chordStream.removeByClass(note.Note)
    offsetTuples_chords = [(int(n.offset / 4), n) for n in chordStream]

    # Generate the chord structure. Use just track 1 (piano) since it is
    # the only instrument that has chords. 
    # Group into 4s, just like before. 
    chords = OrderedDict()
    measureNum = 0
    for key_x, group in groupby(offsetTuples_chords, lambda x: x[0]):
        chords[measureNum] = [n[1] for n in group]
        measureNum += 1

    # Fix for the below problem.
    #   1) Find out why len(measures) != len(chords).
    #   ANSWER: resolves at end but melody ends 1/16 before last measure so doesn't
    #           actually show up, while the accompaniment's beat 1 right after does.
    #           Actually on second thought: melody/comp start on Ab, and resolve to
    #           the same key (Ab) so could actually just cut out last measure to loop.
    #           Decided: just cut out the last measure. 
    del chords[len(chords) - 1]
    assert len(chords) == len(measures)

    return measures, chords


def __init_stream(parsed_stream, track_nr, nbr_of_voices):
    ## init a matrix of appropriate length & width
    ## 
    length_of_array = 4 * parsed_stream.duration.quarterLength   # 16-th are being encoded
    stream_matrix = np.zeros([length_of_array, nbr_of_voices+2], dtype=np.int)
    
    return stream_matrix



def __get_timing():
    ## read file and get the timing from the music file 
    ##
    return None



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




def get_track_from_file(parsed_stream, track_nr, nbr_of_voices): 
##output format: array with "nbr_of_voices" + 2 columns 
## extra columns: mute & hold 
    stream_matrix = __init_stream(parsed_stream, track_nr, nbr_of_voices)
    
    #fill up with mute until the track starts 
    
    for ii in parsed_stream[0].notes : 
        #kk+=1
        chord_note_list = []
        for jj in range(len(ii.pitches)):
            chord_note_list.append( ii.pitches[jj].midi )        
        #    print(kk,': ', ii.midiTickStart, ' - ',jj , ii.pitches[jj].midi, ' ', ii.duration.quarterLength * 2)
    
        chord_note_list = sorted(chord_note_list)
        print(chord_note_list)
        
    return stream_matrix
    
    

get_track_from_file(ram_stream, 1, 3)


ramones_midi = m21.converter.parse(fullfilename)

notes = ramones_midi.stream()[1].elements[0:20]

ramones_midi.stream()[0].show('text')

ramones_midi.stream()[1].elements[5][1].pitch.midi
ramones_midi.stream()[1].elements[5][2].duration



mf = m21.midi.MidiFile()
mf.open(fullfilename)
mf.read()
mf.close()

ticks_per_16th =  mf.ticksPerQuarterNote // 4

ram_stream = m21.midi.translate.midiFileToStream(mf)

ram_stream.highestTime

st_by_instruments = m21.instrument.partitionByInstrument(ram_stream)
 
ii = 0
for part in st_by_instruments.parts:
    print(ii, ':', part.partName)
    ii+=1
    
    
 
ram_stream[0][0].instrumentName
 
ram_stream.analyze('key')

ram_stream.highestOffset

length_of_array = 4 * ram_stream.duration.quarterLength  



tempnote = ram_stream[0].notes[0]
tempnote.pitches[2].ps

kk = -1
git_trk1 = []

for ii in ram_stream[0].notesAndRests[0:10]: 
    kk+=1
    chord_note_list = []
    
    for jj in range(len(ii.pitches)):
        chord_note_list.append(ii.pitches[jj].midi)        
        #print(kk,': ', ii.midiTickStart, ' - ',jj , ii.pitches[jj].midi, ' ', ii.duration.quarterLength * 2, '++  ', ii.splitAtQuarterLength(0.5) )
    chord_note_list = sorted(chord_note_list)
    print(ii.midiTickStart, '  ', chord_note_list, ' -- ', ii.duration.quarterLength * 4)


ram_stream[0].splitAtQuarterLength(0.5)

ram_stream[0].getElementsByClass(m21.meter.TimeSignature)
ram_stream[0].getElementsByClass(m21.key.KeySignature)


for ii in range(50):
   print( m21.duration.quarterLengthToClosestType(ram_stream[0].notesAndRests[ii].duration.quarterLength))

# m21.instrument.unbundleInstruments(ram_stream).show()

#ramones_midi.show()

#sBach = corpus.parse(fullfilename)

#sBach.show()
