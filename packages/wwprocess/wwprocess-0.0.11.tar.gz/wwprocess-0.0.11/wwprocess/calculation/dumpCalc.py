# 此脚本用半功率法计算阻尼比
import scipy.signal as sig
import numpy as np

def dumpCalc(
    data,  # 谱序列
    f,  # 频率横轴
    ind,  # 峰值序号
):
    w, wh, l, r = sig.peak_widths(
        data,
        [ind],
        rel_height=1 - 0.7071  # 半功率点的高度
    )
    h = wh[0] # 半功率点高度
    freqL = l[0] * (f[1] - f[0]) # 左频率
    freqR = r[0] * (f[1] - f[0]) # 右频率
    dumpRatio = (freqR - freqL) / (freqR + freqL)
    return freqL, freqR, h, dumpRatio

def dumpCalcWithTimeSeq(ampS, ampE, cyc):
    return np.log(ampS / ampE) / (2 * np.pi * cyc)


if __name__ == '__main__':
    print(np.log(np.e))
    print(np.pi)
