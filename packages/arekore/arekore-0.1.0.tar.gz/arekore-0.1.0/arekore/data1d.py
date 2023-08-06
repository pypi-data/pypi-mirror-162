from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.container import BarContainer


@dataclass(frozen=True)
class Data1d:
    """1次元データの分析をするためのクラス。

    1次元データの統計量に興味があるわけだから階級も必須にしている。
    """
    rawdata: np.ndarray
    bins: np.ndarray

    def __post_init__(self):
        # MEMO: ndarrayのshapeがおかしいとどうせ後でエラーでるので厳密なガードにはしていない
        if len(self.rawdata.shape) != 1 or self.rawdata.shape[0] < 1:
            raise ValueError(f'only 1d ndarray, got={self.rawdata.shape}')

    def std(self) -> float:
        return self.rawdata.std(ddof=0)

    def min(self) -> float:
        return self.rawdata.min(initial=None)

    def max(self) -> float:
        return self.rawdata.max(initial=None)

    def mean(self):
        return np.mean(self.rawdata)

    def median(self) -> float:
        return np.quantile(self.rawdata, q=0.5)

    def mode(self) -> np.ndarray:
        """複数ある場合には複数返す。"""
        return pd.Series(self.rawdata).mode().to_numpy()

    def mode_with_bins(self, target_bins: np.ndarray = None) -> np.ndarray:
        """階級を指定した最頻値を返す。複数の場合もある。"""
        if target_bins is None:
            target_bins = self.bins

        freq, _ = np.histogram(self.rawdata, bins=target_bins)

        mode_indexes = np.where(freq == np.max(freq))

        階級値 = (target_bins[:-1] + target_bins[1:]) / 2

        return 階級値[mode_indexes]

    def freq_table(self) -> pd.DataFrame:
        s = pd.Series(self.rawdata)
        freq = s.value_counts(bins=self.bins, sort=False)

        階級 = freq.index
        階級値 = (self.bins[:-1] + self.bins[1:]) / 2
        度数 = freq.to_numpy()
        累積度数 = freq.cumsum()
        相対度数 = freq / s.count()
        累積相対度数 = (freq / s.count()).cumsum()

        return pd.DataFrame({'階級': 階級,
                             '階級値': 階級値,
                             '度数': 度数,
                             '累積度数': 累積度数,
                             '相対度数': 相対度数,
                             '累積相対度数': 累積相対度数,
                             }).reset_index(drop=True)

    def freq_table_as_md(self, katex_mode: bool = False) -> str:
        # MEMO: markdownの話が入り込むのは少し癪だけど、同居してたら便利なので実装しておく
        freq_table = self.freq_table()

        # float型の場合は小数点を揃える
        freq_table['階級値'] = freq_table['階級値'].apply(lambda x: f'{x:.2f}')
        freq_table['相対度数'] = freq_table['相対度数'].apply(lambda x: f'{x:.2f}')
        freq_table['累積相対度数'] = freq_table['累積相対度数'].apply(lambda x: f'{x:.2f}')

        if katex_mode:
            for col in freq_table.columns:
                freq_table[col] = freq_table[col].apply(lambda x: fr'\\({x}\\)')

        return freq_table.to_markdown(index=False)

    def iqr(self, hinge: bool = False) -> float:
        return self.q3(hinge) - self.q1(hinge)

    def q1(self, hinge: bool = False) -> float:
        if hinge:
            under_median = self.rawdata[np.where(self.rawdata < self.median())]
            return np.quantile(under_median, q=0.5)
        else:
            return np.quantile(self.rawdata, q=0.25)

    def q3(self, hinge: bool = False) -> float:
        if hinge:
            over_median = self.rawdata[np.where(self.rawdata > self.median())]
            return np.quantile(over_median, q=0.5)
        else:
            return np.quantile(self.rawdata, q=0.75)


def plot_hist(ax: Axes, data: Data1d, **kwargs) -> Tuple[np.ndarray, np.ndarray, BarContainer]:
    if kwargs.get('ec') is None:
        kwargs['ec'] = 'black'

    return ax.hist(data.rawdata, bins=data.bins, **kwargs)
