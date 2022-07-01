#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 04:56:53 2022

Main script that uses CamemBERT transformer to obtain predictability values for each word in a text sequence

First block imports utilities and the CamemBERT model and tokenizer

Second block defines the main function that processes sentences. Sentences are supposed to be lists of words. You can pass an array with many sentences. Each sentence will be trated independently.
The output is a list of predictability (kinda like probabilities, but not quite) levels for each word in the sentence. Actually it's a list of lists, one list for each sentence.

There is a block for model validation. See "validation_set.py" for details.

@author: Álvaro Cabana
"""

#%%  IMPORTS and model loading

import torch
import matplotlib.pyplot as plt
import process_textGrid as tg
import validation_set as vs
from transformers import CamembertForMaskedLM, CamembertTokenizer
from os import listdir
from scipy.io import savemat
import numpy as np


#load CamemBERT model
modelname = 'camembert-base' 

camembert = CamembertForMaskedLM.from_pretrained(modelname)
tokenizer= CamembertTokenizer.from_pretrained(modelname)
camembert.eval()


#%% main processing function, get predicted probabilities for each word
#compare the predicted vector for final token at the end of the sentence, with actual encoded vector
# sentences: list of sentences. each sentence should be a list of words
# sliding: if 0, attempts to use every previous word as context for word i. if not, use only the indicated number of previous words
def processSentence(sentence,sliding=0):
    print(sentence)
    word_probs = []
    for index,word in enumerate(sentence):
        #nTokens_per_word = len(torch.tensor(tokenizer.encode(word))) - 2 #if only one token for this word, this should be 1
        
        #if sliding is nonzero, only that number of preceding words will be used to build the sentence
        if sliding==0:
            firstWordIndex=0
        else:
            firstWordIndex=max(0,index-sliding)
        
        #actual sentence up to now
        sentence_up_to_now = " ".join(sentence[firstWordIndex:(index+1)])
        sentence_up_to_now += " ,"
        #sentence with lacking current word (replaced with mask)
        sentence_up_to_mask = " ".join(sentence[firstWordIndex:(index)])
        sentence_up_to_mask += " <mask> ,"
        #print(sentence_up_to_mask)
        
        
        tokens = torch.tensor(tokenizer.encode(sentence_up_to_now)).unsqueeze(0) # get tokens from CamemBERT
        tokens_predict = torch.tensor(tokenizer.encode(sentence_up_to_mask)).unsqueeze(0) # get tokens from CamemBERT
        all_vectors_predicted = camembert(tokens_predict)[0]

#            if nTokens_per_word>1:
 #               print(tokens)
  #              print(tokenizer.convert_tokens_to_string(tokens[0,-4].item()))
        #if the word corresponds to many tokens, need to average between these
        #these_vectors = all_vectors[0,[i for i in range(-3-nTokens_per_word,-3)],:]
        #these_vectors = all_vectors[:,[i for i in range(1,index+2)]]
        #sentence_vector = torch.mean(these_vectors,dim=1)
        #predicted_vector = all_vectors_predicted[:,-2,:] #if comma is removed, this should be -2
        predicted_vectors = all_vectors_predicted[0,-4,:]
        probs = predicted_vectors.softmax(dim=0)
        max_prob = max(probs)
        last_Token_index = tokens[:,-4]
        
        #word_cosines.append( probs[last_Token_index]/max_prob )
        last_token_prob = probs[last_Token_index]
        last_token_prob_norm = last_token_prob / max_prob
        word_probs.append(last_token_prob_norm.item())

        #for each word, embed the whole sentence up to that word, and extract the last vector (ignore sentencestart and finish tokens)        
    return(word_probs)


#%%% VALIDATION SET 

# get Validation set
validation_set = vs.getValidationSet()


congruent_values = [processSentence(s) for s in validation_set['congruent'] ]
incongruent_values = [processSentence(s) for s in validation_set['incongruent'] ]

incongruent_values[0]

plt.plot([x[-1] for x in congruent_values])
plt.plot([x[-1][1] - y[-1][1] for x,y in zip(congruent_values,incongruent_values)])


#%%  get Transcripts and process them with CamemBERT

#process_textGrid.py
textGrid_folder = "../data/wavfiles/aligned/revised/"
files = listdir(textGrid_folder)


filenames = np.array(list((filter(lambda x: x.endswith(".TextGrid") , files))),dtype=object)
phonemes = np.empty(filenames.shape,dtype="object")
words = np.empty(filenames.shape,dtype="object")
word_markings=np.empty(filenames.shape,dtype="object")
words=np.empty(filenames.shape,dtype="object")
phon_markings=np.empty(filenames.shape,dtype="object")


sliding=10 #sliding parameter. if 0, will use ALL previous context... don't think it can handle more than 100... see CamemBERT documentation for max sentence size...


for i,file in enumerate(filenames):
    all_markings = tg.parseTextGrid(textGrid_folder+file)
    xmin,xmax,text_markings = zip(*all_markings[0]) #[0] text markings, [1] phoneme markings
    probs = processSentence(text_markings,sliding)
    xminf = [float(x) for x in xmin]
    xmaxf = [float(x) for x in xmax]
    probsf= [float(x) for x in probs]
    word_markings[i]=np.array([xminf,xmaxf,probsf]).transpose()
    words[i]=text_markings
    xmin,xmax,p_markings = zip(*all_markings[1]) #[0] text markings, [1] phoneme markings
    xminf = [float(x) for x in xmin]
    xmaxf = [float(x) for x in xmax]
    phonemes[i]=p_markings
    phon_markings[i]=np.array([xminf,xmaxf]).transpose()
#markings = tg.parseTextGrid("../../transcriptions/renard1.TextGrid") #list, first  [0] are text markings, second [1] are phonetic markings
# text_markings = [m[0] for m in markings]
# phon_markings = [m[1] for m in markings]
# xmin,xmax,tmarkings = zip(*text_markings)

savemat("../data/embed.mat", {"word_markings":word_markings,"words":words,"phon_markings":phon_markings,"phonemes":phonemes,"filenames":filenames})

#markings_results = processSentences(tmarkings,sliding=50)
#output = list(zip(xmin,xmax,tmarkings,markings_results[0]))
#fxmin,fxmax,fmarkings = zip(*text_markings)
