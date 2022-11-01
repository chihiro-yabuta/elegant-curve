import numpy as np
from .base import value, coefficients

class Lspia(object):
    """LSPIA を実装したクラス

    http://www.cad.zju.edu.cn/home/hwlin/pdf_files/
    2014-Progressive-and-iterative-approximation-for-
    least-squares-B-spline-curve-and-surface-fitting.pdf
    この論文をそのまま実装したはずです

    Attributes:
        Q (vector array): 近似したい点
        p (int): Bスプラインの次数
        n (int): 制御点の数-1
        th (float): 近似結果の評価に使う。平均して、一点あたりこれ以下の誤差なら終了
        thstep (float): 更新の収束判定につかう
        nmax (int): nとして許される最大数
        t (array): 曲線のパラメータ
        knots (array): ノットベクトル
        P (vector array): 制御点
        m (vector array): ノットの数
        A (matrix): Bスプライン基底関数を並べたもの
        myu (float): 更新に用いる値
        delta (vector array): 各点での誤差
        delta_norm (array): 各点ごとの誤差の大きさ
        delta_diff (vector array): 各点での誤差の変化

    Args:
        Q (vector array): 近似したい点
        p (int): Bスプラインの次数
        th (float): 近似結果の評価に使う。平均して、一点あたりこれ以下の誤差なら終了
        thstep (float): 更新の収束判定につかう

    Examples:
        Q, p, thなどの必要なパラメータは予め決定しておいてください

        >>> lspia = Lspia(Q, p, th, thstep)
        >>> for p, knot, P, err in lspia.run():
        >>>     print(err)

        errが減っていく様子が見えると思います.

        もしerrorが不要な場合、こんな感じで使って貰えれば...

        >>> lspia = Lspia(Q, p, th, thstep)
        >>> for p, knot, P, err in lspia.run():
        >>>     pass  # 途中経過が不要なのでpassでスキップ
        >>> bsp = BSpline(p, knot, P)

        ここで、bspは近似後の軌道を表します.
    """
    def __init__(self, Q, p, th, thstep):
        """コンストラクタ

        Args:
            Q (vector array): 近似したい点
            p (int): Bスプラインの次数
            th (float): 近似結果の評価に使う。平均して、一点あたりこれ以下の誤差なら終了
            thstep (float): 更新の収束判定につかう
        """
        self.Q = Q
        self.p = p
        self.n = p
        self.th = th
        self.thstep = thstep
        self.nmax = self.Q.shape[0] - 1
        if self.nmax <= p:
            raise ValueError("Invalid p")
        self.t = create_ordered_point_param(self.Q)
        self.knots = create_knot_vector(self.n, self.p, self.t)
        self.P = create_default_P(self.Q, self.n)
        self.m = self.Q.shape[0] - 1
        self.A = create_collocation_matrix(
            self.t,
            self.knots,
            self.m,
            self.n,
            self.p
        )
        self.myu = create_appropriate_weight(self.A)
        self.delta = 0
        self.delta_norm = 0
        self.delta_diff = 0
        self.delta2inf()

    def update(self):
        """近似を更新します

        Returns:
            bool, int, array, vector array, float:
                このまま続けるか?
                現在の次数、ノット、制御点、誤差
        """
        if np.all(np.abs(self.delta_diff) <= self.thstep):
            if self.n >= self.nmax:
                err = np.sum(self.delta_norm)
                return False, self.p, self.knots, self.P, err
            else:
                self.add_ctrls()
        delta = calc_delta(self.Q, self.p, self.knots, self.P, self.t)
        self.delta_diff = delta - self.delta
        self.delta = delta
        self.delta_norm = np.linalg.norm(self.delta, axis=1)
        moves = calc_move(self.myu, self.A, self.delta)
        self.P = self.P + moves
        err = np.sum(self.delta_norm)
        cont = err > self.th
        return cont, self.p, self.knots, self.P, err

    def delta2inf(self):
        """delta系列をinfに飛ばします"""
        self.delta = np.ones(self.Q.shape) * np.inf
        self.delta_norm = np.linalg.norm(self.delta, axis=1)
        self.delta_diff = np.ones(self.P.shape) * np.inf

    def add_ctrls(self):
        """制御点を追加します"""
        self.n, self.knots, self.P = add_ctrls(
            self.p,
            self.knots,
            self.P,
            self.t,
            self.delta_norm
        )
        self.A = create_collocation_matrix(
            self.t,
            self.knots,
            self.m,
            self.n,
            self.p
        )
        self.myu = create_appropriate_weight(self.A)
        self.delta2inf()

    def run(self):
        """updateを繰り返して誤差を縮めます"""
        cont = True
        while cont:
            cont, p, knots, P, err = self.update()
            print(f'\rprogress -> {(err):>0.5f} > {self.th}: {cont}', end='')
            yield p, knots, P, err

    def get_degree(self):
        """次数

        Returns:
            int: 曲線の次数
        """
        return self.p

    def get_knot_vector(self):
        """ノット

        Returns:
            array: 曲線の次数
        """
        return self.knots

    def get_control_points(self):
        """制御点

        Returns:
            vector array: 曲線の次数
        """
        return self.P

    def get_params(self):
        """曲線のパラメータ

        Returns:
            array: 曲線の次数
        """
        return self.t

