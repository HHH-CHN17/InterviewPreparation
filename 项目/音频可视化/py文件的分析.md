## 算法实现

### 1.  初始化阶段

1. 导入numpy（处理音频数据，可以用QByteArray和QVector代替），wave（可以理解为Multimedia中QAudioBuffer的对象，用于对音频进行解析）
2. 定义平滑参数，用于稍后拓展音频的时间
3. 用wave获取wav的通道数，采样宽度，帧率，帧数。
4. 计算wav音频持续时间
5. 将wav当成双通道进行处理，读取wav的数据并展开成双通道（相邻样本点表示不同声道），再合并成单通道的数据，为了方便后面进行图像对称操作，需要消除音频中的负值。用数组存储起来并将里面的样本点转换成qint16
6. 综上操作，此时得到的数组（理解成QVector）里面每个值存储的是wav中对应的每一个样本点（帧）。

### 2. 优化帧

为了将原本复杂的直方图进行平滑处理，肯定要缩减wav中原本的样本点数量以及样本点上下波动范围，这样才能减少处理的时间。

看了libAudiofile的官方文档，以及libRosa开发人员写的论文，发现他们对音频的处理是通过滑动窗口来对帧进行平滑处理，但为了进一步减少数据量，通过以下方式处理：

那我该如何达到以上的目的呢，我们可以将所有的样本点进行分组，每一组取平均值，得到一组新的样本点，这样就能有效减少样本点的数量并且减少样本点的波动。

那问题来了，我分组的依据是什么呢，总帧数是确定的，我们可以按倍数拉长音频总时间（倍数为5），用总帧数/拉长后时间，这样我得到的新频率就是原来的1/5，也就是说如果我不×5，那么我分组后可能一组里有100帧，这样处理可能造成最终输出图像失真，×5之后一组只有20帧了，这样的话可以在减少样本点数量的同时保留最终输出图像的音频特性。

综上操作，我们得到的数组里，每一个值对应一个优化后的样本点，但此时直接输出的话，由于样本点过少，会导致锯齿的现象。

### 3. 补帧

```python
	# 平滑处理（补帧操作）
	# x表示x轴的时间点，waveInfo['monoAudio']中的每一个值表示每一个x坐标对应的数据点
    x = np.linspace(0, waveInfo['durationSec'], len(waveInfo['monoAudio']))
    #interp1d为三次插值函数，用它对直方图的数据进行插值处理
    SmoothFunc = interpolate.interp1d(x, waveInfo['monoAudio'], kind='cubic')
    
	#xSmooth表示更新后的x轴，x坐标的数量是原始x轴的5倍
    xSmooth = np.linspace(x.min(), x.max(), 5 * len(x)) # pyqtgraph中有抗锯齿处理,这里我们实际上就是取消了中值滤波

    #向SmoothFunc传入新的x轴，进行平滑操作，同时为了使图像便于观察，进行/10操作
    #同时将数组取反，使图像上下对称
    waveInfo['nonnegtiveAudio'] = SmoothFunc(xSmooth) / 10
    waveInfo['negativeAudio'] = np.negative(waveInfo['nonnegtiveAudio'])
    waveInfo['x_axis'] = xSmooth
    del waveInfo['monoAudio']
    
    return waveInfo
```

### 4. 需要注意的细节

1. wav的数据转换到vector时，由于存储类型是qint16，所以vector的size是QByteArray的一半。
2. 分组之后可能导致会有分组填不满，这个时候需要用0填充
3. 用0填充之后会导致音频文件时长增加，需要减去额外时间。

## 界面实现

- 可以用绘图事件，在老师推荐下尝试使用e-charts

- 注意：
  1. 鼠标滚轮放大之后跑动条更新的时间应该缩短，下方的时间条的单位应该细化，实现方法应该是重载positionChanged函数，使里面的定时器随着时间单位的变化而变化。
  2. 其余的我想看看e-charts中有无类似接口