from abc import ABC, abstractmethod


class Process(ABC):
    """
    循环调用calc()函数处理数据
    """

    def process(self, exp):
        """
        处理函数，传入试验对象和计算函数，返回相应的结果

        Args:
            exp (Wt/Mt): 试验对象
            calc (function): 计算均方根或均值的函数
        """

        # 定义返回值字典
        results = []  # accel disp

        sigs = [exp.accelDataSet, exp.dispDataSet]
        for sig in sigs:
            dataSet = {}
            for round in sig:  # 对accel disp的每一轮试验
                dataMps = {}
                for mp in sig[round]:  # 对一轮试验的每个测点
                    dataMps[mp] = self.__calc(sig[round][mp])  # 调用计算函数
                dataSet[round] = dataMps
            results.append(dataSet)

        return results[0], results[1]  # 返回加速度和位移

    @abstractmethod
    def __calc(self, mp):
        pass


class ProcessCsd(ABC):
    def processCsd(self, exp, accelMpRef, dispMpRef):
        """
        处理函数，传入试验对象和参考点，返回相应的结果
        """

        # 处理加速度
        accelDataSet = {}
        for round in exp.accelDataSet:  # 对accel disp的每一轮试验
            dataMps = {}
            for mp in exp.accelDataSet[round]:  # 对一轮试验的每个测点
                dataMps[mp] = self.__calcCsd(
                    exp.accelDataSet[round][mp], exp.accelDataSet[round][accelMpRef])  # 调用计算函数
            accelDataSet[round] = dataMps

        # 处理位移
        dispDataSet = {}
        for round in exp.dispDataSet:  # 对accel disp的每一轮试验
            dataMps = {}
            for mp in exp.dispDataSet[round]:  # 对一轮试验的每个测点
                dataMps[mp] = self.__calcCsd(
                    exp.dispDataSet[round][mp], exp.dispDataSet[round][dispMpRef])  # 调用计算函数
            dispDataSet[round] = dataMps

        return accelDataSet, dispDataSet  # 返回加速度和位移

    @abstractmethod
    def __calcCsd(self, mp, mpRef):
        pass
