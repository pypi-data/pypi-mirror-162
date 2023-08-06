import math
from typing import Tuple

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import scale


def dist_normal_1d(mean: float, std: float, n: int) -> np.ndarray:
    return np.random.normal(loc=mean, scale=std, size=n)


def dist_bimodal_1d(m1: float, s1: float, n1: int, m2: float, s2: float, n2: int):
    """二峰性の分布"""
    d1 = dist_normal_1d(mean=m1, std=s1, n=n1)
    d2 = dist_normal_1d(mean=m2, std=s2, n=n2)
    return np.concatenate((d1, d2))


def dist_uniform_1d(a: float, b: float, n: int) -> np.ndarray:
    return np.random.uniform(low=a, high=b, size=n)


def xy_specified_cor(r: float, n: int) -> Tuple[np.ndarray, np.ndarray]:
    """相関係数が r となる (x,y) の組を生成する

    ## 参考: correlation - Tool for generating correlated data sets - Cross Validated
    https://stats.stackexchange.com/questions/111865/tool-for-generating-correlated-data-sets
    """
    y_dummy = np.random.normal(size=n).reshape(-1, 1)
    x = np.random.normal(size=n).reshape(-1, 1)

    lr = LinearRegression()
    lr.fit(X=x, y=y_dummy)
    residuals = y_dummy - lr.predict(x)

    y = scale(x) * r + scale(residuals) * math.sqrt(1 - r ** 2)

    x = x.reshape(-1, )
    y = y.reshape(-1, )

    r_actual = np.corrcoef(x, y)[0][1]
    assert abs(r_actual - r) < 1e-5, f'got={r_actual}, want={r}'

    return x, y
