#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 12:30:05 2017

@author: mfrey
"""

from keras.models import Sequential
#from keras.layers import Dense, Activation
#from keras.layers import LSTM
#from keras.optimizers import RMSprop
#from keras.callbacks import ModelCheckpoint
#from keras.utils.data_utils import get_file
import numpy as np
import random
import sys

#import ast 

from keras.models import load_model
#import json

model_type = 'best'
chooser = 4



def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)



def init_models_and_variables(model_chooser, model_type='best'):
    
    maxlen_list = [ 40, 40, 10 ]
    step_list =   [  3,  3,  1 ]
    
    modelname_best = ['lyrics_hdf5/aws_128-128_02_length40_step3_batch128_weights-improvement-00-0.7131.hdf5',
                      'lyrics_hdf5/aws_128_00_length40_step3_batch128_weights-improvement-00-0.9602.hdf5', 
                      'lyrics_hdf5/aws_128_00_length10_step1_batch128_weights-improvement-00-0.7494.hdf5'
                     ]
    
    modelname_worse = ['lyrics_hdf5/aws_128-128_02_length40_step3_batch128_weights-improvement-00-1.0104.hdf5',
                       'lyrics_hdf5/aws_128_00_length40_step3_batch128_weights-improvement-00-1.1308.hdf5', 
                       'lyrics_hdf5/aws_128_00_length10_step1_batch128_weights-improvement-00-1.0064.hdf5'
                      ]
    
 
    X_list = [ 'X403.npy', 'X403.npy', 'X101.npy' ]
    
    X = np.load(X_list[model_chooser])
    
    
    if model_type == 'best':
        modelnamelist = modelname_best
    else: 
        modelnamelist = modelname_worse
    
    step = step_list[model_chooser]
    
    maxlen = maxlen_list[model_chooser]
    
    model = load_model(modelnamelist[model_chooser])
    print("... Model loaded")
    


    with open('char-indeces.txt', 'r') as f:
        s = f.read()
        tmp = eval(s)
    
    char_indices = tmp[0]
    indices_char = tmp[1]

    f = open('textfile', 'r+')
    text = f.read()
    f.close()
        
    return [ X, maxlen, step, model, char_indices, indices_char, text  ]
        
        


def make_text(modelchooser, modeltype='best', diversity = 1.0, num_of_chars=300):

    X, maxlen, step, model, char_indices, indices_char, text = init_models_and_variables(modelchooser, modeltype)
    
    start_index = random.randint(0, len(text) - maxlen - 1)
    
    generated = ''
    sentence = text[start_index: start_index + maxlen]
    generated += sentence
    print('----- Generating with seed: "' + sentence + '"')
    
    for i in range(num_of_chars):
        x = np.zeros((1, maxlen, X.shape[2]))
        for t, char in enumerate(sentence):
            x[0, t, char_indices[char]] = 1.
        preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_char = indices_char[next_index]
    
        generated += next_char
        sentence = sentence[1:] + next_char
        
        sys.stdout.write(next_char)
        sys.stdout.flush()
    
    return generated 


#  modelchooser, modeltype='best', diversity = 1.0)

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("modelchooser", help="Choose a model: 0..2", type=int)
    parser.add_argument("modeltype", help="best or worse", type=str)
    parser.add_argument("diversity", help="Diversity: 0..1.2", type=float)
    parser.add_argument("num_of_chars", help="Number of Output Characters: (int)", type=int)
    
    args = parser.parse_args()
    print( sys.argv[1], sys.argv[2], sys.argv[3])
    
    gen_text = make_text(int(sys.argv[1]), sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))
    
    print( gen_text)
    