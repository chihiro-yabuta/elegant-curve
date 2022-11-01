""" B-spline曲線として軌道を近似します.

近似の前提として用いるパラメータは、

* 軌道を4次のB-spline曲線にする.
* 元軌道1点あたりの誤差が10mm.
* 制御点を増やす基準(ある程度計算が収束したとみなす基準)が10nm.

入力として用いることができるのは、frame,x,y,zが格納されたcsvファイルです.
出力となるのは、json形式のファイルです(もし出力引数を省略した場合は標準出力に出ます).
ただし、コマンドライン引数の入出力としては、ディレクトリを用いることができます.
この場合，入力ファイル内の構造をそのまま出力ディレクトリ内にコピーするようにして、
jsonファイルが出力されます．

出力されるjsonファイルは、出力例にかかれている様なデータを持ちます.
ここで、"original_trajectory"は元軌道データであり、
(frame, x, y, z)の4次元データ列です.
"bspline"は近似後の軌道データを表す構造体です.
"control_point"は制御点を表す3次元位置列です.
"degree"はB-spline関数の次数を表すフィールドであり、この場合常に4です.
"desc"は近似に関する諸々の説明書きです(多分要らない).
"knot_vector"はノットベクトルです.
"parameter"は近似の際に用いた軌道のパラメータであり、
このパラメータが示すのは、i番目の元軌道位置がi番目のパラメータと同じ値を持つ媒介変数です.

入力例

.. csv-table::

    1.0,196.88789,1235.25183,-283.26071
    36.0,196.05135,1236.7179,-281.5545
    54.0,193.06856,1238.03357,-280.79343
    71.0,190.12811,1239.47803,-280.70285
    104.0,190.65826,1237.00903,-279.61865
    147.0,189.49339,1234.59534,-279.21158
    171.0,191.32785,1232.21436,-279.42682

出力例

.. code-block:: json

    {
        "original_trajectory": [],
        "bspline": {
            "control_point": [[]],
            "degree": 4,
            "desc": "",
            "knot_vector": [],
            "parameter": []
        }
    }

--filterオプションを追加することで、入力として指定されたディレクトリ内から、
その文字列を含むファイルのみを対象として近似処理を行うことができます.

--logオプションを用いることで、近似の途中仮定を.log形式のファイルとして出力することができます.
このファイルは、tab区切りのファイル形式で、計算回数、誤差の合計、途中の軌道形状などをまとめて
出力しています.

Examples:
    最もシンプルなioを行う場合

        $ python approximate_trajectories.py ./hoge.csv ./out.json

    この場合、hoge.csvのデータを近似し、out.jsonに出力します.

    ディレクトリレベルのioを行う場合

        $ python approximate_trajectories.py ./input ./output

    この場合、inputディレクトリ内に存在する全てのcsvデータに対して近似処理を行い、
    outputディレクトリ内に出力します.
    そのため、例えばinputディレクトリ内に1.csv,2.csv,3.csvが存在した場合、
    outputディレクトリ内には1.json,2.json,3.jsonが出力されます.

    --filterオプションを使う場合

        $ python approximate_trajectories.py --filter=TEST ./input ./output

    この場合、inputディレクトリ内に存在し、TESTをファイル名に含むファイルを入力として処理し、
    outputディレクトリに出力します.
    そのため、inputディレクトリ内にTEST.csv,HOGE.csv,FUGA.csvが存在した場合、
    outputディレクトリ内にはTEST.jsonが出力されます.

TODO:
    許容する誤差などを、外部から設定することができない.
    そのため、ちょっとパラメータをいじるためにもスクリプト内部をいじる必要がある.
    コマンドライン引数として取れるようにしたい.

.. seealso::

    :py:mod:`remove_unmoved_points`
        前処理を担当してくれるスクリプト

Usage:
    approximate_trajectories.py [--log] [--filter=<f>] <input> [<output>]
    approximate_trajectories.py -h

Options:
    --log  output log file(.log format)
    --filter=<f>  filter for input files

"""
import os
import sys
import csv
import json
import numpy as np
from .bspline.lspia import Lspia

def load(inputfile):
    """Generate trajectory from input file.

    ファイルをロードし、2次元の軌道データとして出力します.

    Args:
        inputfile (string): Input file name.

    Returns:
        Generator of splited trajectories.
    """
    traj = []
    with open(inputfile, "r") as f:
        for row in csv.reader(f):
            try:
                pos = [float(r) for r in row]
                traj.append(pos)
            except ValueError:
                pass
    return np.array(traj)

def write_result(original, param, p, knots, ctrls, output):
    """Write approximation result as json file.

    近似前後の軌道データを基もとに、jsonファイルとしてデータを出力してくれます.

    Args:
        original (vector array): Original trajectory
        p (int): degree of b-spline
        knots (array): knot vector
        ctrls (vector array): control points
        output (string): output file path
    """
    dst_obj = {
        "original_trajectory": original.tolist(),
        "bspline": {
            "desc": "LSPIAにより軌道をBスプラインに近似した結果",
            "parameter": param.tolist(),
            "degree": p,
            "knot_vector": knots.tolist(),
            "control_point": ctrls.tolist()
        }
    }
    dst_string = json.dumps(dst_obj, sort_keys=True, indent=4)
    if output is None:
        with sys.stdout as f:
            f.write(dst_string)
    else:
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))
        with open(output, "w") as f:
            f.write(dst_string)

def approximate(ipath, opath, average_error, lr):
    """Approximate a trajectory.

    B-spline関数の次数、入力ファイルパス、出力ファイルパスをもとに近似を行います.
    もしlogフラグがTrueにセットされていた場合、logファイルも同時に出力します.

    Args:
        p (int): degree of b-spline
        ipath (string): input file path
        opath (string or None): outpur file path
            if this arg is None, output to sys.stdout
        log (bool): If you need .log file, set True
    """
    traj = load(ipath)
    obj_err = average_error * len(traj)
    lspia = Lspia(
        traj[:, 1:],
        4,
        obj_err,
        average_error * lr
    )
    for p, knots, ctrls, err in lspia.run():
        pass
    write_result(
        traj,
        lspia.get_params(),
        lspia.get_degree(),
        lspia.get_knot_vector(),
        lspia.get_control_points(),
        opath
    )
