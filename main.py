import os
from approximate_trajectories import approximate

target = os.listdir('csv')
if len(target) < 1:
    print('csv fileを1つ以上入れて下さい')
else:
    for t in target:
        t = t.replace('.csv', '')
        ipath = f'csv/{t}.csv'
        opath = f'json/{t}.json'
        approximate(4, ipath, opath, False)