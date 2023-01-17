'''
美の線要素のパラメータとフレームを対応させるために使うものです．
jsonを読み取って対応させるだけなので，ややこしいことはしていないです( ・∇・)

ip1, t1, t2, t3, ip2 = parameter_get(json_data, i)
t_n_ip1, t_n_s, t_n_c, t_n_f, t_n_ip2 = frame_get(json_data, 0, ip1, t1, t2, t3, ip2)
'''

import numpy as np
import pandas as pd
import sys
import json

#S字区間と美の線要素区間のパラメータを取得する関数
def parameter_get(json_data, i):
    ip1 = json_data['total_curvature_analysis']['curves'][i]['ts'][0]#S字セグメントの始まり
    t1 = json_data['total_curvature_analysis']['curves'][i]['arcs'][0]['trim_ts'][0]#美の線の始まり
    t2 = json_data['total_curvature_analysis']['curves'][i]['arcs'][0]['trim_ts'][1]#変曲点
    t3 = json_data['total_curvature_analysis']['curves'][i]['arcs'][1]['trim_ts'][1]#美の線の終わり
    ip2 = json_data['total_curvature_analysis']['curves'][i]['ts'][2]#S字セグメントの終わり

    return ip1, t1, t2, t3, ip2

#S字区間と美の線要素区間のフレームを返す関数
def frame_get(json_data, t_n, ip1, t1, t2, t3, ip2):
    while 1:#S字セグメントの始まりのフレーム数を取得
        if ip1 <= json_data['bspline']['parameter'][t_n]:
            t_n_ip1 = t_n+1#S字セグメントの始まりが，媒介変数では何番目かを取得
            break
        t_n = t_n + 1
    while 1:#美の線要素の始まりのフレーム数を取得
        if t1 <= json_data['bspline']['parameter'][t_n]:
            t_n_s = t_n+1#美の線要素始まりが，媒介変数では何番目かを取得
            break
        t_n = t_n + 1
    while 1:#変曲点のフレーム数を取得
        if t2 <= json_data['bspline']['parameter'][t_n]:
            t_n_c = t_n+1#変曲点が，媒介変数では何番目かを取得
            break
        t_n = t_n + 1
    while 1:#美の線要素の終わりのフレーム数を取得
        if t3 <= json_data['bspline']['parameter'][t_n]:
            t_n_f = t_n+1#美の線要素終わりが，媒介変数では何番目かを取得
            break
        t_n = t_n + 1
    while 1:#S字セグメントの終わりのフレーム数を取得
        if ip2 <= json_data['bspline']['parameter'][t_n]:
            t_n_ip2 = t_n+1#S字セグメントの始まりが，媒介変数では何番目かを取得
            break
        t_n = t_n + 1
    return t_n_ip1, t_n_s, t_n_c, t_n_f, t_n_ip2

