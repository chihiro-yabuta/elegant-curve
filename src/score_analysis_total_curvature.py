""" 全曲率を用いた解析結果を得点化し印象評価実験との相関を
重回帰分析によりとります.

入力(<input>)としては、total_curvature_analysisによって出力された、
jsonファイルが格納されたディレクトリを用います.
ここで、jsonファイルの親ディレクトリには、
舞踊名が含まれていることが絶対に必要です.

もう一つの入力(<score>)として、印象評価実験の結果(因子得点)を用います.
このデータのフォーマットを以下に示します.

.. csv-table::

    hula,0.204888232984986,0.2146166125086998,-0.1134436783460195,0.613486252583883
    jawa,0.3035526086265767,-0.1065188965042756,-0.1269955733951140,-0.542384950961065
    india,-0.0723181787969881,-0.4344110962254697,0.0638067966331706,-0.762650685266648
    nichibu,-0.131822740295362,0.554565254618560,-0.0819046424277978,0.477314229900343
    myan,-0.3042999225192132,-0.2282518743975146,0.2585370975357602,0.214235153743487

このとき、第二因子を対象として計算を行います.
もし変更したい場合は、load_score関数の中身を変更して下さい.

出力は標準出力に出ます.

-sオプションを有効にしない場合、
長さのみを特徴量として用います.
-sオプションをつけた場合、
以下の方法で得点を計算し、印象評価との相関をとります.

.. topic:: 得点の計算方法

    動作軌道得点は、

    * 美の線要素の得点
    * 美の線要素の集合としての軌道評価

    この2点により行われます.

    美の線要素は、次式で評価されます.

    .. math::

        s = (l_1+l_2)exp\\left(
            -\\left|\\frac{\\mu_1-1.31}{1.31-0.87}\\right|
            -\\left|\\frac{\\mu_2-1.31}{1.31-0.87}\\right|
            -\\left|\\frac{l_1-l_2}{l_1+l_2}\\right|
        \\right)

    ここで、 :math:`l_1` 、 :math:`l_2` は取り出された美の線要素の弧長です.
    :math:`\\mu_1` 、 :math:`\\mu_2` は各弧の全曲率です.

    軌道全体は、美の線要素の評価値を平均し、
    美の線要素の弧長を掛け、全弧長で割ることで算出します.
    詳細は論文かコードを直接読んでください(calc_score関数).

Warnings:
    舞踊名がファイルパスに含まれない舞踊データを取り扱うことができない.
    また、各舞踊には両手以外のデータが含まれていないことが絶対条件.
    対象とする因子が第二因子に固定されている.

Note:
    評価値の計算もここでやることになってるので、なんとかしたい.
    責任の分割って大事なのに

.. seealso::

    :py:mod:`total_curvature_analysis`
        全曲率を用いた解析をしてくれるスクリプト

Usage:
    score_analysis_total_curvature.py [-s] <input> <score>
    score_analysis_total_curvature.py -h

Options:
    -h, --help  Show this help
    -s, --score  Use score as OLS input.
"""
import csv
import json
import numpy as np
import statsmodels.api as sm
import src.total_curvature_analysis as tca


def load(filename):
    """解析結果を格納したjsonファイルをロードします

    Args:
        filename (str): ファイル名

    Returns:
        object: jsonファイルの中身
    """
    with open(filename) as f:
        return json.load(f)


def get_dances():
    """舞踊名のリストを返します

    Returns:
        list: 舞踊名のリスト
    """
    return [
        "hula",
        "india",
        "jawa",
        "myanmar",
        "nichibu"
    ]


def get_hand(filename):
    """ファイル名から手の左右を返します

    Args:
        filename (str): ファイル名

    Returns:
        str: 右手なら"R",左手なら"L"
    """
    if "R.Pinky" in filename:
        return "R"
    elif "L.Pinky" in filename:
        return "L"


def get_dances_name(path):
    """ファイル名から舞踊名を取得します

    Args:
        path (str): ファイル名

    Returns:
        str: 舞踊名
    """
    for d in get_dances():
        if d in path:
            return d


def calc_lengthratio(json_data):
    """jsonファイルのオブジェクトから長さの割合を返します

    Args:
        json_data (object): jsonファイルの中身

    Returns:
        float: スコアの平均値
    """
    tc_data = json_data["total_curvature_analysis"]
    o_lens = []
    t_lens = []
    for curve in tc_data["curves"]:
        for arc in curve["arcs"]:
            o_lens.append(arc["original_length"])
            if curve["is_valid"]:
                t_lens.append(arc["trim_length"])
    return np.sum(np.array(t_lens)) / np.sum(np.array(o_lens))


def load_lengthes(input_dir):
    """ディレクトリ名から格データを読み込み，スコアを格納します

    Args:
        input_dir (str): ファイルが格納されたディレクトリ名

    Returns:
        object: 舞踊名と手の名前をキーとしscoreを格納したディクショナリ
    """
    dst = {}
    for d in get_dances():
        dst[d] = {}
        dst[d]["R"] = 0.0
        dst[d]["L"] = 0.0
    name = get_dances_name(input_dir)
    hand = get_hand(input_dir)
    json_data = load(input_dir)
    score = calc_lengthratio(json_data)
    dst[name][hand] = score
    return dst


def create_lengthratio_matrix(input_dir):
    """長さの割合を格納した行列を作成します

    Args:
        input_dir (str): ファイルがロードされたディレクトリ名

    Returns:
        matrix: 行列
    """
    data = load_lengthes(input_dir)
    print(data)
    dst = []
    for d in get_dances():
        dst.append([
            1.0,
            data[d]["R"],
            data[d]["L"]
        ])
    return np.array(dst)


