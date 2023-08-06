from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def fig_ax(figsize: Tuple[int, int] = (4, 3)) -> Tuple[Figure, Axes]:
    return plt.subplots(nrows=1, ncols=1, figsize=figsize)


def fig_axes(nrows: int, ncols: int, figsize: Tuple[int, int] = (4, 3)) -> Tuple[Figure, List[Axes]]:
    assert nrows >= 2 or ncols >= 2, '複数グラフ専用APIだよ'

    return plt.subplots(nrows, ncols, figsize=figsize)
