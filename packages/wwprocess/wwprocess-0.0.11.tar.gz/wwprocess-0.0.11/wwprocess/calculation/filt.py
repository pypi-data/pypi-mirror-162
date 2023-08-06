from scipy import signal as sig

# 带通滤波器
def bandpass(data, minFreq, maxFreq, rank=4, fs=500):
    wnMin = 2 * minFreq / fs
    wnMax = 2 * maxFreq / fs
    b, a = sig.butter(rank, [wnMin, wnMax], 'bandpass')
    return sig.filtfilt(b, a, data)


def Filt(wt, minFreq, maxFreq, rank=4, fs=500):
    """
    滤波器

    传入Wt对象，和带通截至频率，对每个数据进行滤波，滤波结果替换原来的数据
    无返回值
    """
    for ws in wt.windSpeedSeq:
        for mp in wt.accelMps:
            wt.accelDataSet[ws][mp] = bandpass(wt.accelDataSet[ws][mp], minFreq, maxFreq, rank, fs)
        for mp in wt.dispMps:
            wt.dispDataSet[ws][mp] = bandpass(wt.dispDataSet[ws][mp], minFreq, maxFreq, rank, fs)
