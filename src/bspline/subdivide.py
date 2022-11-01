"""Bスプライン関数を分割する手法を提供します．

実際これでいいのかという説はあるものの、とりあえず動いてるからいいや.

B-spline関数は、
媒介変数の範囲やその他のパラメータ群を工夫することで、
２つのB-spline関数として表現することが可能です.
それらのアルゴリズムを提供します.
"""
import numpy as np
from .base import BSpline

def subdivide(bspline, t):
    """軌道の関数を指定された位置で分割します.

    あるB-spline関数 :math:`\\vec{C}(t) (0 \\leq t \\leq 1)` があったとき、
    それを :math:`t_1` で分割すると、
    :math:`\\vec{C}_1(t)(0 \\leq t \\leq t_1)` ,
    :math:`\\vec{C}_2(t)(t_1 \\leq t \\leq 1)`
    にすることができます.
    この関数は、まさしくそれを行います.

    Args:
        bspline (BSpline): BSpline軌道を表すオブジェクト
        t (float): bspline(t)の位置で軌道を分割します

    Returns:
        BSpline, Bspline: 分割された２つの軌道
    """
    k = calc_divide_index(bspline.knots, t)
    divided_ctrlss = subdivide_ctrl_points(bspline, t, k)
    divided_knots = subdivide_knot(bspline, t, k)
    return (
        BSpline(bspline.h, divided_knots[0], divided_ctrlss[0]),
        BSpline(bspline.h, divided_knots[1], divided_ctrlss[1])
    )

def subdivide_knot(bspline, t, k=None):
    """指定された位置で軌道を分割した場合におけるノットを計算.

    Args:
        knot (array): ノットベクトル
        t (float): 挿入位置の媒介変数
        k (int): 挿入位置を表すindex.
            Noneなら計算します．

    Returns:
        array, array: 分割されたそれぞれのノットベクトル
    """
    if k is None:
        k = calc_divide_index(bspline.knots, t)
    edge = np.ones(bspline.h + 1) * t
    return (
        np.hstack((bspline.knots[:k+1], edge)),
        np.hstack((edge, bspline.knots[k+1:]))
    )

def subdivide_ctrl_points(bspline, t, k=None):
    """軌道を指定位置において分割した場合における制御点を計算.

    Args:
        bspline (BSpline): 軌道を表す関数
        t (float): 挿入位置の媒介変数
        k (int): 挿入位置をあらわすindex.
            もしNoneであれば計算します．

    Returns:
        vector array, vector array: 分割されたそれぞれの制御点
    """
    if k is None:
        k = calc_divide_index(bspline.knots, t)
    P = bspline.ctrls
    p = bspline.h
    s = 0
    net = create_deboor_net(bspline, t, k)
    Ps = ([], [])
    for i in range(k - p + 1):
        Ps[0].append(P[i])
    for i in range(1, p - s + 1):
        Ps[0].append(net[i][k - p + i])
    for i in range(p - s, 0, -1):
        Ps[1].append(net[i][k - s])
    for i in range(k - s, len(P)):
        Ps[1].append(P[i])
    return np.array(Ps[0]), np.array(Ps[1])

def create_deboor_net(bspline, t, k):
    """deBoorのアルゴリズムで表される、netを計算します.

    Args:
        bspline (BSpline): 軌道を表す関数
        t (float): 挿入位置の媒介変数
        k (int): 挿入位置をあらわすindex

    Returns:
        dict: ネットを表すPの二次元dictionary
    """
    p = bspline.h
    h = bspline.h
    u = bspline.knots
    P = bspline.ctrls
    s = 0
    Ps = {0: {}}
    for i in range(k - p, k - s + 1):
        Ps[0][i] = P[i]
    a = {}
    for r in range(1, h + 1):
        a[r] = {}
        Ps[r] = {}
        for i in range(k - p + r, k - s + 1):
            a[r][i] = (t - u[i]) / (u[i + p - r + 1] - u[i])
            Ps[r][i] = ((1.0 - a[r][i]) * Ps[r - 1][i - 1] +
                        a[r][i] * Ps[r - 1][i])
    return Ps

def calc_divide_index(knots, t):
    """軌道分割における，どの部分にノットを差し込むかを表すindexを計算します.

    Args:
        knots (float array): ノットベクトル
        t (float): 分割位置を表す媒介変数

    Returns:
        int: 挿入位置のindex
    """
    for i in range(knots.shape[0] - 1):
        if knots[i] <= t < knots[i + 1]:
            return i
    return -1
