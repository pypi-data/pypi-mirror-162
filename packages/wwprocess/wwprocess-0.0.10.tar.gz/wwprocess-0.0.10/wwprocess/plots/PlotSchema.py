#!/usr/bin/python
"""
此模块中的Schema函数提供带有全局绘图参数的模板

使用方法：
from template import Schema
Schema('single|double')返回plt对象
"""

import matplotlib.pyplot as plt
from cycler import cycler


config = {
    'figure.figsize': (6.27, 4.5),  # 图像尺寸，单位inch，按a4纸，左右边距各2.5cm调整
    # 'figure.figsize': (6.27, 4.7025),  # 图像尺寸，单位inch，按a4纸，左右边距各2.5cm调整
    'figure.constrained_layout.use': True,
    'figure.constrained_layout.h_pad': 0.1,  # 上下留白的比例
    'figure.constrained_layout.w_pad': 0.1,
    'savefig.dpi': 400,
    'savefig.format': 'png',
    'savefig.pad_inches': 0,
    'font.family': 'serif',  # 衬线字体
    'font.serif': ['microsoft yahei'],  # 微软雅黑
    'font.size': 10.5,  # 相当于小四大小
    'mathtext.fontset': 'stix',  # matplotlib渲染数学字体时使用的字体，和times new roman差别不大
    # 'lines.marker': 's',
    'lines.linewidth': 1,
    'lines.markersize': 3,
    'axes.titlesize': 10.5,
    'axes.titlepad': 15,
    'axes.labelsize': 11,
    'axes.labelpad': 7,
    'axes.unicode_minus': False,  # 处理负号，即-号
    'axes.grid': True,
    'axes.grid.which': 'major',
    'xtick.direction': 'in',
    'xtick.minor.visible': True,
    'xtick.labelsize': 8,
    'ytick.direction': 'in',
    'ytick.labelsize': 8,
    'ytick.minor.visible': True,
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'grid.color': '#c1c1c1',
    'legend.fontsize': 9,
    'legend.fancybox': False,
    'legend.edgecolor': '#000',
    'legend.loc': 'best',
}

# 双排图片的排版配置
configDouble = config.copy()
configDouble['figure.figsize'] = (3, 2.25)  # 图像尺寸，单位inch
configDouble['figure.constrained_layout.w_pad'] = 0.02
configDouble['figure.constrained_layout.h_pad'] = 0.05
configDouble['axes.titlesize'] = 9
configDouble['axes.titlepad'] = 7
configDouble['axes.labelsize'] = 10
configDouble['axes.labelpad'] = 5
configDouble['legend.fontsize'] = 7
configDouble['xtick.labelsize'] = 7
configDouble['xtick.minor.visible'] = False
configDouble['ytick.labelsize'] = 7
configDouble['ytick.minor.visible'] = False


def cycleOpt(plt):
    plt.rc('axes', prop_cycle=(
        cycler('color', ['#1f77b4',
                         '#ff7f0e',
                         '#1f77b4',
                         '#ff7f0e'
                         ]) +
        cycler('linestyle', ['-',
                             '-',
                             '--',
                             '--'
                             ])))


def PlotSchema(alignment, useCycle=False):
    """工厂函数，返回plt对象

    Args:
        alignment (str): 'single'单排 | 'double'双排布局
        useCycle (bool, optional): 是否循环颜色和线型. Defaults to False.

    Raises:
        Exception: _description_

    Returns:
        plt: malplotlib.pyplot对象
    """
    if alignment == 'single':
        plt.rcParams.update(config)
    elif alignment == 'double':
        plt.rcParams.update(configDouble)
    else:
        raise Exception('布局参数错误 -> 单列布局：single，双列布局：double')
    # 颜色和线形循环
    if useCycle:
        cycleOpt(plt)
    return plt


# 用于调试全局参数
if __name__ == '__main__':
    import numpy as np

    plt = PlotSchema('single')

    testDataX = np.arange(-10, 10, 0.1)
    testDataY = np.sin(testDataX)

    fig, ax = plt.subplots()

    ax.plot(testDataX, testDataY, label='sine曲线')
    ax.set_title('title 标题 1234 $math^2$')
    ax.set_xlabel('title 标题 1234 $math^2$')
    ax.set_ylabel('title 标题 1234 $math^2$')
    ax.legend()

    plt.show()
