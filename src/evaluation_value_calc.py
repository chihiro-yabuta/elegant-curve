'''
    美の線要素の評価値を計算するプログラム
    ホガースカーブとの類似度と両弧の弧長の比を考慮した式
    〜.py 〜.csv（類似度が入ったファイル） ~tca.json
'''

import pandas as pd
import math
import json

def value_calc(ipath, rpath, opath):
    data_frame = pd.read_csv(ipath, header=0)
    data_array = data_frame.values.astype(float)
    json_tca = open(rpath, 'r')
    json_data = json.load(json_tca)#jsonファイルを計算できる形する
    n = 0
    #弧長と両弧の比を考慮した評価値の計算
    for i in range(0, len(json_data['total_curvature_analysis']['curves'])):
        t_or_f = str(json_data['total_curvature_analysis']['curves'][i]['is_valid'])# 美の線ですか?
        if t_or_f == 'True'or 'False':
            data_frame = pd.read_csv(ipath, header=0)
            data_array = data_frame.values.astype(float)
            json_tca = open(rpath, 'r')
            json_data = json.load(json_tca)#jsonファイルを計算できる形する
            l1 = json_data['total_curvature_analysis']['curves'][i]['arcs'][0]['trim_length']#美の線前半の弧長
            l2 = json_data['total_curvature_analysis']['curves'][i]['arcs'][1]['trim_length']#美の線後半の弧長

            if not (data_array[(n, 0)] == 'nan' or data_array[(n, 1)] == 'nan'):
                d1 = (data_array[(n, 0)] + 1) / 2
                d2 = (data_array[(n, 1)] + 1) / 2
                length_ratio = abs((l1-l2)/(l1+l2))
                eva_value = (l1 + l2) * math.exp(-(1-d1) -(1-d2) -length_ratio)#評価値の計算（ここが美の線要素評価モデルなので，好きにいじってみるとおもしろい）
                n = n + 1
            if t_or_f == 'True':
                with open(opath, 'a', encoding = 'utf-8') as f:
                    f.write(str(eva_value))
                    f.write('\n')
