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

import h5py as h5py

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from keras.layers import Activation

import sys, re
import random




DEBUGmode = True 


def init_gtrbass_streams():
    # initialize two parts and one stream
    
    
    stream1 = m21.stream.Stream()
    stream1.keySignature = m21.key.Key('C', 'major')
    stream1.timeSignature = m21.meter.TimeSignature('4/4')
     
    ## music21.tempo.MetronomeMark Quarter=165.0

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

 
    





    
ramones_midi_data = pd.read_pickle('ramones_GtrBass_all_data_transposed')
ram_scores = ramones_midi_data.as_matrix()

unique_Ramones_midi_data = ramones_midi_data.drop_duplicates()

frequencies = ramones_midi_data.groupby(['Gtr0','Gtr1','Gtr2','Gtr3','Gtr4','Gtr5','Gtr_Mute', 'Gtr_Hold', 'Bass1', 'Bass_Mute', 'Bass_Hold']).size()
#frequencies.sort(axis=1, ascending=False)
frequencies.sort_values(ascending=False, inplace=True)

ramones_midi_data_notesOnly = ramones_midi_data.loc[:,['Gtr0','Gtr1','Gtr2','Gtr3','Gtr4','Gtr5', 'Bass1']]
frequencies_notes = ramones_midi_data_notesOnly.groupby(['Gtr0','Gtr1','Gtr2','Gtr3','Gtr4','Gtr5', 'Bass1']).size()
frequencies_notes.sort_values(ascending=False, inplace=True)


ramones_midi_data_GtrOnly = ramones_midi_data.loc[:,['Gtr0','Gtr1','Gtr2','Gtr3','Gtr4','Gtr5']]
frequencies_notes_gtr = ramones_midi_data_GtrOnly.groupby(['Gtr0','Gtr1','Gtr2','Gtr3','Gtr4','Gtr5']).size()
frequencies_notes_gtr.sort_values(ascending=False, inplace=True)



ramones_midi_data['combined'] = list(zip(ramones_midi_data.Gtr0, ramones_midi_data.Gtr1,
         ramones_midi_data.Gtr2, ramones_midi_data.Gtr3,
         ramones_midi_data.Gtr4, ramones_midi_data.Gtr5, 
         ramones_midi_data.Gtr_Mute, ramones_midi_data.Gtr_Hold,
         ramones_midi_data.Bass1, ramones_midi_data.Bass_Mute, 
         ramones_midi_data.Bass_Hold))


rmd_frequencies = ramones_midi_data.groupby(['combined']).size()
rmd_frequencies.sort_values(inplace=True,  ascending=False)



# make DF and add index: 
rmd_frequencies_DF = pd.DataFrame(rmd_frequencies)
rmd_frequencies_DF['frq'] = range(0, len(rmd_frequencies_DF))

rmd_frequencies_DF['my_index'] = rmd_frequencies_DF.index

ramones_midi_data = ramones_midi_data.merge(rmd_frequencies_DF, how='left',  left_on='combined', right_on='my_index' )

del ramones_midi_data[ 'my_index']

ramones_midi_data.columns = ['Gtr0',      'Gtr1',      'Gtr2',      'Gtr3',      'Gtr4',
            'Gtr5',  'Gtr_Mute',  'Gtr_Hold',     'Bass1', 'Bass_Mute',
       'Bass_Hold',  'combined',     'count',   'freq']



indices_word = dict(zip(ramones_midi_data.freq.values, ramones_midi_data.combined))
word_indices = dict(zip(ramones_midi_data.combined, ramones_midi_data.freq.values))



#chars = set(str1)
words = set( ramones_midi_data.freq.unique())

#word_indices = dict((c, i) for i, c in enumerate(words))
#indices_word = dict((i, c) for i, c in enumerate(words))

#print("chars:",type(chars))
#print("words",type(words))
print("total number of unique words",len(words))
#print("total number of unique chars", len(chars))

maxlen = 32
step = 1
print("maxlen:",maxlen,"step:", step)

sentences = []
next_words = []
list_words = []

sentences2=[]
list_words = list(ramones_midi_data.freq)

#split the text into sentences of length maxlen --> sentences 
#split the list of words into list of "next_words" 
for i in range(0,len(list_words)-maxlen, step):
    sentences2 = list_words[i: i + maxlen]
    sentences.append(sentences2)
    next_words.append((list_words[i + maxlen]))
    
    
