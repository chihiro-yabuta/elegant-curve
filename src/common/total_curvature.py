import numpy as np
import scipy.integrate as si

class Curvature:
    """ある2次元軌道の曲率を表します

    Attributes:
        function (function): 2次元軌道を返す関数
    """

    def __init__(self, func):
        """初期化

        Args:
            func (function): 軌道を表す関数
        """
        self.function = func

    @property
    def function(self):
        """function: 軌道を表す関数"""
        return self._func

    @function.setter
    def function(self, value):
        self._func = value
        self._d = self._func.diff()
        self._dd = self._func.diff().diff()

    def __call__(self, t):
        d = self._d(t)
        dd = self._dd(t)
        return (d[0] * dd[1] - d[1] * dd[0]) / ((d[0] ** 2 + d[1] ** 2) ** 1.5)

    def value(self, t):
        """関数の値を取得します

        Args:
            t (float): 曲線の媒介変数

        Returns:
            float: 軌道の曲率
        """
        return self(t)

class TotalCurvature:
    """ある関数の全曲率を計算します．

    Attributes:
        function (function): 2次元位置を返す関数
    """
    def __init__(self, func):
        self.function = func

    @property
    def function(self):
        """function: 軌道を表す関数"""
        return self._func

    @function.setter
    def function(self, value):
        self._func = value
        self._d = self._func.diff()
        self._c = Curvature(self._func)

    def _integrand(self, t):
        d = self._d(t)
        return np.abs(self._c(t)) * ((d[0] ** 2 + d[1] ** 2) ** 0.5)

    def __call__(self, from_t, to_t):
        return si.quad(self._integrand, from_t, to_t, limit=100000)[0]

    def value(self, from_t, to_t):
        """関数の値を取得します

        Args:
            t (float): 曲線の媒介変数

        Returns:
            float: 軌道の曲率
        """
        return self(from_t, to_t)
