## 1. 构造函数初始化

### 1.1 初始化数据库

1. 创建QSqlDatabase对象；
2. 在构造函数中使用`QSqlDatabase::contains("sql_default_connection")`检测对应数据库名是否存在，存在则使用`db=QSqlDatabase::database("sql_default_connection")`接收，不存在使用`db=QSqlDatabase::addDatabase("QSQLITE")`创建并接收；
3. 使用`db.setDatabaseName("mp3listdatabase.db")`设置数据库文件名，**注意**该文件是存放在硬盘中的；
4. **注意**要调用`db.open()`打开数据库，才能进行数据库操作；

### 1.2 创建双表，在界面上显示历史表

1. 创建QSqlQuery类对象，并调用`query.exec()`用于执行SQL创建双表，**注意**一次只能执行一条语句。
2. 如果`exec()`执行的是select语句，则查询结果存储在QSqlQuery的对象中，通过`next()`进行遍历，并通过`QSqlRecord recd=query.record();`获取遍历到的当前记录的字段，通过字段访问value

## 2. 搜索歌曲功能实现并导入至搜索表与Qt界面

### 2.1 根据接口搜索

```c++
// 实例化网络请求操作事项
request=new QNetworkRequest;
// 将url网页地址存入 request请求当中
request->setUrl(url);

// 实例化网络管理（访问）
manager=new QNetworkAccessManager;
// 通过get方法，上传具体的请求
manager->get(*request);

// 当网页回复消息时，触发 finished信号，通过netReply读取数据信息
connect(manager,SIGNAL(finished(QNetworkReplay*)),this,SLOT(netReply(QNetworkReply* reply)));
}
```

### 2.2 下载完成后发送信号

```c++
// 读取网络数据的槽函数
void MainWidget::netReply(QNetworkReply *reply)
{
    //对reply进行重定向
    reply->attribute(QNetworkRequest::RedirectionTargetAttribute);

    // 没有错误返回
    if(reply->error() == QNetworkReply::NoError)
    {
        //网页回复消息时，信号会附带一个reply，里面存储着网页回复的具体消息
        QByteArray data=reply->readAll();
        emit finish(data);
    }
    else
    {
        qDebug()<<reply->errorString();
    }

    reply->deleteLater();

}
```
注意接收时要通过事件循环接收，防止还没下载完就执行处理Json的代码

```c++
QByteArray JsonData;
QEventLoop loop;
//auto c表示一个QMetaObject::Connection，一般用于稍后断开连接
auto c = connect(this,finish,[&](const QByteArray &data)
{
	JsonData=data;
	loop.exit(1);
});

loop.exec();
disconnect(c);
```

### 2.3 解析Json

注意下载下来的Json是QByteArray，先转换成QJsonDoucument，下载到本地，再转换成QJsonObject，访问k-v对

[【QT】QT生成与解析JSON数据，包含JSON数组_qt json 数组-CSDN博客](https://blog.csdn.net/rong11417/article/details/104252927)

#### 2.3.1 搜索表Json

1. data里面有个key叫data，其对应的value是个**对象**，我们取名为objectInfo；
2. objectInfo中有个key叫info，其对应的value是个**数组**，我们取名为objectHash；
3. objectHash中的元素是个**对象**，我们统一取名为album；
4. album中的key分别是album_id，singername，songname，hash，分别取出其对应的value，并存入数据库

#### 2.3.2 历史表Json

1. data里有key叫lyrics，play_url，对应的value是歌词与音乐的网址
2. 网址可以直接访问，也可以网络请求下载到本地访问。

## 3. 双击搜索/历史表播放歌曲

- 通过QMediaPlay操作url或者本地mp3文件
- 如果想在搜索表和历史表中都能进行这种操作，需要给搜索表和历史表设置分别设置一个bool值，在双击表的时候把bool设为true，双击另一个表的时候把该值设为false。
