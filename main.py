#p: 4, avarage_error: 0.001, lr: 1e-3
import os
from approximate_trajectories import approximate

target = os.listdir('csv')
if len(target) < 1:
    print('csv fileを1つ以上入れて下さい')
else:
    for t in target:
        print(f'loading {t}')
        t = t.replace('.csv', '')
        ipath = f'csv/{t}.csv'
        opath = f'json/{t}.json'
        approximate(4, ipath, opath, 0.001, 1e-3)
        print('done')