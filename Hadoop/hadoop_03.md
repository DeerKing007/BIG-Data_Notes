# Hadoop_Day3

## 一、HDFS高级理论-持久化

### 1.谁的数据需要持久化

```
namenode是在内存中运行的，其掌握着hdfs的关键数据，namenode的数据安全至关重要！
```

```
namenode数据持久化！是必需的过程。
```

```
datanode中的所有数据，本来就在磁盘，所以不涉及额外的持久化。
```

### 2.namenode中如何持久化

#### 2.1 namenode中的两类文件

```
edits：HDFS操作的日志记录，每次对HDFS进行修改操作后，都会往edits中记录一条日志；
fsimage：HDFS中命名空间、数据块分布、文件属性等信息都存放在fsimage中；
1> 在初始启动namenode时，是需要格式化的；正是在格式化时，会创建第一个空白的fsimage文件
2> namenode启动后也会创建空白的edits文件，每次对hdfs进行操作时，都会向edits文件中写入记录日志
3> 它们都存储在：xxx/hadoop-2.5.2/data/tmp/dfs/name/current
```

#### 2.2 Checkpoint

> 检查点：在一些特定的时刻，会触发一个检查点，会将edits文件中的所有记录合并到fsimage中，并会创建
>
> ​               新的空白的edits文件用于继续记录日志

```
1>在每次启动Namenode时，会把edits中的记录合并(merge)到fsimage中，并且把edits清空。所以fsimage
  总是记录启动Namenode时的状态，而edits在每次启动时也是空的，它只记录本次启动后的操作日志。
2>某些时刻会将Namenode中的edits和fsimage文件拷贝到SecondaryNamenode上，然后将edits中的
  记录与fsimage文件merge以后形成一个新的fsimage，这样不仅完成了对现有Namenode数据的备份，而且还产生 
  了持久化操作的fsimage。最后一步，Second Namenode需要把merge后的fsimage文件upload到Namenode上
  面，完成Namenode中fsimage的更新。
【以上是两种checkpoint的时刻，一个是namenode自己做，一个是secondarynamenode做】
【注意：在通过 sbin/start-dfs.sh启动集群时，默认在namenode所在主机上启动一个SecondaryNamenode】
```

```
secondarynamenode的执行时刻，有如下两项配置决定：
1>fs.checkpoint.period：设置两次相邻checkpoint之间的时间间隔，默认是1小时2>dfs.namenode.checkpoint.txns：设置一个事务执行数量的阈值，达到这个阈值，就强制执行一次
    checkpoint,默认为1000000次事务。
二者满足任何一点都会触发一次checkpoint
```

 ![持久化](png\持久化.png)

#### 2.3 数据恢复

> 可以部分还原NameNode数据(secondary会将自己的fsimage+edits传送给namenode一份以恢复部分数据)

```xml
1. 可以选择指定 FSImage 和 EditsLog的保存目录
   （默认都存在在core-site中的hadoop.tmp.dir目录下的 dfs/name目录中）
	hdfs-site.xml
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///opt/install/hadoop-2.5.2/data/tmp/dfs/name</value>
    </property>
    <property>
        <name>dfs.namenode.edits.dir</name>
        <value>file:///opt/install/hadoop-2.5.2/data/tmp/dfs/name</value>
    </property>
2. 将checkpiont时间缩短，便于测试
	hdfs-site.xml
    <property> (secondarynode 每隔60s做一次checkpoint==就是把edits和fsimage复制出来合并)
        <name>dfs.namenode.checkpoint.period</name>
        <value>60</value>
    </property>
3. 模拟namenode问题，kill namenode
    *在hdfs中存入文件a，然后过60s，
    *立即 kill -9 1414(杀掉namenode)
    *手动清空fsimage和editslog所在目录(模拟namenode硬盘损坏)
    *并重新创建dfs.namenode.name.dir所指向的目录(模拟在新硬盘上创建目录) 
      ==/opt/install/hadoop-2.5.2/data/tmp/dfs/name==
    *将secondarynamenode中的 data/tmp/dfs/namesecondary/current/中的所有文件都拷贝到
     namenode中的 data/tmp/dfs/name/current中 (current目录需要自己建)
4. 启动namenode
 执行：sbin/hadoop-daemon.sh start namenode 启动即可按照拷入的持久化文件恢复内存数据
```

