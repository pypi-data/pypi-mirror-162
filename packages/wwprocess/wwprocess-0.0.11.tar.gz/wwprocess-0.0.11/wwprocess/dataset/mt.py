import os
from wwprocess.dataset.loadTdms import loadTdms

"""
将raw目录下的一个模态试验对应的一个文件夹封装为一个对象

属性包含：
* 模态试验下各个测点的加速度和位移时程数据
方法：
* 在初始化时加载加速度和位移数据
"""


class Mt:  # modalTest
    """封装了风洞试验数据的对象

    Args:
        shape(str): 截面形状 
        testDir(str, optional): 可指定试验文件夹名称
        noGlued(bool, optional): 是否未贴胶带
    """

    def __init__(self,
                 shape,  # 形状 ori rect ..
                 testDir='',  # 输入模态测试的文件夹名，为空则使用默认命名方式
                 noGlued=False,  # 是否粘住缝隙
                 ):
        # 空值
        self.dispMps = []  # 使用的位移测点
        self.accelMps = []  # 使用的加速度测点
        self.accelDataSet = {}  # 二级字典，第一级为第几轮测试，第二级为测点号
        self.dispDataSet = {}  # 位移，逻辑同上
        # 描述配置
        # 初始化的值
        self.shape = shape
        self.testDir = testDir
        self.noGlued = noGlued
        # TODO
        self.__loadDataInAllRounds()

    # 计算所有风速的均方根，二级词典，一级为测点，二级为风速
    # 可传入使用的测点编号
    def __loadDataInAllRounds(self):
        """
        加载模态测试数据

        在初始化时被调用，更新加速度和位移属性
        """
        # 处理文件路径
        if self.testDir:
            dirPath = f'raw/{self.testDir}'
        else:
            if self.noGlued:
                dirPath = f'raw/{self.shape}_modalTest_noGlued'
            else:
                dirPath = f'raw/{self.shape}_modalTest'

        files = os.listdir(dirPath)
        tdmsFiles = list(filter(lambda i: i.split('.')[1] == 'tdms', files))

        # 对每轮模态测试，调用loadTdms函数加载文件，并添加到对应字典
        accelDataSet = {}
        dispDataSet = {}
        for i in range(0, len(tdmsFiles)):
            accelMps, dispMps, accelSet, dispSet = loadTdms(
                f'{dirPath}/{tdmsFiles[i]}')
            accelDataSet[i + 1] = accelSet
            dispDataSet[i + 1] = dispSet

        self.accelDataSet = accelDataSet
        self.dispDataSet = dispDataSet
        self.accelMps = accelMps
        self.dispMps = dispMps