def calc_delta(Q, p, knots, P, t):
    """現在の軌道と近似される点との誤差を計算します

    Args:
        Q (vector array): 近似すべき点列
        p (int): Bスプラインの次数
        knots (array): ノット
        P (vector array): 制御点
        t (array): 曲線のパラメータ

    Returns:
        vector: delta
    """
    delta = np.zeros(Q.shape)
    for i in range(t.shape[0]):
        delta[i] = Q[i] - value(p, knots, P, t[i])
    return delta

def calc_move(myu, A, delta):
    """制御点の移動量を計算します

    Args:
        myu (float): 移動幅
        A (matrix): 係数行列
        delta (vector array): 移動量

    Returns:
        vector array: 移動量
    """
    n = A.shape[1]
    m = A.shape[0]
    moves = np.zeros((n, delta.shape[1]))
    for i in range(n):
        for j in range(m):
            moves[i] += myu * A[j, i] * delta[j]
    return moves


def create_ordered_point_param(Q):
    """近似すべき点のパラメータを生成します

    Args:
        Q (vector array): 近似すべき点列

    Returns:
        vector: Qに関するパラメータ.
            t[0] = .0,
            t[i] = t[i-1] + distance(Q[i] - Q[i-1]),
            t[len(Q)-1] = 1.0,
            となるように生成されます.
    """
    param = np.zeros(Q.shape[0])
    for i in range(Q.shape[0] - 1):
        param[i+1] = param[i] + np.sqrt(np.sum((Q[i] - Q[i+1]) ** 2))
    return param / param[-1]


def create_knot_vector(n, p, param):
    """ノットベクトルを作成します

    http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
    これをそのまま実装したはずです

    Args:
        n (int): 制御点の数-1
        p (int): Bスプライン関数の次数
        param (array): Bスプラインのパラメータ.無ければ[0,1]を等分するようなノットベクトルが生成されます

    Returns:
        array: paramが設定されていない場合、
            p+1個だけ端を重ね、[0,1]の間を均等分割するようなパラメータを用いたノットベクトル.
            paramが設定されている場合、
            p+1だけ端を重ね、パラメータの平均をとることで作成されるノットベクトル.
            ノットベクトルはu[0],u[1]...u[m]となり、m=n+p+1です.
    """
    result = np.zeros(p + n + 2)  # (p+1) + n-p + (p+1)個
    m = len(param) - 1
    for j in range(1, n - p + 1):
        d = (m + 1) / (n + 1 - p)
        i = int(j * d)
        alpha = j * d - i
        result[j + p] = (1.0 - alpha) * param[i - 1] + alpha * param[i]
        # result[j + p] = np.sum(param[j:j+p]) / p
    result[n + 1:] = np.ones(p + 1)
    return result

def create_default_P(Q, n):
    """制御点Pを作成するための初期値の計算を行います

    以下の数式に従い、最も近い添え字のQにPを配置していきます
    P[i] = Q[np.round(m/n*i)]
    ここで、mはQの数-1です。Q[0],Q[1],...Q[m]であるような状態を想定しています

    Args:
        Q (vector array): 近似されるべき点
        n (int): 制御点の数-1

    Returns:
        array: もっとも近い制御点の初期値
    """
    m = Q.shape[0] - 1
    result = np.zeros((n + 1, Q.shape[1]))
    for i in range(n):
        result[i] = Q[int(np.round(m / n * i))]
    return result

