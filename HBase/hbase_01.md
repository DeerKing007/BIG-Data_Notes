# Hbase_Day1

## 一、HBase的引言

### 1. HBase基本概念：

```markdown
是apache组织提供的基于Hadoop的NoSQL数据库，是google BigTable的开源实现
```
### 2. NoSQL特点：

```markdown
1. 大多数NoSQL产品 是内存型
2. 性能极高
3. 对集群友好
```
### 3. NoSQL分类

```markdown
1. kv类型
   redis 
2. 文档类型 （JSON BSON)
   mongoDB
3. 列类型类型 （Column)
   HBase、Cassandra
4. 图形类型
   NEO4j
```
## 二、 HBase存储结构

> 也是一行行的数据
>
> 每行的标识为：rowkey
>
> 每行除了rowkey外，还有其他列簇，如 info   address
>
> 每行的每个列簇中存储的 多个 【键：值】==【列限定符：数据】
>
> 每个限定符都有version，version的值是个timestamp
>
> **hbase的数据层级： namespace下是多个table，table下是多个行，行中是多个列簇(column family)，**
>
> **列簇中是多个“列限定符:数据”**
>
> 注意：“列限定符”==“列簇名:限定符”



 ![hbase的数据存储结构](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/HBase/png/hbase的数据存储结构.png)

 ![hbase的数据存储结构2](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/HBase/png/hbase的数据存储结构2.png)

## 三、HBase安装

### 1. 保证Hadoop安装

> hbase是基于hadoop的nosql数据库

### 2. 安装zk

> zookeeper

```markdown
1> 解压缩zk
2> 在zk_home创建data文件夹
3> 修改配置信息:conf/zoo.cfg
	dataDir=/opt/install/zookeeper-3.4.5/data
4> 启动zk：bin/zkServer.sh start
```

### 3. 安装HBase

#### 3.1 解压

> 解压 并创建目录：`Hbase_Home/data/tmp`

#### 3.2 HBase配置

> `HBase_Home/conf/hbase-env.sh`

```sh
export JAVA_HOME=/usr/java/jdk1.7.0_71
export HBASE_MANAGES_ZK=false
```

#### 3.3 HBase配置

> `HBase_Home/conf/hbase-site.xml`

```xml
<!-- 声明工作目录 -->
<property >
    <name>hbase.tmp.dir</name>
    <value>/opt/install/hbase-0.98.6-hadoop2/data/tmp</value>
</property>
<property >
    <name>hbase.rootdir</name>
    <value>hdfs://hadoop1:8020/hbase9</value>
    <!-- 需要在hdfs上为hbase开辟一个目录： /hbase9 -->
</property>
<property >
    <name>hbase.cluster.distributed</name>
    <value>true</value>
</property>
<!-- 声明zookeeper的host -->
<property>
    <name>hbase.zookeeper.quorum</name>
    <value>hadoop1</value>
</property>
```

#### 3.4 修改regionservers

>  有自己的主从模式：master-region
>
>  定义从服务器位置 : `hbase_home/conf/regionservers`

```
hadoop1
```

#### 3.5 替换hbase相关hadoop的jar

```sh
1> 删除 hbase_home/lib 下的 hadoop-*.jar  和  zookeeper*.jar
rm -f hadoop-*.jar
rm -f zookeeper*.jar
2> 然后复制jar到 hbase_home/lib下
```

#### 3.6 启动hbase

```sh
bin/hbase-daemon.sh start master #启动主
bin/hbase-daemon.sh start regionserver  #启动从
```

## 四、HBase常见的命令使用

> 没有库的概念；有的是namespace；作用类似库
>
> 技巧：*输入一部分指令按tab提示
>
> ​           *执行help指令列举所有指令
>
> ​           *help '指令名' ，可以查看某指令的说明

### 1.Hbase-Shell

```sh
# 登录HBase (ops:输入命令时，不能退格删除 Ctrl+backspace 即可)
bin/hbase shell
```

### 2. NameSpace

```sh
# 数据库=namespace 相关命令
list_namespace #查看所有数据库清单

create_namespace 'ns9' #创建名为ns9的命名空间

drop_namespace 'ns9' #删除库ns9 (要先删除其中的表)

describe_namespace 'ns9' #查看库名为ns9的描述信息

list_namespace_tables 'ns9' #查看ns9库下的表
list #查看非空库下所有表
```

### 3.表