> NameNode与SecondaryNameNode尽量不要放置在同一个节点，避免同时损坏，不能还原数据

```markdown
1. dfs.namenode.secondary.http-address
2. dfs.namenode.secondary.https-address
在namenode所在的节点上，hdfs-site.xml中
<property>
    <name>dfs.namenode.secondary.http-address</name>
    <value>hadoop4:50090</value>
</property>
<property>
    <name>dfs.namenode.secondary.https-address</name>
    <value>hadoop4:50091</value>
</property>
注意：secondarynode中也要配置master的host位置才可以
```
> SecondaryNameNode还原NameNode部分数据，会有丢失的可能。
>
> 如果要解决上述问题，可以使用Hadoop2.x中的HA 高可用的NameNode



## 二、HDFS集群的热扩容，热删除

> 【了解即可】

### 1. 增加节点

```
1. 保证新加的机器 (hosts配置 域名设置 iptables 配置主机到从机SSH免密码登陆   
   hadoop安装(并在core-site.xml 中配好master的地址即可)
   【注意在namenode上添加新机器的host映射  "192.168.5.13 hadoop4"】
2.启动新机器的datatnode (克隆机的话，要记得先删除data/tmp目录，再启动)
  执行：sbin/hadoop-daemon.sh start datanode
3.此时访问namenode，新加的datanode已经自己汇报给namenode，新机器已经加入集群成功。
4.在master的slaves文件中添加新节点的host(如果重启，master可以启动新加的从节点)==可选
5.此时新增的节点，只能保证后续的数据可以分担存储压力，但已经存在的数据依然在旧有的datanode上，
  所以此时可以做一次平衡，把已经存在的数据也可以迁移一部分到新加的datanode上
  执行：sbin/start-balancer.sh 即可
```

### 2. 删除节点

```markdown
1. 创建一个新的文件 位置 名字 随便 定义要删除的主机的host即可
hadoop4
2. 配置 hdfs-site.xml
   增加dfs.hosts.exclude参数，配置第一步新建文件的位置
   <property>
   	<name>dfs.hosts.exclude</name>
   	<value>/root/rm145/del145</value>
   </proerty>
3. 通过命令刷新集群
bin/hdfs dfsadmin -refreshNodes
此时被移除的节点上的block会分配给其他节点
4. 把删除的节点 从slaves 删除
5. kill 掉 被删除的DataNode
   dfs.hosts.exclude 的信息删除
```

## 三、Yarn

### 1. Yarn简介

> #### Yarn:资源调度和任务调度的框架 

> #### **主要组件：ResourceManager、NodeManager、ApplicationMaster** 
>
> **ResourceManager：在系统中的所有应用程序中仲裁资源的最终权限.是一个全局的资源管理器**
>
> **NodeManager：是每个节点上的资源和任务管理器,一方面,它会定时地向 RM 汇报本节点上的 **
>
> ​				**资源使用情况和各个 Container 的运行状态;另一方面,它接收并处理来自 AM 的 **
>
> ​                                **Container启动 / 停止等各种请求**
>
> **ApplicationMaster：负责与 RM 调度器协商以获取资源(用 Container 表示)，负责和与 NM 通信以启动 / **
>
> ​                                       **停止容器。监控所有任务运行状态,并在任务运行失败时重新为任务申请资源以重启**
>
> ​                                       **任务**
>
> 【**其中container代表一套资源(cpu,内存)，rm会为每个任务分配一个容器用于支持其运行的资源需求**】

