# -*- coding: utf-8 -*-
"""Untitled18.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TtN8LHhLJmzgUy6LdtPOCuhecAp3nzJF
"""





from pdb import set_trace
import mne
import pandas as pd
import numpy as np
import math
import os
import h5py
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN,LSTM, Dense, Activation, Bidirectional
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Convolution2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import EarlyStopping
global matrix_abn
global matrix_nor
matrix_nor= np.empty((750, 22), dtype='f')
matrix_abn= np.empty((750, 22), dtype='f')
chk1=0
import math
import argparse
from pathlib import Path
import csv

parser = argparse.ArgumentParser()
parser.add_argument("file_path", type=Path)

p = parser.parse_args()
edf_path = p.file_path
edf_file = mne.io.read_raw_edf(edf_path,  eog = ['FP1', 'FP2', 'F3', 'F4',
    'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8',
    'T3', 'T4', 'T5', 'T6', 'PZ', 'FZ', 'CZ', 'A1', 'A2'
    ], verbose = 'error', preload = True)

edf_file_down_sampled = edf_file.resample(250, npad = "auto")# set sampling frequency to 250 Hz
ed = edf_file_down_sampled.to_data_frame(picks = None, index = None, scalings = 100000,copy = True, start = None, stop = None)# converting into dataframe
Fp1_Fp7 = (ed.loc[: , 'FP1']) - (ed.loc[: , 'F7'])
FP2_F8 = (ed.loc[: , 'FP2']) - (ed.loc[: , 'F8'])
F7_T3 = (ed.loc[: , 'F7']) - (ed.loc[: , 'T3'])
F8_T4 = (ed.loc[: , 'F8']) - (ed.loc[: , 'T4'])
T3_T5 = (ed.loc[: , 'T3']) - (ed.loc[: , 'T5'])
T4_T6 = (ed.loc[: , 'T4']) - (ed.loc[: , 'T6'])
T5_O1 = (ed.loc[: , 'T5']) - (ed.loc[: , 'O1'])
T6_O2 = (ed.loc[: , 'T6']) - (ed.loc[: , 'O2'])
A1_T3 = (ed.loc[: , 'A1']) - (ed.loc[: , 'T3'])
T4_A2 = (ed.loc[: , 'T4']) - (ed.loc[: , 'A2'])
T3_C3 = (ed.loc[: , 'T3']) - (ed.loc[: , 'C3'])
C4_T4 = (ed.loc[: , 'C4']) - (ed.loc[: , 'T4'])
C3_CZ = (ed.loc[: , 'C3']) - (ed.loc[: , 'CZ'])
CZ_C4 = (ed.loc[: , 'CZ']) - (ed.loc[: , 'C4'])
FP1_F3 = (ed.loc[: , 'FP1']) - (ed.loc[: , 'F3'])
FP2_F4 = (ed.loc[: , 'FP2']) - (ed.loc[: , 'F4'])
F3_C3 = (ed.loc[: , 'F3']) - (ed.loc[: , 'C3'])
F4_C4 = (ed.loc[: , 'F4']) - (ed.loc[: , 'C4'])
C3_P3 = (ed.loc[: , 'C3']) - (ed.loc[: , 'P3'])
C4_P4 = (ed.loc[: , 'C4']) - (ed.loc[: , 'P4'])
P3_O1 = (ed.loc[: , 'P3']) - (ed.loc[: , 'O1'])
P4_O2 = (ed.loc[: , 'P4']) - (ed.loc[: , 'O2'])
data = {'Fp1_Fp7': Fp1_Fp7, 'FP2_F8': FP2_F8,	'F7_T3': F7_T3,'F8_T4': F8_T4,'T3_T5': T3_T5,'T4_T6': T4_T6,	'T5_O1': T5_O1,	'T6_O2': T6_O2,	'A1_T3': A1_T3,	'T4_A2': T4_A2,	'T3_C3': T3_C3,	'C4_T4': C4_T4,'C3_CZ': C3_CZ,'CZ_C4': CZ_C4,'FP1_F3': FP1_F3,	'FP2_F4': FP2_F4,	'F3_C3': F3_C3,	'F4_C4': F4_C4,	'C3_P3': C3_P3,	'C4_P4': C4_P4,	'P3_O1': P3_O1,	'P4_O2': P4_O2}
new_data_frame = pd.DataFrame(data, columns = ['Fp1_Fp7', 'FP2_F8', 'F7_T3', 'F8_T4', 'T3_T5', 'T4_T6', 'T5_O1', 'T6_O2', 'A1_T3', 'T4_A2', 'T3_C3', 'C4_T4', 'C3_CZ',	'CZ_C4', 'FP1_F3', 'FP2_F4', 'F3_C3', 'F4_C4', 'C3_P3', 'C4_P4', 'P3_O1', 'P4_O2'])
fs = edf_file_down_sampled.info['sfreq']
[row, col] = new_data_frame.shape
n = math.ceil(row / (750 - (fs /5)))

savedmodel = load_model('model3flipped_loss.hdf5')
#savedmodel2 = load_model("final_model")
#savedmodel2.load_weights('final_model_weights')

abn_times = []
i = 0;
j = 750;

for y in range(n-1):
    if y == 0:
        example = new_data_frame[0: 750]

    elif j < row:
        example = new_data_frame[i: j]

    elif y==n-2:
        example = new_data_frame[-750: ]

    example = example.to_numpy()
    example = np.expand_dims(example,axis = 2)
    example = np.swapaxes(example,0,2)
    example = example.astype('float32')

    new_pred = savedmodel.predict(example)
    #new_pred2 = savedmodel2.predict(example)
    print(y,new_pred)

    if new_pred[0][1]>=0.96:

        st = i/250

        rem = str(math.floor((st%1)*1000)).zfill(3)
        st = math.floor(st)
        et = st+3

        st_ss = st%60
        st_mm = (math.floor(st/60))%60
        st_hh = (math.floor(st/3600))%24
        et_ss = et%60
        et_mm = (math.floor(et/60))%60
        et_hh = (math.floor(et/3600))%24
        start = str(st_hh).zfill(2)+ ':' +str(st_mm).zfill(2)+ ':' +str(st_ss).zfill(2) + '.' +rem
        end = str(et_hh).zfill(2)+ ':' +str(et_mm).zfill(2)+ ':' +str(et_ss).zfill(2) + '.' + rem
        if not abn_times:
            abn_times = [[start,end]]
        else:
            abn_times.append([start,end])
    i = int(j - (fs / 5))
    j = int(j + 750 - (fs /5))

save_path = str(edf_path)[:-4] + '_pred.csv'
print(save_path)
with open(save_path, 'w', newline='') as file:
    writer = csv.writer(file)
    for i in abn_times:
        writer.writerow(i)
