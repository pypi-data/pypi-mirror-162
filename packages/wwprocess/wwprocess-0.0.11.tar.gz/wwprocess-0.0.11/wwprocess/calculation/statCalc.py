import numpy as np
from wwprocess.calculation.process import Process


class Rms(Process):
    """
    传入模态试验对象，计算所有测试轮次的位移和加速度的rms
    """

    def __init__(self, exp):
        """
        计算所有风速/模态测试轮次的下所有测点的加速度和位移均方根

        Args:
            exp (Wt/Mt): 传入试验对象

        """
        self.accelDataSet, self.dispDataSet = self.process(exp)

    def _Process__calc(self, mp):
        """
        传入测点的时程曲线，计算均方根

        Args:
            mp (_type_): _description_
        """
        return np.std(mp)


class Avg(Process):
    """
    传入模态试验对象，计算所有测试轮次的位移和加速度的rms
    """

    def __init__(self, exp):
        """
        计算所有风速/模态测试轮次的下所有测点的加速度和位移均方根

        Args:
            exp (Wt/Mt): 传入试验对象

        """
        self.accelDataSet, self.dispDataSet = self.process(exp)

    def _Process__calc(self, mp):
        """
        传入测点的时程曲线，计算均值

        Args:
            mp (_type_): _description_
        """
        return np.mean(mp)
