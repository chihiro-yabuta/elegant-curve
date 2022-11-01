"""軌道を拡大・縮小する手法を提供します"""
import numpy as np


def scale_matrix(x=1.0, y=1.0, z=1.0):
    """拡大・縮小する行列を返します

    Args:
        x (float): x方向への拡大倍率
        y (float): y方向への拡大倍率
        z (float): z方向への拡大倍率

    Returns:
        matrix: 拡大行列
    """
    return np.array([
        [x, 0.0, 0.0],
        [0.0, y, 0.0],
        [0.0, 0.0, z]
    ])
