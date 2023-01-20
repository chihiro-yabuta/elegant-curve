"""全曲率を用いた軌道の解析を行います.

このスクリプトが担当するのは、
3次元の近似後データ(BSpline関数)を
舞踊名によって定まる2次元平面に投影し、
2次元軌道とすること.
及びその2次元軌道が持つ形状特徴を計算し、
jsonデータとして格納することです.
抑えて頂きたいのは、 **評価値を計算しない** ところです.

アルゴリズムについての説明:

    jsonファイルに格納された3次元の軌道データを、
    そのまま2次元に落とし込みます(SecondDimensionalizeクラスを参照).
    このとき、データまでのファイルパス内に存在する舞踊名から、
    投影する2次元平面を決定します.

    2次元になった軌道に対して、変曲点を算出します(calc_inflection_points関数).
    変曲点群に対して、軌道の端点も追加し、今後は端点も含めて変曲点として扱います.
    算出された変曲点群に対して、
    連続する3つの変曲点位置を取り出すことで、S字状カーブを取り出します.

    取り出されたS字状カーブに対して、curve_analysis関数でさらに解析を行います.
    この関数では、まず全曲率を各S字状カーブについて計算します.
    全曲率については :py:mod:`total_curvature` を参照してください.
    その後、UNDER_TOTAL_CURVATURE、BEST_TOTAL_CURVATURE変数をもとに、
    全曲率がUNDER_TOTAL_CURVATURE以上、BEST_TOTAL_CURVATURE以下になるように、
    S字状カーブをトリミングし、美の線要素を取り出します.

    取り出された美の線要素に対して、
    全曲率や弧長のパラメータ、
    さらにそれらがどのような経緯で取り出されたのかを記述し、
    jsonファイルに出力します.

入力データ:

    入力データとしては、"bspline"フィールドをもつjsonファイルを受け付けます.
    さらに、"bspline"フィールドの内部には、"degree"、
    "knot_vector"、"control_point"のフィールドがなければなりません.
    入力データのイメージを以下に示します.

    .. code:: json

        {
            "bspline": {
                "degree": 4,
                "knot_vector": [],
                "control_point": [
                    [],
                    []
                ]
            }
        }

    もしくは、この形式にそったjsonファイルが格納された
    ディレクトリを設定することも可能です.
    ディレクトリを設定した場合、各ファイルを順に処理し、
    出力ディレクトリ内に同じ木構造を構築します.

出力データ:

    出力データは、入力データの値を全て保持します.
    さらに、それに加えて、解析データを出力します.
    出力データのイメージを以下に示します.

    .. code:: json

        {
            "bspline": {},
            "total_curvature_analysis": {
                "axis": [
                    [],[],[]
                ],
                "desc": "",
                "inflection_points": [],
                "curves": [
                    {
                        "ts": [],
                        "is_valid": True,
                        "arcs": [
                            {
                                "original_ts": [],
                                "trim_ts": [],
                                "total_curvature": 1.45,
                                "is_trimed": [],
                                "trimed_total_curvature": 1.31,
                                "original_length": 1000,
                                "trim_length": 500
                            },
                            {
                                "original_ts": [],
                                "trim_ts": [],
                                "total_curvature": 1.45,
                                "is_trimed": [],
                                "trimed_total_curvature": 1.31
                                "original_length": 1000,
                                "trim_length": 500
                            }
                        ]
                    }
                ]
            }
        }

    ここで、"bspline"フィールドは入力データが
    そのまま格納されているので省略します.
    重要なのは"total_curvature_analysis"フィールドです.
    このスクリプトで解析した結果は全てこのフィールド内部に格納されます.
    まず、"axis"には投影した平面を表す行列データがそのまま格納されています.
    "desc"には説明書きを一応書いてあります(多分使わないでしょう).
    "inflection_points"には求めた変曲点群が格納されています.
    媒介変数のリストです.
    "curves"には分割されたS字状カーブについてのデータがリストで入っています.
    この例では一つだけ掲載していますが、もっとあると考えるのが基本でしょう.
    "ts"はそのS字状カーブが媒介変数ではどこに位置するのかを記載しています.
    "is_valid"はS字状カーブから美の線要素が取り出されたかを示すbool値です
    (美の線要素ならTrue).
    "arcs"にはそのS字状カーブが持つ各弧(変曲点から変曲点まで)
    のデータが入っています.
    リストになっていますが、S字状カーブは２つしか弧を持たないため、
    このリストの要素数は常に2です.
    "original_ts"には弧が媒介変数ではどこからどこまでなのかを格納しています.
    "trim_ts"には弧の全曲率が大きすぎて、
    美の線要素になるためにトリミングされた場合に、
    トリミング範囲を媒介変数で格納しています
    (それ以外の場合、不正な値が入っていると思うので参照しないこと).
    トリミングされたかどうかを"is_trimed"で確認することができます.
    "total_curvature"は"original_ts"の範囲で計算した場合の全曲率です.
    "trimed_total_curvature"はトリミング後の全曲率です.
    "original_length"はトリミング前の弧長、
    "trim_length"はトリミング後の弧長です.
    様々なデータに一貫して言えることですが、
    "is_trimed"がTrueではない場合
    (つまり、全曲率がBEST_TOTAL_CURVATUREより小さくトリミングされなかった場合)、
    にトリミング後の何々系のデータは不正な値が入っている
    可能性があるので参照しないことをおすすめします.

Warnings:

    * 評価値の計算をしてくれるわけでは無い.
    * データまでのファイルパスに舞踊名が含まれている必要がある.

.. seealso::

    :py:mod:`score_analysis_total_curvature`
        評価値の計算をしてくれるすごいやつ.

    :py:mod:`approximate_trajectories`
        前提として想定しているスクリプト.

Usage:
    total_curvature_analysis.py <input> [<output>]
    total_curvature_analysis.py -h

Options:
    -h, --help  Show this help
"""
import json
import csv
import numpy as np
from tqdm import tqdm
import scipy.optimize as so
import scipy.integrate as si
from .bspline.base import BSpline
from .common.projected_bspline import ProjectedBSpline
from .common.total_curvature import Curvature, TotalCurvature
from .common.viewport import get_plane_matrix

