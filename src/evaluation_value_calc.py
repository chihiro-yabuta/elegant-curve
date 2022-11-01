#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    美の線要素の評価値を計算するプログラム
    ホガースカーブとの類似度と両弧の弧長の比を考慮した式
    〜.py 〜.csv（類似度が入ったファイル） ~tca.json
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import json
import sys
args = sys.argv

def evaluation_value_calc(ipath):
    data_frame = pd.read_csv(ipath, header=None)
    data_array = data_frame.values.astype(float)
    json_tca = open('json/result.json', 'r')
    json_data = json.load(json_tca)#jsonファイルを計算できる形する

    n = 0
    #弧長と両弧の比を考慮した評価値の計算
    for i in range(0, len(json_data['total_curvature_analysis']['curves'])):
        t_n = 0
        t_or_f = str(json_data['total_curvature_analysis']['curves'][i]['is_valid'])# 美の線ですか?
        print(t_or_f)
        if t_or_f == 'True'or 'False':
            data_frame = pd.read_csv(args[1], header=None)
            data_array = data_frame.values.astype(float)
            json_tca = open(args[2], 'r')
            json_data = json.load(json_tca)#jsonファイルを計算できる形する
            l1 = json_data['total_curvature_analysis']['curves'][i]['arcs'][0]['trim_length']#美の線前半の弧長
            l2 = json_data['total_curvature_analysis']['curves'][i]['arcs'][1]['trim_length']#美の線後半の弧長
            
            if data_array[(n, 0)] == 'nan' or data_array[(n, 1)] == 'nan':
                print(0)
            else:
                d1 = (data_array[(n, 0)] + 1) / 2
                d2 = (data_array[(n, 1)] + 1) / 2
                length_ratio = abs((l1-l2)/(l1+l2))
                eva_value = (l1 + l2) * math.exp(-(1-d1) -(1-d2) -length_ratio)#評価値の計算（ここが美の線要素評価モデルなので，好きにいじってみるとおもしろい）
                n = n + 1
                print(eva_value)