def calc_curve_size_score(curve_object):
    """curveが持つ大きさに関する項を計算します

    Args:
        curve_object (dict): curveオブジェクト

    Returns:
        float: そのカーブの大きさ
    """
    trimed_length = []
    for arc in curve_object["arcs"]:
        trimed_length.append(arc["trim_length"])
    return trimed_length[0] + trimed_length[1]


def calc_curve_quality_score(curve_object):
    """curveが持つS字の質に関する項を計算します

    Args:
        curve_object (dict): curveオブジェクト

    Returns:
        float: そのカーブの質に関する項
    """
    trimed_length = []
    trimed_tc = []
    for arc in curve_object["arcs"]:
        trimed_length.append(arc["trim_length"])
        if arc["is_trimed"]:
            trimed_tc.append(arc["trimed_total_curvature"])
        else:
            trimed_tc.append(arc["total_curvature"])
    return (
        np.exp(-np.abs(
            (
                (tca.BEST_TOTAL_CURVATURE - trimed_tc[0]) /
                (tca.BEST_TOTAL_CURVATURE - tca.UNDER_TOTAL_CURVATURE)
            )
        )) *
        np.exp(-np.abs(
            (
                (tca.BEST_TOTAL_CURVATURE - trimed_tc[1]) /
                (tca.BEST_TOTAL_CURVATURE - tca.UNDER_TOTAL_CURVATURE)
            )
        )) *
        np.exp(-np.abs(
            (
                (trimed_length[0] - trimed_length[1]) /
                (trimed_length[0] + trimed_length[1])
            )
        ))
    )


def calc_curve_score(curve_object):
    """curveが持つ特徴をもとに、そのスコアを計算します

    Args:
        curve_object (dict): curveオブジェクト

    Returns:
        float: そのカーブの評価値
    """
    if not curve_object["is_valid"]:
        return 0.0
    return (
        calc_curve_size_score(curve_object) *
        calc_curve_quality_score(curve_object)
    )


def calc_score(json_data):
    """jsonファイルのオブジェクトからその舞踊のスコアの平均値を計算します

    Args:
        json_data (object): jsonファイルの中身

    Returns:
        float: スコアの平均値
    """
    tc_data = json_data["total_curvature_analysis"]
    scores = []
    weights = []
    sum_length = 0.0
    trimed_length = 0.0
    for curve in tc_data["curves"]:
        sum_length += sum([a["original_length"] for a in curve["arcs"]])
        if curve["is_valid"]:
            scores.append(calc_curve_score(curve))
            trimed_length += sum([a["trim_length"] for a in curve["arcs"]])
    #     weights.append(sum_length)
    # w = np.array(weights) / weights[-1]
    return np.average(np.array(scores)) * trimed_length / sum_length
    return np.average(np.array(scores), weights=w)


def load_scores(input_dir):
    """ディレクトリ名から各データを読み込み，スコアを格納します

    Args:
        input_dir (str): ファイルが格納されたディレクトリ名

    Returns:
        object: 舞踊名と手の名前をキーとしscoreを格納したディクショナリ
    """
    dst = {}
    for d in get_dances():
        dst[d] = {}
        dst[d]["R"] = 0.0
        dst[d]["L"] = 0.0
    name = get_dances_name(input_dir)
    hand = get_hand(input_dir)
    json_data = load(input_dir)
    score = calc_score(json_data)
    dst[name][hand] = score
    return dst


def create_score_matrix(input_dir):
    """スコアを格納した行列を作成します

    Args:
        input_dir (str): ファイルがロードされたディレクトリ名

    Returns:
        matrix: 行列
    """
    data = load_scores(input_dir)
    print(data)
    dst = []
    for d in get_dances():
        dst.append([
            1.0,
            data[d]["R"],
            data[d]["L"]
        ])
    return np.array(dst)


def load_score(filename):
    """ファイルからスコアを読み込みます

    Args:
        filename (str): ファイルパス

    Returns:
        object: ディクショナリ
    """
    dst = {}
    dances = get_dances()
    factor_num = 2
    with open(filename) as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0:
                dst[dances[0]] = float(row[factor_num])
            elif i == 1:
                dst[dances[2]] = float(row[factor_num])
            elif i == 2:
                dst[dances[1]] = float(row[factor_num])
            elif i == 3:
                dst[dances[4]] = float(row[factor_num])
            elif i == 4:
                dst[dances[3]] = float(row[factor_num])
    return dst


def ols(xs, ys):
    """重回帰分析を行います

    Args:
        xs (matrix): 重回帰分析のx
        ys (array): 重回帰分析のy(説明変数)

    Returns:
        object: 重回帰分析の結果
    """
    model = sm.OLS(ys, xs)
    results = model.fit()
    return results


def show_ols_result(result):
    """重回帰分析の結果を表示します。

    現在はただただsummary()をprintしているだけです

    Args:
        result (object): 重回帰分析の結果。これを表示します
    """
    print(result.summary())


def main(input_arg, score_arg, use_score=False):
    """main関数

    Args:
        input_arg (str): 入力ディレクトリ名
        score_arg (str): スコアのファイル名
    """
    if use_score:
        xs = create_score_matrix(input_arg)
    else:
        xs = create_lengthratio_matrix(input_arg)
    scores = load_score(score_arg)
    ys = np.array([scores[d] for d in get_dances()])
    show_ols_result(ols(xs, ys))


if __name__ == '__main__':
    main()
