# Hbase_Day2

## 一、Hbase的集群

### 1. HDFS集群，Yarn集群，ZK集群

```	
1> 创建虚拟机，2块网卡
2> 主机名 + host映射
3> 免密
4> java的运行环境：jdk
5> 关闭防火墙：关闭服务，关闭自启
6> 克隆+网络适配+hadoop安装+hadoop配置
7> 安装zookeeper
8> 如上主要参考 hadoop_03笔记即可
```

```markdown
zk集群搭建
   1. 解压缩
   2. 创建data文件夹
      mkdir  zk_home/data
   3. zk_home/conf/zoo.cfg (改名)
      dataDir=/opt/install/zookeeper-3.4.5/data
      server.1=hadoop1:2888:3888
      server.2=hadoop2:2888:3888
      server.3=hadoop3:2888:3888    
   4. zk_home/data/myid
      hadoop1   1
      hadoop2   2
      hadoop3   3
   5. 如上配置，同步集群中的每一个节点
   6. 每一个节点  bin/zkServer.sh start
   7. bin/zkServer.sh status #可以查看zk状态
```
### 2. 时间同步

> 在各个机器间统一时间管理
>
> 3台机器，组成集群
>
> 1台为主时间服务器，2台为从时间服务器

#### 2.1 配置过程

```markdown
 1. yum -y install ntp    #三台机器都安装
 2. service ntpd start #三台机器都启动服务
    chkconfig ntpd on  #开机自启
 3. 在服务器主节点
    ntpdate -u 202.112.10.36 #和互联网时间服务器校准时间
 4. 编辑主节点 /etc/ntp.conf，设置自动校准
    #        主节点的网络号
    restrict 192.168.5.0 mask 255.255.255.0 nomodify notrap
    # 中国最活跃的时间服务器 : http://www.pool.ntp.org/zone/cn
    server 210.72.145.44 perfer      # 中国国家授时中心 (优先)
    server 202.112.10.36             # 1.cn.pool.ntp.org (备用)
    server 59.124.196.83             # 0.asia.pool.ntp.org (备用)

    # 允许上层时间服务器主动修改本机时间
    restrict 210.72.145.44 nomodify notrap noquery
    restrict 202.112.10.36 nomodify notrap noquery
    restrict 59.124.196.83 nomodify notrap noquery

    # 外部时间服务器不可用时，以本地时间作为时间服务
    server  127.127.1.0     # local clock
    fudge   127.127.1.0 stratum 10
5. client端(2台从服务器)
	#编辑 /etc/ntp.conf
    server 192.168.5.20
    restrict 192.168.5.20 nomodify notrap noquery
    # 外部时间服务器不可用时，以本地时间作为时间服务
    server  127.127.1.0     # local clock
    fudge   127.127.1.0 stratum 10
6. 三台机器： service ntpd restart
7. 从节点同步主节点时间： ntpdate -u 192.168.5.20
8. linux的	date命令查看处理结果
```

### 3. HBase集群

#### 3.1 配置过程

``` 
1. 解压hbase
2. 修改hbase_home/conf/hbase-env.sh
export JAVA_HOME=/usr/java/jdk1.7.0_71
export HBASE_MANAGES_ZK=false
3. hbase-site.xml
<property >
    <name>hbase.tmp.dir</name>
    <value>/opt/install/hbase-0.98.6-hadoop2/data/tmp</value>
</property>
<property >
    <name>hbase.rootdir</name>
    <value>hdfs://hadoop1:8020/hbase</value> 
</property>
<property >
    <name>hbase.cluster.distributed</name>
    <value>true</value>
</property>
<property>
<name>hbase.zookeeper.quorum</name>
<value>hadoop1,hadoop2,hadoop3</value>
</property>
4. 配置regionservers，告知哪些是从节点
hadoop1
hadoop2
hadoop3
5. 替换jar hadoop jar
6. scp 分发
7. 启动hbase
    在hbase的主节点： bin/start-hbase.sh。即可启动所有hbase节点
    #bin/hbase-daemon.sh start master/regionserver
8. hbase 的 master自带 high-available方案
   在3机器上将master都启动即可
```
## 二、列簇相关属性

1. 指定列簇相关的属性

   ```sh
   create 'ns145:t1',{NAME=>'F1', VERSIONS => '3'，IN_MEMORY=> 'true',TTL=>'10'}
   
   desc 'ns145:t1'
   ```

2. 列簇常见的属性

   ```markdown
   # 列簇对应限定符 能存几个版本的数据
   1. VERSIONS => '1'
   # 指定列簇对应的值 存储时间  单位 s
   2. TTL => 'FOREVER'（time to live）
   # 指定HBase上存储的数据 是否 启动压缩
   3. COMPRESSION => 'NONE'
   # 激进缓存
   4. IN_MEMORY => 'false’  
   #  HFile 块的大小 64k 
   5. BLOCKSIZE => '65536'
   # scan 多  块 大  减少系统的IO
   # 随机 多  块 小  （HFile 有索引概念）
   6. BLOCKCACHE => 'true'
   # 提高查询效率
   7. BLOOMFILTER 布隆过滤
   ```

## 三、HBase的体系架构【重点】

### 1. HBase中表数据的存储架构

 ![hbase结构](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/HBase/png/hbase结构.png)

### 2. Region裂变机制

> 一张表，初始只有一个分区，
>
> 随之数据越来越多，分区中的数据量增大，会有多个HFile出现，
>
> Hbase会进行所有HFile的合并，然后重新分为不同的分区
>
> 在合并的过程中，会伴随着将有删除标记的数据移除(墓碑数据)

### 3. 细节

> Hbase作为基于Hadoop的nosql数据库，会将数据存储到hdfs中
>
> Master负责管理 RegionServer，管理元信息
>
> RegionServer负责管理名下的多个分区
>
> 当有数据要io时，要和master通信


