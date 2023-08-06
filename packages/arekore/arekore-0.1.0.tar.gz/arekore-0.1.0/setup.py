# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arekore']

package_data = \
{'': ['*']}

install_requires = \
['japanize-matplotlib>=1.1.3,<2.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'scikit-learn>=1.1.2,<2.0.0',
 'scipy>=1.9.0,<2.0.0',
 'statsmodels>=0.13.2,<0.14.0',
 'tabulate>=0.8.10,<0.9.0']

setup_kwargs = {
    'name': 'arekore',
    'version': '0.1.0',
    'description': '記述統計のためのクラスや可視化のあれこれ。ダミーデータも作れるよ。',
    'long_description': '# arekore\n記述統計のためのクラスや可視化のあれこれ。ダミーデータも作れるよ。\n\n## Quickstart\n### 1次元データ\n\n```python\nimport matplotlib.pyplot as plt\nimport numpy as np\nfrom arekore import dummy, viz\nfrom arekore.data1d import Data1d, plot_hist\n\n\ndef main():\n    # ダミーデータ生成\n    rawdata = dummy.dist_normal_1d(mean=50, std=10, n=100)\n\n    # 1次元データオブジェクトの作成\n    d = Data1d(rawdata, bins=np.arange(0, 100 + 1, 5))\n\n    # ヒストグラムの描画\n    fig, ax = viz.fig_ax(figsize=(8, 6))\n    plot_hist(ax, d)\n    plt.show()\n\n    # 度数分布表もつくれる\n    freq_table_md = d.freq_table_as_md()\n\n    print(freq_table_md)\n    """| 階級           |   階級値 |   度数 |   累積度数 |   相対度数 |   累積相対度数 |\n|:---------------|---------:|-------:|-----------:|-----------:|---------------:|\n| (-0.001, 10.0] |        5 |      0 |          0 |       0    |           0    |\n| (10.0, 20.0]   |       15 |      0 |          0 |       0    |           0    |\n| (20.0, 30.0]   |       25 |      1 |          1 |       0.01 |           0.01 |\n| (30.0, 40.0]   |       35 |     14 |         15 |       0.14 |           0.15 |\n| (40.0, 50.0]   |       45 |     30 |         45 |       0.3  |           0.45 |\n| (50.0, 60.0]   |       55 |     37 |         82 |       0.37 |           0.82 |\n| (60.0, 70.0]   |       65 |     16 |         98 |       0.16 |           0.98 |\n| (70.0, 80.0]   |       75 |      2 |        100 |       0.02 |           1    |\n| (80.0, 90.0]   |       85 |      0 |        100 |       0    |           1    |\n| (90.0, 100.0]  |       95 |      0 |        100 |       0    |           1    |\n"""\n\n\nif __name__ == \'__main__\':\n    main()\n```\n\n![data1d_histogram](./examples/data1d_histogram.png)\n\n### 2次元データ\n\n```python\nimport matplotlib.pyplot as plt\n\nfrom arekore import dummy, viz\nfrom arekore.data2d import Data2d, plot_regression_line, plot_scatter\n\n\ndef main():\n    # ダミーデータ生成\n    x, y = dummy.xy_specified_cor(r=0.8, n=50)\n\n    # 2次元データオブジェクトの作成\n    d = Data2d(x=x, y=y)\n\n    # 散布図と回帰直線を描画\n    fig, ax = viz.fig_ax(figsize=(8, 6))\n    plot_scatter(ax, d)\n    plot_regression_line(ax, d)\n\n    plt.show()\n\n\nif __name__ == \'__main__\':\n    main()\n\n```\n\n![data2d_scatter_and_regresson_line](./examples/data2d_scatter_and_regresson_line.png)\n',
    'author': 'mohira',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mohira',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
