'''
    ホガースカーブと抽出された美の線尿素の類似度を計算するプログラム
    それぞれの曲線を変曲点で分け，前半と後半部分としている．
    前半と後半部分をそれぞれ50点でリサンプリングし，弧ごとに相関係数を計算し出力
    出力はホガースカーブと美の線要素の類似度で，0~1の値で表される．
    1に近いほど類似度は大きい．
    弧ごとに計算しているので，出力は一つの美の線要素に対して2つである．
    〜.py ~.csv (b-splineサンプル点が格納されたファイル名)  ~tca.json (美の線か否かが記述されたjsonファイル)
'''

import numpy as np
import pandas as pd
import json
from scipy import interpolate
from .common.parameter_to_frame import *

data =[]

#リサンプリングする
def resample(t0, tf, dt):
    t = np.arange(t0, tf + dt, dt)
    f_x = interpolate.interp1d(t, tra_x, kind='linear')
    f_y = interpolate.interp1d(t, tra_y, kind='linear')
    f_z = interpolate.interp1d(t, tra_z, kind='linear')

    num = 51
    t_resample = np.linspace(t0, tf, num)

    return f_x(t_resample), f_y(t_resample), f_z(t_resample)

#曲率を計算するにあたり必要な微分をする
def diff(x_resample, y_resample, z_resample):
    for i in range(0, 50):
        x_diff = x_resample[i+1] - x_resample[i]
        y_diff = y_resample[i+1] - y_resample[i]
        z_diff = z_resample[i+1] - z_resample[i]
        data_fder.append([x_diff,y_diff,z_diff])
    return data_fder

#曲率を計算し，3点の移動平均を使用して滑らかに
def curvature(data_cur, data_cur_ave, data_array, data_array2):
    for l in range(0, len(data_array2)):
        k = (data_array[(l, 0)] * data_array2[(l, 1)] - data_array[(l, 1)] * data_array2[(l, 0)]) / ((data_array[(l, 0)] ** 2 + data_array[(l, 1)]** 2) ** 1.5)
        kk = k * ((data_array[(l, 0)] ** 2 + data_array[(l, 1)] ** 2) ** 0.5)
        data_cur.append(abs(kk))

    num=3
    b=np.ones(num)/num
    data_cur_ave = np.convolve(data_cur, b, mode='same')

    return data_cur_ave

def similarity(rpath, spath):
    json_tca = open(rpath, 'r')
    json_data = json.load(json_tca)
    data_array = np.array(json_data['bspline']['control_point'])
    for i in range(0, len(json_data['total_curvature_analysis']['curves'])):
        t_or_f = str(json_data['total_curvature_analysis']['curves'][i]['is_valid'])
        if t_or_f == 'True':
            mew1 = json_data['total_curvature_analysis']['curves'][i]['arcs'][0]['trimed_total_curvature']
            mew2 = json_data['total_curvature_analysis']['curves'][i]['arcs'][1]['trimed_total_curvature']
            if mew1 == None:
                mew1 = json_data['total_curvature_analysis']['curves'][i]['arcs'][0]['total_curvature']
            if mew2 == None:
                mew2 = json_data['total_curvature_analysis']['curves'][i]['arcs'][1]['total_curvature']
            ip1, t1, t2, t3, ip2 = parameter_get(json_data, i)
            _, t_n_s, t_n_c, t_n_f, _ = frame_get(json_data, 0, ip1, t1, t2, t3, ip2)

            if t_n_c - t_n_s < 5 or t_n_f - t_n_c < 5:
                print(-1, -1)
            else:
                print(t_n_s, t_n_c-3)
                for s in range(t_n_s, t_n_c-3):
                    tra_x = data_array[(s, 0)]
                    tra_y = data_array[(s, 1)]
                    tra_z = tra_z, data_array[(s, 2)]
                print(1)

                front_tra_x_resample, front_tra_y_resample, front_tra_z_resample = resample(0, t_n_c-t_n_s-4, 1)

                for s in range(t_n_c-3, t_n_f):
                    tra_x = data_array[(s, 0)]
                    tra_y = data_array[(s, 1)]
                    tra_z = data_array[(s, 2)]

                back_tra_x_resample, back_tra_y_resample, back_tra_z_resample = resample(0, t_n_f - t_n_c+2, 1)

                data_fder = []
                data_fder = diff(front_tra_x_resample, front_tra_y_resample, front_tra_z_resample)
                data_fder = diff(back_tra_x_resample, back_tra_y_resample, back_tra_z_resample)

                df=pd.DataFrame(data_fder)
                df.to_csv("First_order_derivative.csv",header=False, index=False)

                data_frame = pd.read_csv('First_order_derivative.csv', header = None)
                data_array = data_frame.values.astype(float)

                data_sder = []
                for j in range(0, len(data_array)-1):
                    x_sder = data_array[(j+1, 0)] - data_array[(j, 0)]
                    y_sder = data_array[(j+1, 1)] - data_array[(j, 1)]
                    z_sder = data_array[(j+1, 2)] - data_array[(j, 2)]
                    data_sder.append([x_sder,y_sder,z_sder])

                df=pd.DataFrame(data_sder)
                df.to_csv("Second_order_derivative.csv",header=False, index=False)

                data_frame = pd.read_csv('First_order_derivative.csv', header = None)
                data_array = data_frame.values.astype(float)
                data_frame2 = pd.read_csv('Second_order_derivative.csv' , header = None)
                data_array2 = data_frame2.values.astype(float)

                data_cur_ave = curvature([], [], data_array, data_array2)

                data_frame = pd.read_csv('hogarth_curve_curvature.csv', header=None)
                data_array = data_frame.values.astype(float)

                hogarth_data = []
                for ttt in range(0, len(data_array)):
                    hogarth_data.append(data_array[(ttt, 0)])

                cor_f, cor_b, hog_f, hog_b = [], [], [], []
                for cor in range(0, 49):
                    cor_f.append(data_cur_ave[cor])
                    hog_f.append(hogarth_data[cor])
                    cor_b.append(data_cur_ave[cor+49])
                    hog_b.append(hogarth_data[cor+49])

                x_f = [cor_f, hog_f]
                x_b = [cor_b, hog_b]

                print(np.corrcoef(x_f)[0, 1],np.corrcoef(x_b)[0, 1])

                data.append([np.corrcoef(x_f)[0, 1],np.corrcoef(x_b)[0, 1]])
                print(data)

    df = pd.DataFrame(data)
    df.to_csv(spath, header = False, index = False)
