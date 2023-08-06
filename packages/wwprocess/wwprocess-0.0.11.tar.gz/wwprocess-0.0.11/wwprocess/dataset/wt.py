import os
import numpy as np
from wwprocess.dataset.loadTdms import loadTdms

"""
将raw目录下的一个风洞试验对应的一个文件夹封装为一个对象

属性包含：
* 风洞试验下各个测点的加速度和位移的时程数据
方法：
* 在初始化时加载所有风速下的加速度和位移数据
"""


class Wt:  # AeroElasticTest
    """封装了风洞试验数据的对象

    Args:
        shape(str): 截面形状 
        windField(str): 风场条件
        angle(str): 风向角
        noGlued(bool, optional): 是否未贴胶带
        thorough(bool, optional): 是否加密风速
    """

    def __init__(self,
                 shape,  # 形状 ori rect ..
                 windField,  # 风场
                 angle,  # 风向角
                 noGlued=False,  # 是否粘住缝隙
                 thorough=False,  # 是否加密风速
                 testDir='' # 是否输入试验文件夹
                 ):
        # 空值
        self.dispMps = []  # 使用的位移测点
        self.accelMps = []  # 使用的加速度测点
        self.accelDataSet = {}  # 所有风向角的加速度数据
        self.dispDataSet = {}  # 所有风向角的位移数据
        # 描述配置
        # 初始化的值
        self.angle = angle
        self.shape = shape
        self.windField = windField
        self.thorough = thorough
        self.noGlued = noGlued
        self.testDir = testDir
        # 加载风洞试验的平均风速数据
        self.__loadMeanFlow()
        # 加载加速度和位移数据
        self.__loadDataInWindSpeeds()

    def __loadMeanFlow(self):
        """
        加载风速数据
        """
        if self.testDir:
            dirPath = f'raw/{self.testDir}'
        elif self.noGlued:
            if self.thorough:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_noGlued_{self.angle}_thorough'
            else:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_noGlued_{self.angle}'
        else:
            if self.thorough:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_{self.angle}_thorough'
            else:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_{self.angle}'
        meanFlowData = np.loadtxt(
            # TODO
            f'{dirPath}/meanFlow.txt')
        self.meanFlows = meanFlowData  # 平均风速数据
        self.windSpeedSeq = range(1, np.size(meanFlowData) + 1)

    # 计算所有风速的均方根，二级词典，一级为测点，二级为风速
    # 可传入使用的测点编号
    def __loadDataInWindSpeeds(self,
                               ):
        """
        加载所有风速下的数据

        在初始化时被调用，更新加速度和位移属性
        """
        # 处理文件路径
        if self.testDir:
            dirPath = f'raw/{self.testDir}'
        elif self.noGlued:
            if self.thorough:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_noGlued_{self.angle}_thorough'
            else:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_noGlued_{self.angle}'
        else:
            if self.thorough:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_{self.angle}_thorough'
            else:
                dirPath = f'raw/{self.shape}_windTunnelTest_{self.windField}_{self.angle}'

        files = os.listdir(dirPath)
        tdmsFiles = list(filter(lambda i: i.split('.')[1] == 'tdms', files))

        # 在每个风速下，调用loadTdms函数加载文件，并添加到对应字典
        accelDataSet = {}
        dispDataSet = {}
        for i in range(0, len(tdmsFiles)):
            accelMps, dispMps, accelSet, dispSet = loadTdms(f'{dirPath}/{tdmsFiles[i]}')
            accelDataSet[i + 1] = accelSet
            dispDataSet[i + 1] = dispSet

        self.accelDataSet = accelDataSet
        self.dispDataSet = dispDataSet
        self.accelMps = accelMps
        self.dispMps = dispMps
