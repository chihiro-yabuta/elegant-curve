avarage_error, lr = 10, 1e-3 #自由に変えて下さい 初期値: 0.001, 1e-3
#途中で絶対止まるのでファイルは１個ずつ実行すること
#outputは直で上書きするので都度削除すること

import os
from src.approximate_trajectories import approximate
from src.total_curvature_analysis import analyze_curvature
from src.evaluation_value_calc import value_calc
from src.degree_of_similarity import similarity

target = os.listdir('input')
if len(target) < 1:
    print('csv fileを1つ以上入れて下さい')
else:
    for t in target:
        print(f'target -> {t}')
        t = t.replace('.csv', '')
        ipath = f'input/{t}.csv'
        apath = f'archive/axis/{t}.json'
        bpath = f'archive/bspline/{t}.csv'
        rpath = f'archive/result/{t}.json'
        spath = f'archive/similar/{t}.csv'
        fpath = f'output/{t}.csv'
        print('doing approximate')
        approximate(ipath, apath, avarage_error, lr)
        print('\ndoing analyze_curvature')
        analyze_curvature(apath, bpath, rpath)
        print('doing similarity')
        similarity(bpath, rpath, spath)
        print('doing score_curvature')
        value_calc(spath, rpath, fpath)
        print('\ndone\n')
