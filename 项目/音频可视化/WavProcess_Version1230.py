# 12.30时间轴修正
import numpy as np
import wave
from scipy import interpolate

SmoothTime = 5

def ReadFileFromPath(path):
    try:
        f = wave.open(path)
    except Exception as e:
        print(e)
        return
    #waveinfo是一个字典，相当于map
    waveInfo = {}
    waveInfo['channelNum'] = f.getnchannels()
    waveInfo['sampWidth'] = f.getsampwidth()
    #wav音频文件的频率
    waveInfo['frameRate'] = f.getframerate()
    #wav音频文件的总帧数
    waveInfo['frameNum'] = f.getnframes()

    #waveInfo['durationSec']表示wav音频所持续的时间（单位：秒）
    waveInfo['durationSec'] = waveInfo['frameNum'] / waveInfo['frameRate']

    #用f.readframes方法读取音频文件的所有帧，得到一个字节串对象，然后将数据转换成qint16，再转换成二维数组
    #在C++中，可以用QByteArray接收原始音频数据，然后用QVector<qint16>接收转换后的qint16的数据
    #注意vector的size为QByteArray的size()/2，因为每个帧的振幅占2个字节，此时完成音频文件的一维数组初始化
    #但此时音频文件是单声道，为实现双声道的效果，需要把一维数组转换成二维数组，C++示例代码如下：
    #QVector<qint16> leftChannel, rightChannel;
    #for (int i = 0; i < audioVector.size(); i += 2)//注意i每次要加2，即相邻帧代表左右两个声道
    #{
    #    leftChannel.append(audioVector[i]);
    #    rightChannel.append(audioVector[i + 1]);
    #}
    stereoAudio = np.frombuffer(f.readframes(waveInfo['frameNum']), dtype=np.short).reshape(-1, 2)
    stereoAudio = stereoAudio.T

    #首先，用stereoAudio[0]和stereoAudio[1]分别表示立体声音频的左右两个通道，它们都是一维数组，每个元素表示一个采样点的值。
    #然后，用numpy模块的加法和除法运算将两个通道的数据相加并除以2，得到一个一维数组，表示两个通道的平均值，也就是一个单声道音频。
    #然后，用numpy模块的where函数将单声道音频的数据中小于0的值替换为0，这样可以去除负值的噪音，得到一个一维数组，表示一个非负的单声道音频。
    #最后，将这个一维数组赋值给waveInfo字典的’monoAudio’键，表示这是一个单声道音频。
    #
    #使用二维数组的好处：你可以直接用一维数组来处理音频数据，但是这样可能会增加代码的复杂度和运行时间。
    #因为如果你用一维数组，你需要自己计算每个通道或每个分组的起始和结束位置，然后用切片操作来获取它们的数据。
    #这样可能会导致代码的可读性和效率降低。而如果你用二维数组，你可以直接用索引或循环来访问每个通道或每个分组的数据，
    #这样可以使代码更简洁和高效
    waveInfo['monoAudio'] = (stereoAudio[0] + stereoAudio[1]) / 2
    waveInfo['monoAudio'] = np.where(waveInfo['monoAudio'] > 0, waveInfo['monoAudio'], 0)
    waveInfo['monoAudio'] = waveInfo['monoAudio'].astype(np.short)

    # x毫秒作为一条直方图的依据
    # 以每一帧的后五毫秒的数据做一个分组
    if waveInfo['durationSec'] * SmoothTime > int(waveInfo['durationSec'] * SmoothTime):
        waveInfo['durationSec'] = int(waveInfo['durationSec']) + 1

    #这几行代码的作用是计算每个分组的大小，也就是每个分组包含的帧数。具体的逻辑如下：
    #首先，用计算音频文件的总帧数除以每个分组包含的毫秒数的余数，看是否为0。
    #如果为0，说明音频文件的总帧数刚好可以被每个分组包含的毫秒数整除，也就是说每个分组的大小都相等。
    #这时，计算音频文件的总帧数除以每个分组包含的毫秒数的商，得到每个分组的大小，并赋值给groupSize变量。
    #如果不为0，说明音频文件的总帧数不能被每个分组包含的毫秒数整除，也就是说最后一个分组的大小会小于其他分组。
    #这时，计算音频文件的总帧数除以每个分组包含的毫秒数的商，然后再加一，
    #得到每个分组的大小，并赋值给groupSize变量。这样可以保证所有的数据都被分组，但是最后一个分组会有一些空余的位置。
    if waveInfo['frameNum'] % (waveInfo['durationSec'] * SmoothTime) == 0:
        groupSize = waveInfo['frameNum'] // (waveInfo['durationSec'] * SmoothTime)
    else:
        groupSize = waveInfo['frameNum'] // (waveInfo['durationSec'] * SmoothTime) + 1


    # 首部填充0
    #首先，计算需要在音频数据前面填充0的个数，这个个数等于分组大小乘以每个分组包含的毫秒数再减去音频文件的总帧数。
    #然后，用numpy模块的pad函数在音频数据前面填充0，使其长度刚好等于分组大小乘以每个分组包含的毫秒数，这样可以保证每个分组都被填满。
    #接着，用reshape方法将音频数据变成一个二维数组，每一行表示一个分组，每一列表示一个帧。
    padNum = groupSize * waveInfo['durationSec'] * SmoothTime - waveInfo['frameNum']
    waveInfo['monoAudio'] = np.pad(waveInfo['monoAudio'], [int(padNum), 0], mode='constant')
    waveInfo['monoAudio'] = waveInfo['monoAudio'].reshape(-1, int(groupSize))

    #然后，用for循环遍历每一个分组，并用mean方法计算每个分组的平均值，这样可以得到一个一维数组，表示每个分组的均值。
    #接下来，用numpy模块的unique函数去除重复的值，并用切片操作将二维数组变成一维数组，并用flatten方法将其展平。
    #最后，将这个一维数组赋值给waveInfo字典的’monoAudio’键，表示这是一个直方图的数据。
    #
    #至此完成数据的缩减，但是遇见的问题是帧数不够转换成图形之后无法完全体现音频的波形。
    for i in range(len(waveInfo['monoAudio'])):
        waveInfo['monoAudio'][i] = waveInfo['monoAudio'][i].mean()
    np.unique(waveInfo['monoAudio'], axis=0)
    waveInfo['monoAudio'] = waveInfo['monoAudio'][::, 0:1]
    waveInfo['monoAudio'] = waveInfo['monoAudio'].flatten()

    # 补偿时间---补点后增加了10帧
    #首先，判断padNum是否大于0，也就是是否有在音频数据前面填充0的操作，如果有，则说明音频数据的长度增加了，也就是音频文件的持续时间延长了。
    #然后，将音频文件的持续时间减去0.79秒，这是为了补偿填充0带来的时间延长。这个0.79秒可能是作者根据实验得到的一个经验值。
    #最后，将减去0.79秒后的值赋值给waveInfo字典的’durationSec’键，表示这是一个补偿后的音频文件的持续时间。
    if padNum > 0:
        waveInfo['durationSec'] = waveInfo['durationSec'] - 0.79

    # 平滑处理（补帧操作）
    #首先，用numpy模块的linspace函数创建一个等差数列，表示音频文件的时间轴，并赋值给x变量。
    #   这个数列的起点是0，终点是音频文件的持续时间（是原始音频的持续时间，不是拓展后的音频持续时间），元素个数是直方图的数据的个数。
    #然后，用scipy模块的interp1d函数创建一个三次插值函数，并用它对直方图的数据进行插值处理，并赋值给SmoothFunc变量。
    #   这个函数可以根据给定的时间点（x）和数据点（waveInfo['monoAudio']），生成一个连续的函数，可以用来计算任意时间点的数据值。
    x = np.linspace(0, waveInfo['durationSec'], len(waveInfo['monoAudio']))
    SmoothFunc = interpolate.interp1d(x, waveInfo['monoAudio'], kind='cubic')

    #接着，用numpy模块的linspace函数再次创建一个等差数列，表示音频文件的平滑后的时间轴，并赋值给xSmooth变量。
    #   这个数列的起点和终点和x变量相同，但是元素个数是x变量的五倍（其实应该是smoothTime倍），这样可以得到更多的时间点，使得曲线更平滑。
    #然后，用SmoothFunc函数对xSmooth变量中的每个时间点计算对应的数据值，并除以10，得到一个一维数组，
    #   并赋值给waveInfo字典的’nonnegtiveAudio’键。这个除以10的操作可能是为了缩小数据的范围，使得曲线更容易观察。
    #接着，用numpy模块的negative函数对’nonnegtiveAudio’键中的一维数组取负值，
    #   并赋值给waveInfo字典的’negativeAudio’键。这样可以得到一个对称的曲线，表示音频文件的波形。
    #然后，将xSmooth变量赋值给waveInfo字典的’x_axis’键，表示音频文件的平滑后的时间轴。
    #最后，删除waveInfo字典中不再需要的’monoAudio’键，并返回waveInfo字典。
    xSmooth = np.linspace(x.min(), x.max(), 5 * len(x)) # pyqtgraph中有抗锯齿处理,这里我们实际上就是取消了中值滤波

    #这里是对新时间点对应的每一个数据点进行/10，使图像更加易于观察
    #同时将数组取反，使图像上下对称
    waveInfo['nonnegtiveAudio'] = SmoothFunc(xSmooth) / 10
    waveInfo['negativeAudio'] = np.negative(waveInfo['nonnegtiveAudio'])
    waveInfo['x_axis'] = xSmooth
    del waveInfo['monoAudio']

    return waveInfo

if __name__ == "__main__":
    pass