UNDER_TOTAL_CURVATURE = np.deg2rad(50.0)
"""float: 取り出す全曲率の下限値
"""

BEST_TOTAL_CURVATURE = np.deg2rad(75.0)
"""float: 全曲率がこの値になるように取り出されます．
"""
cr_num = 0

class SecondDimensionalize:
    """３次元軌道を2次元上に落とします

    3次元軌道のうち，0,1要素を取り出すことで2次元軌道の関数にします．
    何か特別な何かをすることで2次元化するわけではありません．

    Args:
        func (function): 3次元軌道の関数

    Attributes:
        func (function): 3次元軌道の関数
        mat (matrix): 3次元軌道の0, 1要素を取り出して2次元に落とす行列
    """

    def __init__(self, func):
        self.mat = np.array(
            [[1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0]]
        )
        self.func = func

    def __call__(self, t):
        return np.dot(self.mat, self.func(t))

    def diff(self):
        """微分値を返します

        微分関数は3次元軌道の微分値を2次元に落としたものです．

        Returns:
            SecondDimensionalize: 2次元軌道
        """
        return(
            SecondDimensionalize(self.func.diff())
        )

def get_dances():
    """舞踊名のリストを返します

    Returns:
        list: 舞踊名のリスト
    """
    return [
        "hula",
        "india",
        "jawa",
        "myan",
        "nichibu",
        "pepper"
    ]

def build_viewport_axis_str(dancename):
    """舞踊名から投影平面を返します.

    Args:
        dancename (str): ファイル名

    Returns:
        str: 舞踊名
            "hula", "india", "jawa", "myan", "nichibu", "pepper"

    """
    return "xy"
'''
    if dancename == "hula":
        return "-zy"
    elif dancename == "india":
        return "-zy"
    elif dancename == "jawa":
        return "xy"
    elif dancename == "myan":
        return "xy"
    elif dancename == "nichibu":
        return "xy"
    elif dancename == "pepper":
        return "yz"
    else:
        return None
'''

