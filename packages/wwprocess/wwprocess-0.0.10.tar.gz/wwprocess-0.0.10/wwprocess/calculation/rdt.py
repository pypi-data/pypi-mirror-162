import numpy as np
from wwprocess.calculation.filt import Filt
from wwprocess.calculation.densify import Densify
from wwprocess.calculation.statCalc import Rms


def grepStartX(
    data,  # 纵轴
    rmsVal,  # 均方根值
    error=0.05,  # 和均方根差多少
    numToExam=10  # 向左向右检查多少个
):
    """
    找有效的序列起点，返回起点序列的序号
    """
    effectiveStartX = []
    for ind in range(0, len(data)):
        curError = np.abs(np.abs(data[ind]) - rmsVal) / rmsVal
        # 误差超限则终止
        if curError > error:
            continue
        effective = True
        for i in range(1, numToExam + 1):
            leftInd = ind - i
            rightInd = ind + i
            if leftInd >= 0:  # 左侧序列够用
                compareErrorLeft = np.abs(
                    np.abs(data[leftInd]) - rmsVal) / rmsVal
                if compareErrorLeft < curError:
                    effective = False
                    break
            if rightInd < len(data):  # 右侧序列够用
                compareErrorRight = np.abs(
                    np.abs(data[rightInd]) - rmsVal) / rmsVal
                if compareErrorRight < curError:
                    effective = False
                    break
        if effective == True:
            effectiveStartX.append(ind)
    return effectiveStartX


def getMean(
    data, # 数据序列
    rmsVal, # 使用的均方根值
    lenOfSlice, # 数据长度
):
    """
    对单条数据做平均处理，返回平均后的结果，和使用的数据集长度作为参考
    """
    startX = grepStartX(data, rmsVal)
    subSeqs = []
    dataLen = len(data)
    for ind in startX:
        # 处理不够长的序列
        if ind + lenOfSlice > dataLen:
            continue
        subSeq = np.array(data[ind: ind + lenOfSlice])
        # 处理起始数据点为负值的情况
        if data[ind] < 0:
            subSeq = subSeq * (-1)
        subSeqs.append(subSeq)
    subSeqs = np.array(subSeqs).T
    avgSeq = np.mean(subSeqs, axis=1)
    return avgSeq, len(startX)


def Rdt(wt, modFreq, lenOfSlice = 10000):
    
    Filt(wt, modFreq * 0.75, modFreq * 1.25)
    Densify(wt)
    rms = Rms(wt)

    for ws in wt.windSpeedSeq:
        for mp in wt.accelMps:
            rmsVal = rms.accelDataSet[ws][mp]
            wt.accelDataSet[ws][mp], _ = getMean(wt.accelDataSet[ws][mp], rmsVal, lenOfSlice)
        for mp in wt.dispMps:
            rmsVal = rms.dispDataSet[ws][mp]
            wt.dispDataSet[ws][mp], _ = getMean(wt.dispDataSet[ws][mp], rmsVal, lenOfSlice)
        print(f'wsSeq{ws} finished')