> **Yarn框架图：**
>
>  ![yarn_结构](png\yarn_结构.gif)

### 2. 启动yarn

单机版

```markdown
sbin/hadoop-daemon.sh start namenode
sbin/hadoop-daemon.sh start datanode  #启动hdfs

sbin/yarn-daemon.sh start resourcemanager
sbin/yarn-daemon.sh start nodemanager    #启动yarn
```

集群版

```markdown
sbin/start-dfs.sh
sbin/stop-dfs.sh  启动集群中各机器的namenode或datanode进程

sbin/start-yarn.sh
sbin/stop-yarn.sh  启动集群中各机器的resoucemanager和nodemanager
```
### 3. yarn集群详细流程【重点】

![yarn-mr流程](png\yarn-mr流程.png)



## 四、Map-Reduce

> #### **map-reduce:分布式计算模型**
>
> **主要包括：map-task和reduce-task**

### 1. MapReduce核心流程

> map-reduce的运行过程主要分5步：
>
>   【input-->map-->shuffle-->reduce-->output】
>
> ![map-reduce流程](png\map-reduce流程.png)

### 2. map-reduce流程实例

> Word Count 单词计数

![wordcount-mr](png\wordcount-mr.png)

### 3. Word Count Python代码

> **1> 注意**

```markdown
因为Hadoop是Java编程语言开发的，所以Python无法直接调用，Hadoop为了解决这个问题
提供了一个Hadoop Streaming的技术解决
```
> **2> MapReduce运行**

```markdown
1. hdfs 上传需要处理的原始文件
   bin/hdfs dfs -put localpath  hdfspath
2. 开发Map Reduce [python2.x]
3. Map 和 Reduce py代码 和 run.sh 上传 Linux操作系统中
4. 执行：./run.sh
5. run.sh，内容：
#hadoop家目录下的一个jar包
STREAM_JAR_PATH="/opt/install/hadoop-2.5.2/share/hadoop/tools/lib/hadoop-streaming-2.5.2.jar"

#/demo1/src.txt 是一个hdfs路径，是要运算的输入文件
INPUT_FILE_PATH="/demo1/src.txt"
#/demo2 是一个hdfs路径，是输出路径。注意：输出路径必须是不存在的
OUTPUT_PATH="/demo2"

#执行了一个hadoop指令
/opt/install/hadoop-2.5.2/bin/hadoop jar $STREAM_JAR_PATH \
-input $INPUT_FILE_PATH \
-output $OUTPUT_PATH \
-mapper "python map.py" \
-reducer "python reduce.py" \
-file ./map.py \
-file ./reduce.py
```

## 五、Hadoop HDFS HA架构

> 高可用架构  high available

```markdown
HA架构的NameNode,由一个主节点对外提供服务，同时通过Zookeeper把主节点中的内容，自动的同步到备机中，保证主，备数据的一致。如果主机出现问题，备机会通过zookeeper自动升级主节点。原主机再启动namenode后会成为备机
```

![1537342838016](png\1537342838016.png)

![主备同步](png\主备同步.png)

### 1. 搭建zookeeper集群 

> 奇数个节点，至少 3个节点 