def get_dancename(filename):
    """ファイル名から舞踊名を返します

    Args:
        filename (str): ファイル名

    Returns:
        str: 舞踊名
    """
    dances = get_dances()
    for d in dances:
        if d in filename:
            return d

def get_viewport_axis(filename):
    """視点方向の行列を返します

    Args:
        filename (str): ファイル名

    Returns:
        matrix: 視点方向を表す行列
    """
    dancename = get_dancename(filename.lower())
    axis_str = build_viewport_axis_str(dancename)
    axis_matrix = get_plane_matrix(axis_str)
    return np.r_[
        axis_matrix,
        [np.cross(axis_matrix[0], axis_matrix[1])]
    ]

def load_json(filename):
    """jsonファイルのロード

    Args:
        filename (str): ファイル名

    Returns:
        dict: jsonの中身
    """
    with open(filename) as f:
        return json.load(f)

def calc_inflection_points(pbsp, trange=None, n_splits=None, ts=None):
    """変曲点を計算します

    Args:
        pbsp (projected_bspline.ProjectedBSpline): 軌道
        trange (Touple[float]): 変曲点を計算する範囲.
            Noneの場合、(0.0, 1.0)になります.
        n_splits (int): 変曲点を計算する際に、分割する個数.
            Noneの場合、100000になります.
        ts (array): 分割した媒介変数群.
            Noneの場合、trangeとn_splitsによって決定されます.

    Returns:
        List[float]: 変曲点の媒介変数位置
    """
    cf = Curvature(pbsp)
    if ts is None:
        if trange is None:
            trange = (0.0, 1.0)
        if n_splits is None:
            n_splits = 100000
        ts = np.linspace(trange[0], trange[1], n_splits)
    dsts = []
    for a, b in tqdm(zip(ts, ts[1:])):
        try:
            dsts.append(so.brentq(cf, a, b))
        except ValueError as e:
            pass
    return dsts

def search_trim_point(total_curvature_func, ts):
    """ 軌道中から、切り取るべきポイントを探します

    Args:
        total_curvature_func (function): 軌道の全曲率がどの程度理想に近いかを示す値．
                                         この値が0になる場所を探索します
        ts (list[float]): 探索範囲
    """
    return so.brentq(total_curvature_func, ts[0], ts[1])

def calc_length(pbsp, trange):
    """軌道の長さを計算します.

    Args:
        pbsp (function): diff関数をもち、微分できる必要があります.
        trange (Touple[float]): 軌道長計算する媒介変数の範囲

    Returns:
        float: 軌道長
    """
    diff = pbsp.diff()
    length_func = (lambda t: np.sum(diff(t) * diff(t)) ** 0.5)
    length, err = si.quad(length_func, trange[0], trange[1], limit=10000)
    return length

def set_length_field(func, arc_dict):
    """ある解析結果について、長さに関するフィールドを埋めます

    Note:
        この関数には副作用があります.
        arc_dictを汚染します.

    Args:
        func (function): 長さを計算する軌道
        arc_dict (dict): 長さを保存するディレクトリ

    Returns:
        dict: arc_dictと同じものです
    """
    arc_dict["original_length"] = calc_length(func, arc_dict["original_ts"])
    arc_dict["trim_length"] = calc_length(func, arc_dict["trim_ts"])
    return arc_dict

