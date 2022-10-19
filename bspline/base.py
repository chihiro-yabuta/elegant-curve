# -*- coding: utf-8 -*-
"""Define the base of b-spline curve.

B-spline関数に関する基本的な計算をまるっとまとめたモジュール.
B-spline関数が必要とするパラメータが決定されているとき、
それを用いた計算を一気にしてくれ、関数として表現してくれるようになります.
B-spline関数の詳細な説明は省略しますが、
http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/
このページが参考になるかと思います.

簡単に説明すると、B-splineカーブは次式で表現されます.

.. math::

    \\vec{C}(t) = \\sum_{i=0}^{n}B_{i, p}(t)\\vec{P}_i

ここで、

* :math:`t` は曲線の媒介変数.
* :math:`B_{i,p}` はp次のB-spline基底関数.
* :math:`\\vec{P_i}` は制御点

です.
:math:`B_{i,p}` は内部にノットと呼ばれるパラメータを持ち、本来再帰的に計算されます.
が、一般的にはde Boorのアルゴリズムが用いられるようです.
詳細は、
http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-coef.html
このページが詳しいです.
"""
import numpy as np
from numba import jit, f8, i4

bspline_spec = [
    ("h", i4),
    ("knots", f8[:]),
    ("ctrls", f8[:, :])
]

class BSpline(object):
    """BSpline curve class.

    B-spline関数の基本的な計算をまるっと行ってくれる関数.
    関数を定義するのに必要なパラメータを内部に格納し、
    それを基に計算を行ってくれます.

    Attributes:
        h (int): degree of b spline
        knots (array): knot vector
        ctrls (vector array): control points array

    Examples:
        このクラスを使う場合、
        B-spline関数のパラメータを予め設定し、
        クラス作成時の引数として設定する必要があります.
        インスタンスはあたかも関数であるかのように呼び出しを行うことができます.

        >>> # set parameters some value
        >>> bsp = BSpline(h, knots, ctrls)
        >>> bsp(0.5)  # call this fuction
        [0.4, 0.2, 0.5]  # position at u=0.5
    """
    def __init__(self, h, knots, ctrls):
        """__init__ function

        Args:
            h (int): degree of b spline
            knots (array): knot vector
            ctrls (vector array): control points array
            param (array): parameter of b-spine
        """
        self.h = h
        self.knots = knots
        self.ctrls = ctrls

    def __call__(self, u):
        """__call__ function.

        This method wrap bspline.base.value function.

        Args:
            u (float): this function return C(u)

        Returns:
            array: 3-D positon
        """
        return value(self.h, self.knots, self.ctrls, u)

    def value(self, u):
        """calcurate b-spline curve postion

        b-spline関数の、ある媒介変数のときの値を返します.
        関数的に呼び出しをするのが嫌いなあなたにプレゼント.

        Args:
            u (float): 媒介変数

        Returns:
            array: 3-D position
        """
        return self.__call__(u)

    def diff(self):
        """Create derivative function.

        B-spline関数を微分した関数を返します.
        B-spline関数の微分もまたB-spline関数であるため、
        BSpline型で返ります.

        詳細については、Derivatives of a B-spline Curve
        (http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-derv.html)
        を参考にしてください。

        Returns:
            BSpline: new b-spline function
        """
        diff_ctrls = np.zeros((self.ctrls.shape[0] - 1, self.ctrls.shape[1]))
        for i in range(len(self.ctrls) - 1):
            diff_ctrls[i] = (
                float(self.h) /
                (self.knots[i+self.h+1] - self.knots[i+1]) *
                (self.ctrls[i+1] - self.ctrls[i])
            )
        diff_knots = self.knots[1:-1]
        diff_h = self.h - 1
        return BSpline(
            diff_h,
            diff_knots,
            diff_ctrls
        )

    def __str__(self):
        """__str__ function
        """
        return "Degree:\n{0}\nKnot vector:\n{1}\nCtrls:\n{2}\n".format(
            self.h,
            self.knots,
            self.ctrls
        )


@jit(i4(f8[:], f8), nopython=True)
def find_knots_index(knots, u):
    """ノットベクトルにおけるuの位置を探索します

    Args:
        knots (array): ノットベクトル
        u (float): 曲線の進行度

    Returns:
        int: Index of u in knot vector
    """
    for i in range(knots.shape[0] - 1):
        if knots[i] <= u < knots[i+1]:
            return i
    return -1


@jit(f8[:](i4, i4, f8[:], f8), nopython=True, cache=True)
def coefficients(n, p, knots, u):
    """Bスプライン係数を計算します。

    B-spline Curves Computing the Coefficients
    http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-coef.html
    を実装しただけです

    Args:
        n (int): 係数の数+1.係数と掛け合わされるべき制御点の数+1
        p (int): スプライン関数の次数
        knots (array): ノット列
        u (float): 曲線の進行度

    Returns:
        array: 各制御点への重み
    """
    m = knots.shape[0] - 1.0
    N = np.zeros(n + 1)
    if u == knots[0]:
        N[0] = 1.0
        return N
    elif u == knots[-1]:
        N[-1] = 1.0
        return N
    k = find_knots_index(knots, u)
    if k == -1:
        return N
    N[k] = 1.0
    for d in range(1, p+1):
        N[k-d] = (knots[k+1] - u) / (knots[k+1] - knots[k-d+1]) * N[k-d+1]
        for i in range(k-d+1, k):
            N[i] = (
                (u - knots[i]) / (knots[i+d] - knots[i]) * N[i] +
                (knots[i+d+1] - u)/(knots[i+d+1] - knots[i+1]) * N[i+1]
            )
        N[k] = (u - knots[k]) / (knots[k+d] - knots[k]) * N[k]
    return N



value_locals = dict(coef=f8[:], result=f8[:])


@jit(f8[:](i4, f8[:], f8[:, :], f8), nopython=True, locals=value_locals)
def value(p, knots, ctrls, u):
    """Bスプライン曲線の位置を計算します

    Args:
        p (int): 曲線の次数
        knots (array): ノットベクトル
        ctrls (vector array): 制御点
        u (float): 曲線の進行度

    Returns:
        array: 曲線の位置
    """
    coef = coefficients(ctrls.shape[0] - 1, p, knots, u)
    result = np.zeros(ctrls.shape[1])
    for i in range(ctrls.shape[0]):
        result += coef[i] * ctrls[i]
    return result
