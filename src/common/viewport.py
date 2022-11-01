""" 観客の視点方向を考慮する場合の手法を提供します
"""
import numpy as np
import re

def get_plane_matrix(plane_str):
    """視点平面を表す文字列から，平面を表す行列を計算します

    Args:
        plane_str (string): 視点平面を表す文字列

    Returns:
        matrix: 視点平面を表す行列

    'xy'とか'-zy'とかから行列を作る

    >>> print(get_plane_matrix('xy'))
    [[ 1.  0.  0.]
     [ 0.  1.  0.]]
    >>> print(get_plane_matrix('-zy'))
    [[-0. -0. -1.]
     [ 0.  1.  0.]]
    """
    axis = re.findall("-?[xyz]", plane_str)
    vectors = []
    for a in axis:
        vectors.append(get_axis_vector(a))
    return np.array(vectors)

def get_axis_vector(axis_str):
    """軸を表す文字列から，軸を表すベクトルを返します

    Args:
        axis_str (string): 軸を表す文字列

    Returns:
        array: 軸を表すベクトル

    Raises:
        ValueError: axis_strが軸を表す文字列でなかった場合に発生

    'x'とか'-z'とかからベクトルを作る
    >>> print(get_axis_vector('x'))
    [ 1.  0.  0.]
    >>> print(get_axis_vector('-z'))
    [-0. -0. -1.]
    """
    dst = None
    if "x" in axis_str:
        dst = np.array([1.0, 0.0, 0.0])
    elif "y" in axis_str:
        dst = np.array([0.0, 1.0, 0.0])
    elif "z" in axis_str:
        dst = np.array([0.0, 0.0, 1.0])
    else:
        raise ValueError("axis_str is invalid: " + str(axis_str))
    if "-" in axis_str:
        dst = -1.0 * dst
    return dst
