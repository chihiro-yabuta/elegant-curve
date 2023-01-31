# 評価値から美の曲線グラフを作るプログラム
import json, matplotlib.pyplot as plt, numpy as np
from src.common.parameter_to_frame import parameter_get, frame_get

#ファイル名，変曲点のインデックス番号
name = '06'
i = 0

bpath = f'archive/bspline/{name}.csv'
rpath = f'archive/result/{name}.json'
json_tca = open(rpath, 'r')
json_data = json.load(json_tca)
#isvalid = falseの場合は飛ばす

ip1, t1, t2, t3, ip2 = parameter_get(json_data, i)
print(ip1, t1, t2, t3, ip2)
t_n_ip1, t_n_s, t_n_c, t_n_f, t_n_ip2 = frame_get(json_data, 0, ip1, t1, t2, t3, ip2)
print(t_n_s, t_n_f)

pos = []
with open(bpath) as f:
    for s in f.read().split('\n')[t_n_s:t_n_f+1]:
      pos.append(list(map(float, s.split(',')))[:2])
pos = np.array(pos)
plt.plot(pos[:,0], pos[:,1])
plt.xlabel('pixel')
plt.ylabel('pixel')
plt.savefig(f'{name}.png')