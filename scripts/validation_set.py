#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 09:42:14 2022

Validation set of congruent and incongruent sentences, taken from Azevedo et al (2022) 10.1075/ml.20032.aze


@author: Álvaro Cabana
"""

def getValidationSet():
    validation_n400_file = open("../data/validation1.n400.txt")
    cong = []
    incong = []
    for line in validation_n400_file:
        mots = line.split()
        mots_incong = mots[0:(len(mots)-1)]
        incong.append(mots_incong)
        mots_cong = mots[0:(len(mots)-2)]+ [mots[-1] ]
        cong.append(mots_cong)
    return({'congruent' : cong,'incongruent' : incong})