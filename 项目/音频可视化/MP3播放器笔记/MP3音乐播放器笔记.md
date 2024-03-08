## 数据库数据表设计与实现

### 数据库的基本组成：

数据库是用于存储和管理数据的结构化集合。数据库的基本组成通常包括以下要素：

1. 数据：数据库的核心部分，用于存储有组织的信息。数据可以包括文本、数字、图像、音频等各种类型的信息。

2. 表格（Tables）：数据通常以表格的形式存储，其中每个表格代表一个实体或数据类型。每个表格包含一组行和列，行表示记录，列表示属性。

3. 记录（Records）：记录是表格中的行，每一行代表一个特定的数据实例。例如，一个员工信息表格中的每一行可能代表一个员工的信息。

4. 字段（Fields）：字段是表格中的列，每一列代表一个特定的数据属性。例如，员工信息表格中的字段可以包括姓名、员工号、工资等。

5. 主键（Primary Key）：主键是一个字段或一组字段，用于唯一标识表格中的每个记录。主键确保每条记录都具有唯一的标识符。

6. 查询（Queries）：查询是用于检索、过滤和分析数据的命令或操作。查询可以用来查找特定条件下的记录或执行计算。

7. 索引（Indexes）：索引是一种数据结构，用于加速数据检索操作。它们通常基于一个或多个字段，允许数据库引擎更快地查找特定数据。

8. 视图（Views）：视图是虚拟表格，它基于一个或多个实际表格的查询结果。视图允许用户以不同的角度查看数据，而不实际改变底层数据。

9. 关系（Relationships）：数据库中的不同表格可以通过关系相互关联。这些关系可以是一对一、一对多或多对多的关系，用于建立数据之间的连接。

10. 约束（Constraints）：约束是用于确保数据完整性和一致性的规则。常见的约束包括主键约束、外键约束、唯一约束和检查约束。

11. 存储过程和触发器（Stored Procedures and Triggers）：存储过程是预定义的数据库操作，可以通过调用执行，而触发器是自动执行的操作，通常与数据更改相关。

12. 安全性和权限控制（Security and Authorization）：数据库通常具有安全性特性，以确保只有授权的用户能够访问和修改数据。这包括用户身份验证、权限控制和加密等。

这些是数据库的基本组成要素，不同类型的数据库管理系统（DBMS）可能在实现和扩展这些要素方面有所不同。数据库是在许多应用程序和系统中广泛使用的关键组件，用于存储和管理数据以支持各种业务和信息管理需求。

### SQLite数据库使用步骤：

1. 创建QSqlDatabase对象；
2. 在构造函数中使用`QSqlDatabase::contains("sql_default_connection")`检测对应数据库名是否存在，存在则使用`db=QSqlDatabase::database("sql_default_connection")`接收，不存在使用`db=QSqlDatabase::addDatabase("QSQLITE")`创建并接收；
3. 使用`db.setDatabaseName("mp3listdatabase.db")`设置数据库文件名，**注意**该文件是存放在硬盘中的；
4. **注意**要调用`db.open()`打开数据库，才能进行数据库操作；
5. 创建QSqlQuery类对象，并调用`query.exec()`用于执行SQL语句，**注意**一次只能执行一条语句。
6. 如果`exec()`执行的是select语句，则查询结果存储在QSqlQuery的对象中，通过`next()`进行遍历

### 1. 构造函数初始化

#### 判断数据库连接是否存在，不存在则添加得到连接