print('nb sequences(length of sentences):', len(sentences))
print("length of next_word",len(next_words))


print('Vectorization...')
X = np.zeros((len(sentences), maxlen, len(words)), dtype=np.bool)
y = np.zeros((len(sentences), len(words)), dtype=np.bool)

for ii in range(len(sentences)):
    for jj in range(maxlen):
        #print(i,t,word)
        X[ii, jj, sentences[ii][jj]] = 1
    y[ii, next_words[ii] ] = 1




model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape=(maxlen, len(words))))
model.add(Dropout(0.2))
model.add(LSTM(128, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(len(words)))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

#model.fit(X, y, batch_size=128, nb_epoch=N_epochs)



#build the model: 2 stacked LSTM
#print('Build model...')
#model = Sequential()
#model.add(LSTM(512, return_sequences=True, input_shape=(maxlen, len(words))))
#model.add(Dropout(0.2))
#model.add(LSTM(512, return_sequences=False))
#model.add(Dropout(0.2))
#model.add(Dense(len(words)))
#model.add(Activation('softmax'))

#model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

###
#X.shape
#Out[21]: (98455, 30, 21304)
###


# define the LSTM model: 
#  We can now define our LSTM model. Here we define a single hidden LSTM layer 
#  with 256 memory units. The network uses dropout with a probability of 20. 
#  The output layer is a Dense layer using the softmax activation function to 
#  output a probability prediction for each of the 47 characters 
#  between 0 and 1.
#

#model = Sequential()
#model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
#model.add(Dropout(0.2))
#model.add(Dense(y.shape[1], activation='softmax'))
#model.compile(loss='categorical_crossentropy', optimizer='adam')

# define the checkpoint
filepath="RAIMONES_weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]



#model.fit(X, y, epochs=20, batch_size=128, callbacks=callbacks_list)

model.fit(X, y, epochs=50, batch_size=128, callbacks=callbacks_list)







## JOIN 







# Pandas.Merge 





## try out MARKOV CHAINS!! 



filename = "RAIMONES_weights-improvement-49-0.8433.hdf5"
model.load_weights(filename)



def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)




#
instruments = 2
tracks_per_instruments = [6,1]

num_of_generated_outputs = 128


diversity_array = [0.2, 0.5, 1.0, 1.2, 1.5]

generated_output = np.zeros(( num_of_generated_outputs + maxlen,
                             sum(tracks_per_instruments) + 2 * len(tracks_per_instruments), 
                             len(diversity_array) ), dtype='int')

#add init-words to output matrix 

 

start_index = random.randint(0, len(list_words) - maxlen - 1)

for kk in range(len(diversity_array)):
    diversity = diversity_array[kk]
    print()
    print('----- diversity:', diversity)
    generated = []
    sentence = list_words[start_index: start_index + maxlen]
    generated.append(sentence)
    
    for ll in range(maxlen):
        generated_output[ ll,:, kk ] = indices_word[ sentence[ll] ]
    
    
    print('----- Generating with seed: "' , sentence , '"')
    print()
    print(generated)
    print()

    for ii in range(num_of_generated_outputs):
        x = np.zeros((1, maxlen, len(words)))
        for jj in range(maxlen):
            x[0, jj, sentence[jj]] = 1

        preds = model.predict(x, verbose=0)[0]
        
        next_index = sample(preds, diversity)
        next_word = indices_word[next_index]  ## is this correct?! 
        
        generated_output[  maxlen-1+ii, :, kk ] = next_word
        
        
        del sentence[0]
                
        sentence.append(next_word)
        
        print(next_word)
    print()
    
    


midifilenames = ['00RAIMONES_first_trials02.mid', 
                 '00RAIMONES_first_trials05.mid', 
                 '00RAIMONES_first_trials10.mid', 
                 '00RAIMONES_first_trials12.mid', 
                 '00RAIMONES_first_trials15.mid']


for ii in range(5):
    ram_scores = generated_output[:,:,ii]
    ramones_stream = read_bin_data_make_stream(ram_scores, tracks_per_instruments)

    midifilename = midifilenames[ii]
    mf = m21.midi.translate.streamToMidiFile(ramones_stream)
    mf.open(midifilename, 'wb')
    mf.write()
    mf.close()




