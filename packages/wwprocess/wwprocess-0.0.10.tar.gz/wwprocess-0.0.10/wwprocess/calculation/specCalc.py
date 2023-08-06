from wwprocess.calculation.process import Process, ProcessCsd
import numpy as np
from scipy import signal


def anpsdCalc(psdInOneRound,
              mps):
    """
    输入一次试验的psd字典：key -> 测点号，val -> psd数组，以及使用到的测点号，返回anpsd数组
    """

    f = psdInOneRound[1][0]
    rowSize = f.size
    colSize = len(mps)
    normPsds = np.empty([rowSize, colSize], dtype=float)
    for mp in psdInOneRound:
        if mp not in mps:
            continue
        normPsds[:, int(mp) - 1] = psdInOneRound[mp][1] / np.sum(psdInOneRound[mp][1])
    anpsdValue = np.mean(normPsds, axis=1)
    return f, anpsdValue


def anpsd(
        psdModal,
        accelMps=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        dispMps=[1, 2]):
    # 输出：字典，键为试验轮次，值为tuple(f, anpsd)
    accelAnpsd = {}
    for round in psdModal.accelData:
        accelAnpsd[round] = [None, None]
        accelAnpsd[round][0], accelAnpsd[round][1] = anpsdCalc(psdModal.accelData[round], mps=accelMps)

    dispAnpsd = {}
    for round in psdModal.dispData:
        dispAnpsd[round] = [None, None]
        dispAnpsd[round][0], dispAnpsd[round][1] = anpsdCalc(psdModal.dispData[round], mps=dispMps)

    psdModal.accelAnpsd = accelAnpsd
    psdModal.dispAnpsd = dispAnpsd

class Psd(Process):
    """
    计算psd

    数据为2级字典，第一级为风速/模态测试轮次，第二级为测点号，值为tuple，第一个元素为f，第二个为amp
    """

    def __init__(
        self,
        exp,
        nfft=2 ** 12,  # 变换点数
        fs=500,  # 采样频率
        window='boxcar',
        nperseg='',
        detrend='linear',
        noverlap=0,
    ):
        self.nfft = nfft
        self.fs = fs
        self.window = window
        if nperseg:
            self.nperseg = nperseg
        else:
            self.nperseg = nfft / 4
        self.detrend = detrend
        self.noverlap = noverlap

        self.accelData, self.dispData = self.process(exp)

    def _Process__calc(self, mp):

        # 计算功率谱
        return signal.welch(
            mp,
            fs=self.fs,
            window=self.window,
            nfft=self.nfft,
            nperseg=self.nperseg,
            detrend=self.detrend,
            noverlap=self.noverlap,
        )


class Csd(ProcessCsd):
    """
    计算csd

    数据为2级字典，第一级为风速/模态测试轮次，第二级为测点号，值为tuple，第一个元素为f，第二个为amp
    """

    def __init__(
        self,
        exp,
        accelRef=3,
        dispRef=2,
        nfft=2 ** 12,  # 变换点数
        fs=500,  # 采样频率
        window='boxcar',
        nperseg='',
        detrend='linear',
        noverlap=0,
    ):
        self.accelRefData = accelRef
        self.dispRef = dispRef
        self.nfft = nfft
        self.fs = fs
        self.window = window
        if nperseg:
            self.nperseg = nperseg
        else:
            self.nperseg = nfft / 4
        self.detrend = detrend
        self.noverlap = noverlap

        self.accelData, self.dispData = self.processCsd(exp, accelRef, dispRef)

    def _ProcessCsd__calcCsd(self, mp, mpRef):

        # 计算功率谱
        return signal.csd(
            mp,
            mpRef,
            fs=self.fs,
            window=self.window,
            nfft=self.nfft,
            nperseg=self.nperseg,
            detrend=self.detrend,
            noverlap=self.noverlap,
        )
