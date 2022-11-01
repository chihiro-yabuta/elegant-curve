""" 観客の視点方向を表す行列を任意の方向に回転させる手法を提供します
"""
import numpy as np


def rotate(mat, rad, axis="x", is_degree=False):
    """観客の視点方向を基準として，正射影の投影面を回転させます

    正射影によって投影されているものと仮定します．
    その場合，投影面を回転させたい需要に見舞われたとします。
    その場合にこの関数を使って投影面を回転させます

    Args:
        mat (matrix): 投影面に投影するための行列
            形としては，[e_x, e_y, e_z].Tみたいなイメージ
        rad (float): 角度を表す数。通常ラジアンを想定しています。
            もしdegを使いたければis_degreeフラグをTrueにしてください
        axis (str): 軸を表す文字列。"x", "y", "z"をサポートしています
        is_degree (bool): radプロパティがデグリーであるかを表す数

    Returns:
        matrix: 観客の視点方向を基準とした回転行列
    """
    if is_degree:
        rad = np.radians(rad)
    rot = rotate_matrix(rad, axis)
    return np.dot(mat, rot)


def rotate_matrix(rad, axis):
    """観客の視点方向を基準として，正射影の投影面を回転させた行列を計算します

    正射影によって投影されているものと仮定します．
    その場合，投影面を回転させたい需要に見舞われたとします。
    その場合にこの関数を使って行列を入手してください
    この関数は投影面を基準として回転変換を行う場合の行列を計算します

    Args:
        rad (float): 角度[rad]

    Returns:
        matrix: 観客の視点方向を基準とした回転行列

    Raises:
        ValueError: If axis name is invalid
    """
    if axis == "x":
        return rotateX(rad)
    elif axis == "y":
        return rotateY(rad)
    elif axis == "z":
        return rotateZ(rad)
    else:
        raise ValueError("axis ``{}'' is invalid axis name".format(axis))


def rotateX(rad):
    """投影面をX軸を中心に回転させる行列を返します.

    Args:
        rad(float): 回転角度[rad]

    Returns:
        matrix: 回転行列
    """
    return np.array([
        [1, 0, 0],
        [0, np.cos(rad), np.sin(rad)],
        [0, -np.sin(rad), np.cos(rad)]
    ])


def rotateY(rad):
    """投影面をY軸を中心に回転させる行列を返します.

    Args:
        rad(float): 回転角度[rad]

    Returns:
        matrix: 回転行列
    """
    return np.array([
        [np.cos(rad), 0, -np.sin(rad)],
        [0, 1, 0],
        [np.sin(rad), 0, np.cos(rad)]
    ])


def rotateZ(rad):
    """投影面をZ軸を中心に回転させる行列を返します.

    Args:
        rad(float): 回転角度[rad]

    Returns:
        matrix: 回転行列
    """
    return np.array([
        [np.cos(rad), np.sin(rad), 0],
        [-np.sin(rad), np.cos(rad), 0],
        [0, 0, 1]
    ])