def create_collocation_matrix(t, knots, m, n, p):
    """Bスプライン基底関数を用いて行列を作成します

    Args:
        t (array): Bスプラインのパラメータ
        knots (array): Bスプライン曲線のノットベクトル
        m (int): 近似されるべき点の数-1.
            点はQ[0],Q[1]...Q[m]となります
        n (int): 制御点の数-1
        p (int): Bスプライン関数の次数
    """
    result = np.zeros((t.shape[0], n + 1))
    for i in range(t.shape[0]):
        result[i] = coefficients(n, p, knots, t[i])
    return result

def create_appropriate_weight(A):
    """Collocation matrixから、解に近づけていくための係数である\myuを計算します

    Args:
        A (matrix): Collocation matrix

    Returns:
        float: 解に近づくための係数 :math:`\\mu`
    """
    n = A.shape[1]
    t = np.dot(A.T, A)
    a = np.zeros(n)
    for i in range(n):
        a[i] = np.sum(t[i])
    return 2.0 / np.max(a)

def add_ctrls(p, knots, P, t, err):
    t_j, t_bar = calcurate_inserted_knot(t, knots, err)
    knots, P = insert_knot(knots, t_bar, t_j, p, P)
    n = P.shape[0] - 1
    return n, knots, P

def calculate_knot_interval_error(t, knot, error):
    """現在の誤差の計算結果から、各ノット間におけるエラーを計算します

    Args:
        t (array): Bスプライン曲線のパラメータ
        knot (array): ノットベクトル
        error (array): 現在の近似元点と近似結果との差(差のノルムの配列)

    Returns:
        array: ノット間ごとの誤差, ノット間に格納された曲線のパラメータのテーブル.
    """
    ts = np.array([
        [
            i for i, te in enumerate(t) if k1 <= te <= k2
        ] for k1, k2 in zip(knot, knot[1:])
    ])
    return np.array([np.sum(error[te]) for te in ts]), ts

def calcurate_inserted_knot(t, knots, delta_norm):
    """誤差量と曲線のパラメータ、ノットベクトルから、
    ノットが挿入されるべき位置およびその値を計算します

    Args:
        t (array): Bスプライン曲線のパラメータ
        knots (array): ノッベクトル
        delta_norm (array): 元の点と現在の点の誤差を並べたもの
            フィッティング誤差

    Returns:
        float, float: (t_j, t_bar).
            t_jはノットの挿入位置.
            t_barはノットの値.
    """
    d, ts = calculate_knot_interval_error(t, knots, delta_norm)
    t_j = None
    t_bar = None
    j = np.argmax(d)
    if len(ts[j]) == 2:
        t_j = j
        t_bar = (t[j] + t[j + 1]) / 2.0
    elif len(ts[j]) > 2:
        d_max = d[j]
        for t_i in ts[j]:
            begin_indices = np.arange(ts[j][0], t_i + 1, 1)
            end_indices = np.arange(t_i, ts[j][-1] + 1, 1)
            if ((np.sum(delta_norm[begin_indices]) >= d_max / 2.0) and
                    (np.sum(delta_norm[end_indices]) >= d_max / 2.0)):
                t_j = j
                t_bar = (t[t_i] + t[t_i + 1]) / 2.0
                break
    return t_j, t_bar

def insert_knot(knots, t, k, p, P):
    """曲線の形状を変更しないように、ノットベクトルにノットを挿入します

    Osloアルゴリズムを実装したものです。

    Args:
        knots (array): knot vector
        t (float): inserted knot value
        k (int): inserted knot index
            ノットtはknots[k]とknots[k+1]の間に挿入されます
        p (int): Bスプライン曲線の次数
        P (vector array): 制御点

    Returns:
        array, vector array: knots, P
            knotsはtが挿入されたノットベクトル.
            Pは形状が変更されないように調整された制御点.
    """
    result_P = []
    for i in range(len(P) + 1):
        if i <= k - p:
            result_P.append(P[i])
        elif k - p + 1 <= i <= k:
            ai = (t - knots[i]) / (knots[i+p] - knots[i])
            result_P.append(
                (1.0 - ai) * P[i - 1] + ai * P[i]
            )
        elif k + 1 <= i:
            result_P.append(P[i-1])
    return np.insert(knots, k + 1, t), np.array(result_P)
