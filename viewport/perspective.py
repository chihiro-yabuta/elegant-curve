""" 透視投影変換行列を計算します.

TODO:
    色々なバグが潜在的に残ってる可能性があるので、
    きちんと検証しましょう.
"""
import numpy as np


class Homogeneous:
    """3次元で座標を返す関数の結果を同次座標系で返すように変換します．

    やることは最後の要素に1を追加するだけ.

    Examples:
        適当に関数を設定した前提で

        >>> h = Homogeneous(func)
        >>> print(func(0.0))
        [1., 2., 3.]
        >>> print(h(0.0))
        [1., 2., 3., 1.]

    TODO:
        同次座標系位置の微分ってほんとにVectorでいいの?
        僕知らないよ

    Warning:
        同時座標系の微分は適当に計算してはいけませんでした.
        きちんと計算しましょう.
    """

    def __init__(self, func):
        """初期化

        Args:
            func (function): 3次元位置を返す関数
        """
        self._func = func

    def __call__(self, t):
        """関数の値を返します

        Args:
            t (float): 媒介変数

        Returns:
            vector: 同次座標系で表された位置
        """
        return np.r_[self._func.__call__(t), np.array([1.0])]

    def value(self, t):
        """関数の値を返します

        Args:
            t (float): 媒介変数

        Returns:
            vector: 同次座標系で表された位置
        """
        return self.__call__(t)

    def diff(self):
        """微分した関数を返します

        Returns:
            HomogeneousVector: 微分した関数
        """
        return HomogeneousVector(self._func.diff())


class HomogeneousVector:
    """3次元ベクトルを同次座標系中におけるベクトルへと変換するクラス

    やることは最後に0を追加するだけ.

    Examples:
        適当に関数を設定した前提で

        >>> h = HomogeneousVector(func)
        >>> print(func(0.0))
        [1., 2., 3.]
        >>> print(h(0.0))
        [1., 2., 3., 0.]
    """

    def __init__(self, func):
        """初期化

        Args:
            func (function): 3次元ベクトルを返す関数
        """
        self._func = func

    def __call__(self, t):
        """関数の値を返します

        Args:
            t (float): 媒介変数

        Returns:
            vector: 同次座標系空間中でのベクトル
        """
        return np.r_[self._func.__call__(t), np.array([0.0])]

    def value(self, t):
        """関数の値を返します

        Args:
            t (float): 媒介変数

        Returns:
            vector: 同次座標系空間中でのベクトル
        """
        return self.__call__(t)

    def diff(self):
        """微分した値を返します.

        Warning:
            同時座標系のベクトルの微分って、ベクトルであってる?

        Returns:
            HomogeneousVector: 微分した関数
        """
        return HomogeneousVector(self._func)


class Dehomogeneous:
    """同次座標系で表された関数を3次元位置に戻します.

    同時座標系データの最後の要素が0ならそれはベクトルであると判断し、
    最後の要素を引き剥がして返します.
    もし0でないならば、
    全体をその数で割って返します.

    Examples:
        同時座標系のベクトルを変換する場合

        >>> v = Dehomogeneous(v_func)  # v_funcは同時座標系のベクトルを返す関数
        >>> print(v_func(0.0))
        [1., 5., 7., 0]
        >>> print(v(0.0))
        [1., 5., 7., 0]

        同時座標系の位置を変換する場合

        >>> p = Dehomogeneous(p_func)  # p_funcは同時座標系の位置を返す関数
        >>> print(p_func)
        [1., 5., 7., 2.]
        >>> print(p(0.0))
        [0.5, 2.5, 3.5]
    """

    def __init__(self, func):
        """初期化

        Args:
            func (function): 同次座標系を返す関数
        """
        self._func = func

    def __call__(self, t):
        """関数の値を返します

        Args:
            t (float): 媒介変数

        Returns:
            vector: 3次元で表された位置
        """
        pos = self._func.__call__(t)
        if pos[3] != 0.0:
            return pos[0:3] / pos[3]
        else:
            return pos[0:3]

    def value(self, t):
        """関数の値を返します

        Args:
            t (float): 媒介変数

        Returns:
            vector: 3次元で表された位置
        """
        return self.__call__(t)

    def diff(self):
        """微分した関数を返します

        Returns:
            Dehomogeneous: 微分した関数を再度変換したもの
        """
        return Dehomogeneous(self._func.diff())


def perspective(angle, aspect, near, far):
    """透視投影変換行列を計算します

    Args:
        angle (float): 縦方向の視野角(degree)
        aspect (float): 視界のアスペクト比
        near (float): 近い面までの距離
        far (float): 遠い面までの距離

    Returns:
        matrix: 透視投影行列
    """
    radians = np.deg2rad(angle / 2.0)
    sine = np.sin(radians)
    cotan = np.cos(radians) / sine
    clip = far - near
    return np.array([
        [cotan / aspect, 0., 0., 0.],
        [0., cotan, 0., 0.],
        [0., 0., -(near + far) / clip, -(2.0 * near * far) / clip],
        [0., 0., -1, 0.]
    ])


def _normalzie(v):
    return v / np.linalg.norm(v)


def _translate(mat, vec):
    dst = mat
    dst[:, 3] += np.dot(mat[:, 0:3], vec)
    return dst


def look_at(eye, center, viewup):
    """ある点からある点をみるview行列を計算します

    Args:
        eye (vector): 視点の位置
        center (vector): 視点が見る位置
        viewup (vector): 視点の上方向

    Returns:
        matrix: view行列
    """
    forward = center - eye
    forward = _normalzie(forward)
    up = viewup
    side = np.cross(forward, up)
    side = _normalzie(side)
    up = np.cross(side, forward)
    up = _normalzie(up)
    m = np.eye(4)
    m[0, 0:3] = side
    m[1, 0:3] = up
    m[2, 0:3] = -forward
    m = _translate(m, -eye)
    return m
