from nptdms import TdmsFile


def loadTdms(
    fileName,
    group='data',
    accelMps=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    dispMps=[1, 2, 3, 4],
):
    """加载tdms文件

    Args:
        fileName (str): tdms文件路径
        group (str, optional): tdms文件中所要加载的分组. Defaults to 'data'.
        accelMps (list, optional): 所使用的加速度测点. Defaults to [1, 2, 3, 4, 5, 6, 7, 8, 9].
        dispMps (list, optional): 所使用的位移测点. Defaults to [1, 2].

    Returns:
        tuple(accelMps, dispMps, accelDict, dispDict): 加速度字典和位移字典，key -> 测点号，val -> 测点时程数组

    初始化时被调用，也可作为静态方法单独使用
    """

    chAccelMap = {  # 加速度通道
        '1': '加速度0',
        '2': '加速度1',
        '3': '加速度2',
        '4': '加速度3',
        '5': '加速度4',
        '6': '加速度5',
        '7': '加速度6',
        '8': '加速度7',
        '9': '加速度8'
    }

    chDispMap = {  # 位移通道
        '1': '位移0',
        '2': '位移1',
        '3': '位移2',
        '4': '位移3'

    }

    with TdmsFile.open(fileName) as tdmsFile:  # 加载文件
        group = tdmsFile[group]  # 获取组

        # 提取加速度数据
        accelSet = {}
        for mp in accelMps:
            if mp in [2, 5, 8]:
                accelSet[mp] = group[chAccelMap[str(
                    mp)]][:] * (-1) * 10 * 9.8
            else:
                accelSet[mp] = group[chAccelMap[str(mp)]][:] * 10 * 9.8
        # 位移
        dispSet = {}
        for mp in dispMps:
            dispSet[mp] = group[chDispMap[str(mp)]][:] / (-100)

    return accelMps, dispMps,accelSet, dispSet
