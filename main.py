avarage_error, lr = 100, 1e-3 #自由に変えて下さい 初期値: 0.001, 1e-3

import os
from src.approximate_trajectories import approximate
from src.total_curvature_analysis import analyze_curvature
from src.evaluation_value_calc import value_calc
from src.degree_of_similarity import similarity

target = os.listdir('csv')
if len(target) < 1:
    print('csv fileを1つ以上入れて下さい')
else:
    for t in target:
        print(f'target -> {t}')
        t = t.replace('.csv', '')
        ipath = f'csv/{t}.csv'
        opath = f'json/{t}.json'
        rpath = f'result/{t}.json'
        spath = f'similar/{t}.json'
        print('doing approximate')
        approximate(ipath, opath, avarage_error, lr)
        print('\ndoing analyze_curvature')
        analyze_curvature(opath, rpath)
        print('doing similarity')
        similarity(rpath, spath)
        print('doing score_curvature')
        value_calc(spath, rpath)
        print('\ndone\n')