[Qt中操作SQLite数据库_qt sqlite-CSDN博客](https://blog.csdn.net/gongjianbo1992/article/details/88070605)

**（在MainViewWidget构造函数中进行）**

```c++
    ui->setupUi(this);

    // 禁止窗口改变尺寸大小
    this->setFixedSize(this->geometry().size());

    // 去掉标题栏
    this->setWindowFlag(Qt::FramelessWindowHint);


    // 1:判断数据库连接是否存在，存在就得到连接，如果不存在添加得到链接
    if(QSqlDatabase::contains("sql_default_connection"))
    {
        // 根据数据库默认连接名称得到连接
        db=QSqlDatabase::database("sql_default_connection");
    }
    else
    {
        db=QSqlDatabase::addDatabase("QSQLITE"); // 添加数据库，得到该数据库的默认连接
        db.setDatabaseName("mp3listdatabase.db"); // 设置数据库文件名称
    }
```

#### 打开数据库，打开数据库标识，并创建两个表

**使用QSqlQuerry类**

- 如果`db.open()`成功，则创建query对象，并创建 歌曲搜索表，歌曲痕迹数据表 并 使用`select`语句查询

```c++
 // 2:打开数据库，打开标识（QSqlQuery类)
    if(!db.open())
    {
        QMessageBox::critical(0,QObject::tr("Open Data Error."),db.lastError().text());
    }
    else
    {
        // 3:定义query对象，得到打开的数据库标识
        // query默认在打开的数据库中操作，此处创建搜索表
        QSqlQuery query;
        QString sql="create table if not exists searchlist(id integer,songname text,singername text,album_id text,hash text)";
        if(!query.exec(sql))
        {
            QMessageBox::critical(0,QObject::tr("create searchlist Error."),db.lastError().text());
        }

        // 同上，此处创建歌曲痕迹数据表
        sql="create table if not exists historysong(id integer primary key autoincrement,songname text,singername text,album_id text,hash text)";
        if(!query.exec(sql))
        {
            QMessageBox::critical(0,QObject::tr("create historysong Error."),db.lastError().text());
        }


```

- 将在 数据库的歌曲痕迹表 中搜索到的所有歌曲显示出来
- 因为搜索表会清空，而历史表不会，而历史数据会保留在本地.db文件上，所以每次打开该程序都需要把历史表的数据显示在qt界面上

```c++
        // 查询历史数据表中的插入歌曲数据
        sql="select *from historysong;";
        if(!query.exec(sql))
        {
            QMessageBox::critical(0,QObject::tr("select historysong Error."),db.lastError().text());
        }

        while(query.next())
        {
            QString songname,singername;
            //query.record()表示查询结果的字段信息
            QSqlRecord rec=query.record();
            
            int ablumkey=rec.indexOf("songname");
            int hashkey=rec.indexOf("singername");
            songname=query.value(ablumkey).toString();
            singername=query.value(hashkey).toString();

            QString strshow=songname + "--" +singername;

            //搜索表和历史表都是QListWidget，添加item的方式都一样
            QListWidgetItem *item=new QListWidgetItem(strshow);
            ui->listWidget_History->addItem(item);
        }
    }

```

### 2. 搜索歌曲

```c++
// 搜索音乐
void MainWidget::on_pushButton_Search_clicked() // OK
{
    // 将原有歌曲数据清空
    ui->listWidget_Search->clear();

    // 先清理数据库中已经存储的 hash等数据
    QSqlQuery query;
    QString sql = "delete from searchlist;";
    if(!query.exec(sql))
    {
        QMessageBox::critical(0,QObject::tr("Delete searchlist Error."),db.lastError().text());
    }

    // 根据用户输入的MP3音乐名称，发起请求操作
    QString url = kugouSearchApi + QString("format=json&keyword=%1&page=1&pagesize=20&showtype=1").arg(ui->lineEdit_Search->text());

```

- 注意：①kugouSerchApi为define的一个搜索网址，②+后面为固定值，只有%1为自定义参数，表示搜索歌曲名

```c++
    httpAccess(url);

    QByteArray JsonData;
    QEventLoop loop;

    auto c = connect(this, &MainWidget::finish, [&](const QByteArray & data)
    {
        JsonData = data;
        loop.exit(1);
    });

    loop.exec();
    disconnect(c);

    //解析网页回复的数据，将搜索得到的音乐hash和album_id与列表的索引值存放到数据库
    hashJsonAnalysis(JsonData);

}

```

- **注意**上面代码中通过loop事件循环检测网页发来的信号，避免还没有接收到信号就disconnect。

- httpAccess(url)：向该url发起http请求操作，为自定义函数，最后返回一个`finish(data)`信号，具体实现如下：

  ```c++
  // 访问HTTP网页
  void MainWidget::httpAccess(QString url)
  {
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
  
  // 读取网络数据的槽函数
  void MainWidget::netReply(QNetworkReply *reply)
  {
      // 获取响应的信息并输出，状态码为200属于正常
      QVariant status_code=reply->attribute(QNetworkRequest::HttpStatusCodeAttribute);
      qDebug()<<status_code;
  
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

  

- ```c++
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

- hashJsonAnalysis(JsonData)：退出事件循环之后将得到的JsonData进行解析（下节实现）

## 下载音乐_数据解析Json显示歌词

注意下载下来的Json是QByteArray，先转换成QJsonDoucument，下载到本地，再转换成QJsonObject，访问k-v对

### 搜索表Json文件分析

[【QT】QT生成与解析JSON数据，包含JSON数组_qt json 数组-CSDN博客](https://blog.csdn.net/rong11417/article/details/104252927)

1. data里面有个key叫data，其对应的value是个**对象**，我们取名为objectInfo；
2. objectInfo中有个key叫info，其对应的value是个**数组**，我们取名为objectHash；
3. objectHash中的元素是个**对象**，我们统一取名为album；
4. album中的key分别是album_id，singername，songname，hash，分别取出其对应的value，并存入数据库

### 历史表Json文件分析

1. data里有key叫lyrics，play_url，对应的value是歌词与音乐的网址
2. 网址可以直接访问，也可以网络请求下载到本地访问。

### 1. 使用Json解析音乐数据

```c++
// 音乐的hash和ablum_id值解析，使用JSON
void MainWidget::hashJsonAnalysis(QByteArray JsonData) // OK
{
    //将JsonData从基于文本的表示转化为 QJsonDocument
    QJsonDocument document = QJsonDocument::fromJson(JsonData);
    
    //document为对象
    if ( document.isObject())
    {
        //一个QJsonObject对象是一个“key/value 对”列表，key 是独一无二的字符串，value 由一个 QJsonValue 表示。
        //QJsonValue可以为数组，对象或其他基本数据类型
        QJsonObject data = document.object();

        //包含指定的 key
        if (data.contains("data"))
        {
            // 获取指定 key 对应的 value，并转换成对象
            QJsonObject objectInfo = data.value("data").toObject();
            //包含指定的 key
            if (objectInfo.contains("info"))
            {
                
                //QJsonArray 数组是值的列表。列表可以被操作，通过从数组中插入和删除 QJsonValue 
                //此处的 QJsonValue 里存放的是数组
                // 获取指定 key 对应的 value，并转换成数组
                QJsonArray objectHash = objectInfo.value("info").toArray();

                for (int i = 0; i < objectHash.count(); i++)
                {
                    QString songname, singername, album_id, hash;
                    QJsonObject album = objectHash.at(i).toObject();
                    if (album.contains("album_id"))
                    {
                        album_id = album.value("album_id").toString();

                    }

                    if (album.contains("singername"))
                    {
                        singername = album.value("singername").toString();

                    }

                    if (album.contains("songname"))
                    {
                        songname = album.value("songname").toString(); // 歌曲名称

                    }

                    if (album.contains("hash"))
                    {
                        hash = album.value("hash").toString();

                    }



                    QSqlQuery query;
                    QString sql = QString("insert into searchList values(%1, '%2', '%3', '%4', '%5')").arg(QString::number(i)).arg(songname).arg(singername).arg(album_id).arg(hash);

                    if ( !query.exec(sql))
                    {
                        QMessageBox::critical(0, QObject::tr("insert Error"),db.lastError().text());
                    }

                    // 将解析的音乐名称，存入listWidget_Search控件列表进行显示
                    QString show = songname + "--" + singername;
                    QListWidgetItem *item = new QListWidgetItem(show);
                    ui->listWidget_Search->addItem(item);
                }
            }
        }
    }

    if(document.isArray())
    {
        qDebug()<<"Array";
    }


}

```

### 2. 下载音乐并播放

```c++
// 音乐歌曲下载和播放
void MainWidget::downloadPlayer(QString album_id,QString hash) // OK
{
	//这个url是固定格式，不用管
    QString url = kugouDownloadApi + QString("r=play/getdata"
                                             "&hash=%1&album_id=%2"
                                             "&dfid=1spkkh3QKS9P0iJupz0oTy5G"
                                             "&mid=de94e92794f31e9cd6ff4cb309d2baa2"
                                             "&platid=4").arg(hash).arg(album_id);

	//执行完并等到网页回复数据的时候，会发送finish(data)信号，由下面的connect接受
    httpAccess(url);

	//有没有觉得15-22行很熟悉！？
    QByteArray JsonData;
    QEventLoop loop;
    auto d = connect(this, finish, [&](const QByteArray & data){
        //显然，JsonData表示从网页上传下来的数据
        JsonData = data;
        loop.exit(1);
    });
    loop.exec();
    disconnect(d);

    // 解析将要播放音乐
    QString music = musicJsonAnalysis(JsonData);

    //用于播放媒体源
    player->setMedia(QUrl(music));

    // 设置音量
    player->setVolume(100);

    // 设置音量的滑动条
    ui->VopSlider->setValue(100);

    // 播放音乐
    player->play();

}
```

- `setMedia`是一个函数，用于在Qt中设置媒体播放器的媒体源。它有两个参数：`media`和`stream`。其中，`media`是一个`QMediaContent`对象，表示媒体文件的路径或URL。如果您想要从本地文件系统中播放媒体文件，可以使用`QUrl::fromLocalFile()`函数将文件路径转换为URL。例如：

  ```cpp
  player->setMedia(QUrl::fromLocalFile("/path/to/music.mp3"));
  ```

  如果您想要从网络上播放媒体文件，可以直接使用URL。例如：

  ```cpp
  player->setMedia(QUrl("http://example.com/music.mp3"));
  ```

  第二个参数`stream`是一个可选参数，用于指定媒体流的格式。如果您不需要指定流格式，则可以将其设置为`nullptr`或省略该参数。

```c++
// 搜索的音乐数据信息JSON解析，解析出真正的音乐文件和歌词
QString MainWidget::musicJsonAnalysis(QByteArray JsonData) // OK
{
    QJsonDocument document = QJsonDocument::fromJson(JsonData);
    if ( document.isObject())
    {
        QJsonObject data = document.object();
        if (data.contains("data"))
        {
            QJsonObject objectPlayUrl = data.value("data").toObject();

            if (objectPlayUrl.contains("lyrics"))
            {
				//发送音乐文件的歌词信号
                emit lyricShow(objectPlayUrl.value("lyrics").toString());
            }

            if (objectPlayUrl.contains("play_url"))
            {
                //返回音乐文件的地址
                return objectPlayUrl.value("play_url").toString();
            }
        }

        if (document.isArray())
        {
            qDebug() << "Array.";
        }
    }

}
```

## 上一曲_ 播放暂停_下一曲 _循环播放实现

### QMediaPlayer类解析



### 1. 双击搜索列表，并将双击到的音乐显示在历史列表并存入歌曲痕迹表中，播放音乐

根据控件的currentRow，将双击到的歌曲与数据库中的歌曲联系起来，然后播放

```c++
void MainWidget::playSearchMusic() // 双击搜索列表，播放音乐 // OK
{    
    // 获取双击的歌曲对应索引，就是数据库当中数据表的ID号
    // 在往数据库中写歌曲的时候，第一个属性值就是ID，表示这首歌曲在数据表中的位置
    // 这个顺序和显示在搜索列表中的顺序一致
    int row=ui->listWidget_Search->currentRow();
    qDebug()<<"row-->"<<row;

    // 查询搜索数据库中数据表中存储的音乐的数据信息
    // 该语句执行完后，会返回所有id为row的歌曲信息,并存储在query中
    QSqlQuery query;
    QString sql=QString("select *from searchlist where id=%1;").arg(row);
    if(!query.exec(sql))
    {
        QMessageBox::critical(0,QObject::tr("select searchlist table Error."),db.lastError().text());

    }

    // 将选中的音乐的数据信息存入历史数据表
    QString songname,singername,album_id,hash;
    //query.next()用于遍历之前select的查询结果
    while(query.next())
    {
        //query.record()用于获取查询结果的字段（即所有列名）
        QSqlRecord recd=query.record();
        //获取对应字段的索引
        //使用索引获取value值的好处：如果字段拼错了，那么在编译阶段就能发现错误
        //否则在运行时才能发现错误
        int songkey=recd.indexOf("songname");
        int singerkey=recd.indexOf("singername");
        int ablumkey=recd.indexOf("album_id");
        int hashkey=recd.indexOf("hash");

        songname=query.value(songkey).toString();
        singername=query.value(singerkey).toString();
        album_id=query.value(ablumkey).toString();
        hash=query.value(hashkey).toString();

        //从歌曲痕迹表中查询hash值为hash的记录
        sql=QString("select hash from historysong where hash='%1';").arg(hash);
        if(!query.exec(sql))
        {
            QMessageBox::critical(0,QObject::tr("select hash Error."),db.lastError().text());

        }

        //如果没有该hash值，则将点击的歌曲插入歌曲痕迹表，否则不做处理
        if(query.next()==NULL)
        {
            //注意历史痕迹表中的id是自动增长的，从1开始。
            sql=QString("insert into historysong values(NULL,'%1','%2','%3','%4')").arg(songname).arg(singername).arg(album_id).arg(hash);
            if(!query.exec(sql))
            {
                QMessageBox::critical(0,QObject::tr("insert historysong Error."),db.lastError().text());
            }

            // 将解析的音乐名称，保存listWidget_History列表控件当中
            QString show=songname + "--" +singername;
            QListWidgetItem *item=new QListWidgetItem(show);
            ui->listWidget_History->addItem(item);
        }
    }

    downloadPlayer(album_id,hash);

}
```
- 双击搜索列表，播放音乐的思路：
  1. 首先该函数为槽函数，在双击搜索列表的某一行后触发；
  2. 通过`int row=ui->listWidget_Search->currentRow();`得出当前点击的row，注意这个row也对应该歌曲在数据库中的id；
  3. 得到id了就可以通过id进行select查询，查询结果存储在query中；
  4. 通过`query.next()`遍历查询结果，显然此处的查询结果只有一个；
  5. 通过`QSqlRecord recd=query.record();`获取当前记录的字段；
  6. 获取字段中每一条属性的索引，并通过索引获取对应的value，至此完成搜索列表上的操作。
  7. 在 歌曲痕迹表 中查询是否存在该歌曲的hash值，没有有则说明 痕迹表 与 历史列表 中无该歌曲的记录，需要插入；
  8. 注意7.中的插入操作对 歌曲痕迹表 和 历史列表 都要进行。
  9. 调用`downloadPlayer(album_id,hash);`下载歌曲并播放。

- 29-37行：

  使用索引获取value值的好处：

  如果字段拼错了，会返回-1，方便调试。

### 2. 双击历史播放列表，播放音乐

```c++
void MainWidget::playHistoryMusic() // 双击历史播放列表，播放音乐 // OK
{
    // 我们要获取双击的哪一行的索引，其实就是数据库中数据表的id编号
    row=ui->listWidget_History->currentRow();
    // qDebug()<<"row-->"<<row;

    // 查询搜索数据库中数据表的历史记录存储的音乐数据信息
    QSqlQuery query;
    //注意arg()中为row+1，因为历史痕迹表中的id是AUTOINCREMENT（即自动增长），默认从1开始
    QString sql=QString("select *from historysong where id = %1;").arg(row+1);
    if(!query.exec(sql))
    {
        QMessageBox::critical(0,QObject::tr("select historysong Error."),db.lastError().text());

    }

    QString album_id,hash;
    while(query.next())
    {
        QSqlRecord recd=query.record();
        int ablumkey=recd.indexOf("album_id");
        int hashkey=recd.indexOf("hash");

        album_id=query.value(ablumkey).toString();
        hash=query.value(hashkey).toString();
    }
    downloadPlayer(album_id,hash);

}
```

### 3. 音量调整_进度调整

```c++
 // 音量调整
void MainWidget::on_VopSlider_valueChanged(int value) // OK
{
    player->setVolume(value);
    ui->label_Vop->setText(QString::number(value));

}

// 进度调整
void MainWidget::on_progressSlider_valueChanged(int value) // OK
{
	//这个time的格式是0小时，value/60000分钟，qRound((value%60000)/1000.0)秒
	//表示我重新拖动的value所对应的分钟：秒
    QTime time(0,value/60000,qRound((value%60000)/1000.0));

    ui->label_Time->setText(time.toString("mm:ss"));
    if(i==false)
    {
        player->setPosition(qint64(value));
    }

}

void MainWidget::on_progressSlider_sliderPressed() // OK
{
    i=false;
}

void MainWidget::on_progressSlider_sliderReleased() // OK
{
    i=true;
}
```

### 4. 下一曲_上一曲 _循环播放 _播放暂停

- 注意：上一曲，下一曲，播放暂停指的是在历史搜索表中进行该操作
- 如果想在搜索表和历史表中都能进行这种操作，需要给搜索表和历史表设置分别设置一个bool值，在双击表的时候把bool设为true，双击另一个表的时候把该值设为false。

```c++
// 上一曲
void MainWidget::on_pushButton_Front_clicked() // OK
{
    row--;
    //row--后<0表示当前播放的是第一首，这时候直接转到最后一首就可以了
    //下一曲的逻辑一样的
    if(row<0)
    {
        row=ui->listWidget_History->count();
    }

    // 查询搜索数据库历史记录表当中存储音乐数据信息
    QSqlQuery query;
    QString sql=QString("select *from historysong where id=%1;").arg(row+1);
    if(!query.exec(sql))
    {
        QMessageBox::critical(0,QObject::tr("select historysong Error."),db.lastError().text());
    }

    QString album_id,hash;
    while(query.next())
    {
        QSqlRecord recd=query.record();
        int ablumkey=recd.indexOf("album_id");
        int hashkey=recd.indexOf("hash");

        album_id=query.value(ablumkey).toString();
        hash=query.value(hashkey).toString();
    }
    downloadPlayer(album_id,hash);

}
```

```c++
//播放暂停
void MainWidget::on_pushButton_Playpause_clicked() // OK
{
    // 播放 暂停图标大家自已去完成（实现切换）
    if(player->state()==QMediaPlayer::PlayingState)
    {
        player->pause();
    }
    else if(player->state()==QMediaPlayer::PausedState)
    {
        player->play();
    }

}

```

```c++
//下一曲
void MainWidget::on_pushButton_Next_clicked() // OK
{
    row++;
    if(row>ui->listWidget_History->count())
    {
        row=0;
    }

    // 查询搜索数据库历史记录表当中存储音乐数据信息
    QSqlQuery query;
    QString sql=QString("select *from historysong where id=%1;").arg(row+1);
    if(!query.exec(sql))
    {
        QMessageBox::critical(0,QObject::tr("select historysong Error."),db.lastError().text());
    }

    QString album_id,hash;
    while(query.next())
    {
        QSqlRecord recd=query.record();
        int ablumkey=recd.indexOf("album_id");
        int hashkey=recd.indexOf("hash");

        album_id=query.value(ablumkey).toString();
        hash=query.value(hashkey).toString();
    }
    downloadPlayer(album_id,hash);

}
```

```c++
//循环播放注意加个connect判断当前音乐是否结束，其他实现与下一曲类似
connect(&player, &QMediaPlayer::mediaStatusChanged, [&](QMediaPlayer::MediaStatus status) {
    if (status == QMediaPlayer::EndOfMedia) {
        // 音乐播放完成
        // 在这里执行您的操作
    }
});

```

