from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D


@dataclass
class Data2d:
    """2次元データの分析をするためのクラス

    - 2つの量的変数と前提にしている。
    - Data1dを2つ所持する構造は面倒なのでやめた。Data2dにしている次点でヒストグラムとか見る気はないわけで。
    - ヒストグラムを2回みたいなら、Data1dを2つ使いましょうね。
    """

    x: np.ndarray
    y: np.ndarray  # 回帰分析を前提にしているから x2 ではなく y としている
    coef: float = field(init=False)
    intercept: float = field(init=False)

    def __post_init__(self):
        """多少計算時間はかかるけど回帰直線を出すことは多いので、最初から計算しておく"""

        if self.x.shape != self.y.shape:
            raise ValueError(f'xとyの型が不一致です。x={self.x.shape}, y={self.y.shape}')

        ols = sm.OLS(self.y, sm.add_constant(self.x))
        result = ols.fit()
        self.intercept, self.coef = result.params

    def cor(self) -> float:
        return np.corrcoef(self.x, self.y)[0][1]

    def xmin(self) -> float:
        return self.x.min(initial=None)

    def xmax(self) -> float:
        return self.x.max(initial=None)

    def ymin(self) -> float:
        return self.y.min(initial=None)

    def ymax(self) -> float:
        return self.y.max(initial=None)

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(data={'x': self.x, 'y': self.y})

    def to_md(self, x_decimal: int = 2, y_decimal: int = 2, katex: bool = True) -> str:
        # MEMO: markdownの話が入り込むのは少し癪だけど、同居してたら便利なので実装しておく
        df = self.to_df()

        df['x'] = df['x'].round(decimals=x_decimal)
        df['y'] = df['y'].round(decimals=y_decimal)

        if katex:
            df['x'] = df['x'].apply(lambda x: fr'\\({x}\\)')
            df['y'] = df['y'].apply(lambda x: fr'\\({x}\\)')

        return df.to_markdown(index=False)


def plot_scatter(ax: Axes, data: Data2d, **kwargs) -> PathCollection:
    return ax.scatter(data.x, data.y, **kwargs)


def plot_regression_line(ax: Axes, data: Data2d, **kwargs) -> List[Line2D]:
    if kwargs.get('color') is None:
        kwargs['color'] = 'r'

    xs = np.array([data.xmin() - 0.1, data.xmax() + 0.1])
    ys = data.intercept + data.coef * xs
    return ax.plot(xs, ys, **kwargs)