def curve_analysis(pbsp, tb, tc, te):
    """ある軌道(S字状カーブ)を解析します

    Args:
        pbsp (ProjectedBSpline): 投影された軌道
        tb (float): 解析の始点を表す媒介変数
        tc (float): 変曲点を表す媒介変数
        te (float): 解析の終点を表す媒介変数

    Returns:
        dict: 解析結果を格納したディクショナリ
    """
    total_curvature_func = TotalCurvature(pbsp)
    curve = {
        "ts": (tb, tc, te),
        "is_valid": None,
        "arcs": []
    }
    total_curvature_begin = total_curvature_func(tb, tc)
    arc_begin = {
        "original_ts": (tb, tc),
        "trim_ts": None,
        "total_curvature": total_curvature_begin,
        "is_trimed": False,
        "trimed_total_curvature": None
    }
    total_curvature_end = total_curvature_func(tc, te)
    arc_end = {
        "original_ts": (tc, te),
        "trim_ts": None,
        "total_curvature": total_curvature_end,
        "is_trimed": False,
        "trimed_total_curvature": None
    }
    if (total_curvature_begin >= UNDER_TOTAL_CURVATURE and
            total_curvature_end >= UNDER_TOTAL_CURVATURE):
        curve["is_valid"] = True
        if total_curvature_begin >= BEST_TOTAL_CURVATURE:
            tc_func = (
                lambda t: (
                    total_curvature_func(t, tc) -
                    BEST_TOTAL_CURVATURE
                )
            )
            tb_dash = search_trim_point(
                tc_func,
                (tb, tc)
            )
            arc_begin["is_trimed"] = True
            arc_begin["trimed_total_curvature"] = BEST_TOTAL_CURVATURE
        else:
            tb_dash = tb
        arc_begin["trim_ts"] = (tb_dash, tc)

        if total_curvature_end >= BEST_TOTAL_CURVATURE:
            tc_func = (
                lambda t: (
                    total_curvature_func(tc, t) -
                    BEST_TOTAL_CURVATURE
                )
            )
            te_dash = search_trim_point(
                tc_func,
                (tc, te)
            )
            arc_end["is_trimed"] = True
            arc_end["trimed_total_curvature"] = BEST_TOTAL_CURVATURE
        else:
            te_dash = te
        arc_end["trim_ts"] = (tc, te_dash)
    else:
        arc_begin["trim_ts"] = (tb, tc)
        arc_end["trim_ts"] = (tc, te)
        curve["is_valid"] = False
    arc_begin = set_length_field(pbsp, arc_begin)
    curve["arcs"].append(arc_begin)
    arc_end = set_length_field(pbsp, arc_end)
    curve["arcs"].append(arc_end)
    return curve

def analysis(pbsp):
    """軌道データ全体を解析します

    Args:
        pbsp (projected_bspline.ProjectedBSpline): 軌道

    Returns:
        dict: 解析結果
    """
    global cr_num
    dst = {
        "desc": ("total_curvature_analysisによって作られたデータ\n" +
                 "変曲点3つを一つのS字とし，ホガースの示した美の線に近づくように一部を取り出すような処理をします．"),
        "curves": []
    }
    inf_points = calc_inflection_points(pbsp)
    dst["inflection_points"] = inf_points
    if 0.0 not in inf_points:
        inf_points.insert(0, 0.0)
    if 1.0 not in inf_points:
        inf_points.append(1.0)
    for tb, tc, te in tqdm(zip(inf_points, inf_points[1:], inf_points[2:])):
        dst["curves"].append(
             curve_analysis(pbsp, tb, tc, te)
        )
    cr_num = len(dst["curves"])
    return dst

def build_bspline(bspline_dict):
    """Bspline関数を構築します

    Args:
        bspline_dict (dict): BSpline関数のパラメータ

    Returns:
        bspline.base.BSpline: 軌道
    """
    return BSpline(
        int(bspline_dict["degree"]),
        np.array(bspline_dict["knot_vector"]),
        np.array(bspline_dict["control_point"])
    )

def analyze_curvature(apath, bpath, rpath):
    """main関数

    Args:
        input_arg (str): 入力ファイルもしくはディレクトリ
        output_arg (str): 出力ファイルもしくはディレクトリ
    """
    global cr_num
    json_data = load_json(apath)
    param = json_data['bspline']['parameter']
    traj_func = SecondDimensionalize(
        ProjectedBSpline(
            build_bspline(json_data["bspline"]),
            get_viewport_axis(apath)
        )
    )

    pbb = ProjectedBSpline(build_bspline(json_data['bspline']),get_viewport_axis(apath))
    with open(bpath, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(len(param)):
            writer.writerow(pbb(param[i]))

    result = analysis(traj_func)
    result["axis"] = traj_func.func.axis.tolist()
    json_data["total_curvature_analysis"] = result
    with open(rpath, "w", encoding="utf-8") as f:
        json.dump(json_data, f, sort_keys=True, indent=4)