```sh
#表相关命令
# 创建表
1. 基本形式
# 创建表t1, 表中一个列簇:f1
create 't1', 'f1'  #默认会创建在default数据库中

2. 多列族
create 't2','info','address'...

3. 指定具体的namespace
create 'ns9:t1','f1'

4. 具体描述列簇属性的建表方式 
create 'ns9:t1','f1','f2'
#VERSIONS是列簇中可以保留几个数据版本
create 'ns9:t1',{NAME=>'f1',VERSIONS=>'2'},{NAME=>'f2',VERSIONS=>'3'}  
【NAME和VERSIONS必须大写】

5. 查看表说明
describe 't1' # 查看默认命名空间中的t1
describe 'ns9:t1'  #查看 ns9中的 t1
desc  等价于 describe

6. 删除表
# 让表失效后，再删除
disable 't1'
drop 't1' #删除默认空间的表
disable 'ns9：t1' #失效ns9下的t1表
drop 'ns9:t1' #删除ns9空间的表

7.删除某库下所有表
disalbe_all 'ns9:.*' # 失效ns9下所有表 【.* 是正则】
drop_all 'ns9:.*' #杀出ns9下所有表

disable_all '.*:.*' #失效除默认库外的所有库的所有表
drop_all '.*:.*' #删除除默认库外的所有库的所有表

8. 插入数据
#create 'ns9:user','info'
put 'ns9:user','001','info:name','suns'
     表名      rowkey  列簇：限定符  值
     
9. 删除数据
#删除user表中001行中info列簇下的name
delete 'ns9:user','001'，'info:name'
#删除时间戳为1534864463888的数据，时间戳不加引号
delete 'ns9:user','001','info:name',1534864463888 
#删除一整行
deleteall 'ns9:user','001'

10. 查询 查一行或一个列
get 'ns9:user','001'  #查询rowkey为‘001’的一整行数据
get 'ns9:user','001','info:name' #查询001行 info列中name的数据
#查询对应时间戳的值，时间戳不加引号
get 'ns9:user','001',{COLUMN=>'info:name',TIMESTAMP=>1547134289133}

11.全表查询
scan 'ns9:user' #查询user表的所有数据行，(ops:hbase会对rowkey有自动的排序)
#查询user表的 从'a'到'c'行 
scan 'ns9:user', {STARTROW => 'a',STOPROW => 'c'}
#查看表中的最新3个版本的数据
scan "ns145:t_test146",{VERSIONS=>3,RAW=>true}
#包含 startrow  不包含 stoprow
```

> 坑：在hbase赋值是 “=>” ，容易误写成“=”，如 STARTROW=’a‘ ,STOPROW='b',此时会导致
>
> STARTROW不再是“STARTROW”  而是’a‘.则使用了STARTROW的指令的语义会发生改变

## 五、Hbase的Python访问方式

```python
# 1.在python的虚拟环境中安装依赖程序包：python3版本  happybase 
pip install thrift
pip install thrift-sasl
pip install happybase

# 2.在hbase端，启动 thirt服务
bin/hbase-daemon.sh start thrift

#python代码 
import happybase
#建议与HBase连接  thrift服务端口：9090
connection = happybase.Connection(host="192.168.184.16", port=9090) 
connection = happybase.Connection(host="hadoop1", port=9090)
connection.open() #打开连接

# 注意：如上代码在windows运行时，会又一个bug，需要改动一个源码：
#      ....\Lib\site-packages\thriftpy\parser\parser.py
#修改其中的488行为如下情况：
#if url_scheme == '':
if url_scheme in ('e', ''): #根据错误信息改写本行，【其中 ‘e’,要看异常】
```

```python
#建表测试
# hbase  create 'baizhi125:user','f1','f2'
# hbase  create 'baizhi125:user',{NAME=>'f1',VERSIONS=>1},{NAME=>'f2'}
families = {
    "fie1":dict(),
    "fie2":{"max_versions":3}
}
connection.create_table('baizhi125:user',families)

#删除表
connection.delete_table('baizhi125:user',disable=True)
```

```python
#插入一个数据
# 1获取表对象
table = connection.table('baizhi125:user')
# hbase put 'baizhi125:user',"rowkey","base:name","suns"
table.put("001",{"base:name":"suns"})
table.put("001",{"base:sex":"male"})
table.put("002",{"base:name":"huxz"，"address:city":"bj"})

#删除数据
table.delete("001") #一整行
table.delete("001",columns=['base:name']); #行中的某些列的值
#查询
table.row("001") #一整行
table.row("001",columns=["hbase:name"]) #某一行中的某些列

scanner = table.scan() #查全表
scanner = table.scan(columns=('address',),limit=2) #查询“address”列簇的，前2行
print(list(scanner)) #转成list，或for循环打印
```

