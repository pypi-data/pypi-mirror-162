import numpy as np
from scipy.interpolate import interp1d
from wwprocess.dataset.wt import Wt
from wwprocess.plots.PlotSchema import PlotSchema


def Densify(wt, density=10):
    """
    将wt中的每个数据进行插值加密，两点之间的插值个数为density
    """
    for ws in wt.windSpeedSeq:
        for mp in wt.accelMps:
            wt.accelDataSet[ws][mp] = dens(wt.accelDataSet[ws][mp], density=density)
        for mp in wt.dispMps:
            wt.dispDataSet[ws][mp] = dens(wt.dispDataSet[ws][mp], density=density)

def dens(
    data, 
    density = 10 # 每两个点之间的点数
):
    dataLen = len(data)
    # 横轴
    x = np.arange(0, dataLen)
    # 插值函数
    f1 = interp1d(x, data, kind='linear')
    # 确定加密后的点个数
    # 公式：(点数 - 1) * 两点之间插值个数 * 点数
    # 例如，有20个点，每两个点之间插10个值，则共有(20 -1) * 10 + 20 = 210个点
    totalPoints = (dataLen - 1) * density + dataLen
    denseSeq = np.linspace(0, dataLen - 1, totalPoints)
    return f1(denseSeq)