```markdown
1. 上传zookeeper到linux服务器，并解压缩/opt/install中
2. zookeeper解压目录/conf，设置zk的配置文件
   zoo_sample.cfg 改名 成 zoo.cfg
   【cp zoo_sample.cfg zoo.cfg】
3. 修改zoo.cfg中的配置信息
    # zookeeper_home 创建 data目录
    dataDir=/opt/install/zookeeper-3.4.5/data
    #3个zookeeper节点
    server.1=hadoop1:2888:3888 
    server.2=hadoop2:2888:3888
    server.3=hadoop3:2888:3888
   （其中的 1，2，3是各个机器的标识)
4. 在刚创建的data目录下面 创建一个myid文件
   #第一台机器  myid文件中，输入一个字符: 1  （对应配置中的server.1）
   进而这台机器都知道自己是 【server.1】
5. scp 把zookeepr的解压目录 拷贝到 集群的每一个节点 （跳过）
   ops：则所有机器都安装了zk，且配置完毕

6. 每台机器 修改 myid 文件的值
    #第一台服务器  myid文件中，输入一个字符: 1  （对应配置中的server.1）
    #第二台服务器  myid文件中，输入一个字符: 2  （对应配置中的server.2）
    #第三台服务器  myid文件中，输入一个字符: 3  （对应配置中的server.3）

7. 启动zookeeper集群
    在每个zookeeper的机器上都要执行：
    bin/zkServer.sh start 
    bin/zkServer.sh status 查看集群状态  follower=从  leader=主 
```
### 2. Hadoop基本环境

```markdown
可使用现有的hadoop集群，需要删除各机器 hadoop_home/data/tmp下的所有内容；
如果没有可以按照第二天的笔记搭建即可
```
![主机进程分布](png\主机进程分布.png)

### 3. 配置Hadoop-HA

#### 3.1 hdfs-site.xml

```xml
<!--指定hdfs的nameservice为ns9,是当前集群的标识-->
<property>
    <name>dfs.nameservices</name>
    <value>ns9</value>
</property>
<!-- ns9下面有两个NameNode，分别是nn1，nn2 
     一主 一备 共两个namenode
-->
<property>
    <name>dfs.ha.namenodes.ns9</name> <!-- ns9 == nameService -->
    <value>nn11,nn22</value>
</property>
<!-- nn1的RPC通信地址 -->
<property>
    <name>dfs.namenode.rpc-address.ns9.nn11</name>
    <value>hadoop1:8020</value>
</property>
<!-- nn1的http通信地址 -->
<property>
    <name>dfs.namenode.http-address.ns9.nn11</name>
    <value>hadoop1:50070</value>
</property>
<!-- nn2的RPC通信地址 -->
<property>
    <name>dfs.namenode.rpc-address.ns9.nn22</name>
    <value>hadoop2:8020</value>
</property>
<!-- nn2的http通信地址 -->
<property>
    <name>dfs.namenode.http-address.ns9.nn22</name>
    <value>hadoop2:50070</value>
</property>

<!-- qjournal://..;..;../ns9 中"ns9"依然是nameservice
	 journalnode至少需要3个，且为奇数个
-->
<property>
	<name>dfs.namenode.shared.edits.dir</name>
    <value>qjournal://hadoop1:8485;hadoop2:8485;hadoop3:8485/ns9</value>
</property>
<!-- 指定JournalNode在本地磁盘存放数据的位置，该目录会自动创建 -->
<property>
    <name>dfs.journalnode.edits.dir</name>
    <value>/opt/install/hadoop-2.5.2/journal</value>
</property>
<!-- 开启NameNode故障时自动主备切换 -->
<property>
    <name>dfs.ha.automatic-failover.enabled</name>
    <value>true</value>
</property>
<!-- 配置失败自动切换实现方式 -->
<property>
    <name>dfs.client.failover.proxy.provider.ns9</name>
    <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
</property>
<!-- 配置隔离机制，如果ssh是默认22端口，value直接写sshfence即可 -->
<property>
    <name>dfs.ha.fencing.methods</name>
    <value>sshfence</value>
</property>
<!-- 使用隔离机制时需要ssh免密登陆 -->
<property>
    <name>dfs.ha.fencing.ssh.private-key-files</name>
    <value>/root/.ssh/id_rsa</value>
</property>
```

#### 3.2 core-site.xml

