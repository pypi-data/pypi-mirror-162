# arekore
記述統計のためのクラスや可視化のあれこれ。ダミーデータも作れるよ。

## Quickstart
### 1次元データ

```python
import matplotlib.pyplot as plt
import numpy as np
from arekore import dummy, viz
from arekore.data1d import Data1d, plot_hist


def main():
    # ダミーデータ生成
    rawdata = dummy.dist_normal_1d(mean=50, std=10, n=100)

    # 1次元データオブジェクトの作成
    d = Data1d(rawdata, bins=np.arange(0, 100 + 1, 5))

    # ヒストグラムの描画
    fig, ax = viz.fig_ax(figsize=(8, 6))
    plot_hist(ax, d)
    plt.show()

    # 度数分布表もつくれる
    freq_table_md = d.freq_table_as_md()

    print(freq_table_md)
    """| 階級           |   階級値 |   度数 |   累積度数 |   相対度数 |   累積相対度数 |
|:---------------|---------:|-------:|-----------:|-----------:|---------------:|
| (-0.001, 10.0] |        5 |      0 |          0 |       0    |           0    |
| (10.0, 20.0]   |       15 |      0 |          0 |       0    |           0    |
| (20.0, 30.0]   |       25 |      1 |          1 |       0.01 |           0.01 |
| (30.0, 40.0]   |       35 |     14 |         15 |       0.14 |           0.15 |
| (40.0, 50.0]   |       45 |     30 |         45 |       0.3  |           0.45 |
| (50.0, 60.0]   |       55 |     37 |         82 |       0.37 |           0.82 |
| (60.0, 70.0]   |       65 |     16 |         98 |       0.16 |           0.98 |
| (70.0, 80.0]   |       75 |      2 |        100 |       0.02 |           1    |
| (80.0, 90.0]   |       85 |      0 |        100 |       0    |           1    |
| (90.0, 100.0]  |       95 |      0 |        100 |       0    |           1    |
"""


if __name__ == '__main__':
    main()
```

![data1d_histogram](./examples/data1d_histogram.png)

### 2次元データ

```python
import matplotlib.pyplot as plt

from arekore import dummy, viz
from arekore.data2d import Data2d, plot_regression_line, plot_scatter


def main():
    # ダミーデータ生成
    x, y = dummy.xy_specified_cor(r=0.8, n=50)

    # 2次元データオブジェクトの作成
    d = Data2d(x=x, y=y)

    # 散布図と回帰直線を描画
    fig, ax = viz.fig_ax(figsize=(8, 6))
    plot_scatter(ax, d)
    plot_regression_line(ax, d)

    plt.show()


if __name__ == '__main__':
    main()

```

![data2d_scatter_and_regresson_line](./examples/data2d_scatter_and_regresson_line.png)
