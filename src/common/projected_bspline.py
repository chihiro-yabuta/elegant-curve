"""何らかの平面に投影した軌道を計算するモジュール

現在は面に投影されたBスプライン関数しか実装してない.

Note:
    :py:mod:`viewport_bspline`
    と完全にかぶってる.完全に自分のミス.
"""
import numpy as np

class ProjectedBSpline:
    """ 面に投影されたBSpline軌道を表す

    関数であるかのように扱うことができます.
    そのため、()を使ってある媒介変数の時の軌道位置を取得することができます.

    投影前の軌道は、3次元位置を返す関数を想定しています.
    が、実際には投影を表す行列(axis)と関数の戻り値の内積を計算しているため、
    使用者が次元をきちんと合わせていれば特に問題は無いと思います.

    Warning:
        微分値を計算したりその他の都合を考慮すると、
        正射影以外の投影を必要とするならこのクラスを使わないほうが良いかと.

    Attributes:
        bsp(function): BSpline軌道
        axis(matrix): 投影面を表す行列

    Args:
        bsp(function): BSpline Trajectory
        axis(matrix): 投影面を表す行列

    Examples:
        予め投影する軌道が決定されている必要があります.

        >>> axis = numpy.array([
            [0., 1., 0.],
            [0., 0., 1.],
            [1., 0., 0.]
        ])
        >>> pbsp = ProjectedBSpline(bsp, axis)  # bspは投影される軌道.
        >>> print(pbsp(0.5))
        [123., 456., 789.]  # 座標位置は適当なので深く考えないでください.

    Attributes:
        bsp(function): BSpline軌道
        axis(matrix): 投影面を表す行列

    Args:
        bsp(function): BSpline Trajectory
        axis(matrix): 投影面を表す行列
    """

    def __init__(self, bsp, axis):
        """Init ProjectedBSpline with bsp, axis.
        """
        self.bsp = bsp
        self.axis = axis

    def __call__(self, t):
        """Call projected trajectory.
        tがpbsp関数に入れる引数？

        Args:
            t(float): parameter of funtion
        """
        return np.dot(self.axis, self.bsp.value(t))

    def diff(self):
        """Get diff function.

        元の関数が微分可能である必要があります.
        ぶっちゃけるとdiff関数を実装している必要があります.
        それ以上のことは特になにも考えていません.
        微分した関数は次式によって計算されます.

        .. math::

            \\frac{d}{dt}(A \\cdot \\vec{C}(t)) =
            A \\cdot \\frac{d}{dt}\\vec{C}(t)

        そのため、投影する面が時間的に変動する場合( :math:`A` が時間的に変動する場合)、
        微分は不正確なものとなります.
        """
        return ProjectedBSpline(
            self.bsp.diff(),
            self.axis
        )

class Curvature:
    """投影面上の軌道が有する曲率を表す関数オブジェクト.

    Warning:
        2次元軌道の符号付き曲率にしか対応していません.

    Attributes:
        bsp(function): BSpline軌道
        d(function): bspの微分
        dd(function): bspの二階微分
    """

    def __init__(self, bsp):
        """Init function.
        Args:
            bsp(ProjectedBSpline): 軌道
        """
        self.bsp = bsp
        self.d = bsp.diff()
        self.dd = bsp.diff().diff()

    def __call__(self, t):
        """Call function.
        Args:
            t(float): 媒介変数
        """
        dif = self.d(t)
        ddiff = self.dd(t)
        return ((dif[0] * ddiff[1] - dif[1] * ddiff[0]) /
                (dif[0] ** 2 + dif[1] ** 2) ** 1.5)