```xml
<property>		
    <name>fs.default.name</name>
    <!--<value>hdfs://hadoop1:8020</value> 
        不再这么写，因为不再是某一个主机作为namenode，而是多台主机作为namenode-->
    <value>hdfs://ns9</value> （ops:ns9 == nameseverice）
                              （这个标识在hdfs-site.xml中已声明）
</property>
<property>
    <name>hadoop.tmp.dir</name>
    <value>/opt/install/hadoop-2.5.2/data/tmp</value>
</property>
<property>
    <!-- zookeeper 位置 -->
    <name>ha.zookeeper.quorum</name> （配zookeeper的各个节点，namenode需要和zookeeper连接）
    <value>hadoop1:2181,hadoop2:2181,hadoop3:2181</value>
</property>
```
#### 3.3 yarn-site.xml

```xml
<property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
</property>
<property>
    <name>yarn.nodemanager.aux-services.mapreduce_shuffle.class</name>
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
</property>
<!-- 指定resourcemanager地址 -->
<property>
    <name>yarn.resourcemanager.hostname</name>
    <value>hadoop3</value>
</property>
```

#### 3.4 yarn-env.sh中添加内容

```
export JAVA_HOME=/usr/java/jdk1.7.0_71
```

#### 3.5 同步配置

> **将	core-site.xml**  
>
> ​    	**hdfs-site.xml** 
>
> ​    	**yarn-site.xml** 
>
> ​	**yarn-evn.sh**  
>
> ​	**/root/.ssh/**
>
> ​        **slaves文件   **
>
> ​        **同步给所有机器**
>
> ​        **注意：namenode的公钥也要发给自己一份**
>
> ​        **除公私钥之外其他配置也要给datanode发一份**
>
> 免密技巧：在一台主机上：
>
>     1. ssh-keygen 生成公钥 私钥
>        
>     2. ssh-copy-id root@自己的host  将公钥发送给自己(自己给自己免密)
>        
>     3. 将自己的 /root/.ssh/所有内容   发送给其他要免密的机器
>        
>        scp  /root/.ssh/*  root@hadoop2:/root/.ssh
>        
>        scp  /root/.ssh/*  root@hadoop3:/root/.ssh
>
> 关于hadoop_home/etc/hadoop/slaves的作用：
>
> 1.告知namenode：谁是datanode 【sbin/start-dfs.sh就可以找到对应的datanode】
>
> 2.告知resourcemanager：谁是改启动nodemanager的机器

#### 3.6 执行命令

> 注意：清空之前的  hadoop_home/data/tmp
>
> 请按照如下顺序，依次启动集群各个节点

```
1>首先启动各个节点的Zookeeper，在各个节点上执行以下命令：
  	zk_home/bin/zkServer.sh start

2> 在某一个namenode节点执行如下命令，创建命名空间
    bin/hdfs zkfc -formatZK

3> 在每个journalnode节点用如下命令启动journalnode
   	至少需要3个，且为奇数个
	sbin/hadoop-daemon.sh start journalnode

4> 在主namenode节点格式化namenode
	bin/hdfs namenode -format

5> 在主namenode节点启动namenode进程
	sbin/hadoop-daemon.sh start namenode

6> 在备namenode节点执行第一行命令，把备namenode节点的目录格式化并把元数据从主namenode节点copy
   过来:
	bin/hdfs namenode -bootstrapStandby
   然后用第二个命令启动备namenode进程:
	sbin/hadoop-daemon.sh start namenode

7> 在两个namenode节点都执行以下命令
	sbin/hadoop-daemon.sh start zkfc

8> 在所有datanode节点都执行以下命令启动datanode
	sbin/hadoop-daemon.sh start datanode

9> 在rm所在机器上运行：
   需要在rm机器上运行，且rm机器上要配置好slaves文件，已确定每个datanode，为他们启动nodemanager
	./sbin/start-yarn.sh
```

> 如上搭好集群后，后续的集群启动：

```sh
sbin/start-dfs.sh  （启动 nn,dn,jn,zkfc）
sbin/start-yarn.sh  (启动 rm,nm)
bin/zkServer.sh start (启动 zk)
```

