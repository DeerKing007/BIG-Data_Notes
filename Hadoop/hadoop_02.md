# Hadoop_Day2

## 一、Hadoop组成的4大模块

> （Hadoop2.x）

```markdown
4大模块   和他们对应的配置文件               
Hadoop-Common 包含很多工具        对应配置：core-site.xml  
Hadoop-HDFS  用于存储             对应配置：hdfs-site.xml
Hadoop-MapReduce  负责运算        对应配置：mapred-site.xml
Hadoop-Yarn  资源管理             对应配置：yarn-site.xml
```

## 二、Hadoop配置

> 默认配置
>
> 官网可查

```markdown
*-default.xml   hadoop默认配置信息
core-defau.xml
hdfs-default.xml
yarn-default.xml
mapred-default.xml
```

> 自定义配置
>
> `hadoop_home/etc/hadoop/`下的 xx-site.xml
>
> core-site.xml
>
> hdfs-site.xml
>
> mapred-site.xml(复制)
>
> yarn-site.xml

```
修改时在对应的xx-site.xml中添加property标签
<property>
   <name>dfs.replication</name>
   <value>2</value>
</property>
修改后会覆盖默认配置
```

## 三、HDFS的Client访问【重点】

![1537239274885](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537239274885.png)

### 1. HDFS Shell命令

```markdown
1. 查看hdfs目录命令
bin/hdfs dfs -ls /
bin/hdfs dfs -ls /suns
2. 创建目录的命令
bin/hdfs dfs -mkdir 目录名字
bin/hdfs dfs -mkdir /suns
bin/hdfs dfs -mkdir -p /a/b/c/d/e
3. 本地文件上传到hdfs
bin/hdfs dfs -put 本地的文件路径  hdfs文件路径
bin/hdfs dfs -put /root/data/data1 /suns
4. 查看hdfs文件
# HDFS 分布式大数据文件系统 只存文本本件
bin/hdfs dfs -text /suns/data1
bin/hdfs dfs -cat /suns/data1
5. 从hdfs中下载文件到本地
bin/hdfs dfs -get hdfs文件路径  本地路径
6. 从hdfs中删除文件或者文件夹
bin/hdfs dfs -rm /suns/hello.txt
bin/hdfs dfs -rm -r /suns/data1
7. cp命令复制
bin/hdfs dfs -cp 原始位置 目标位置
8. mv命令 移动 或者 改名
bin/hdfs dfs -mv 原始位置 目标位置
```

```xml
<!--删除的细节
    修改垃圾箱的文件保存时间  默认 0  分钟 不保存
    垃圾箱的位置
    /user/root/.Trash/180918031000/suns/data1
    在core-site.xml中添加如下配置
-->
 <property>
	<name>fs.trash.interval</name>
	<value>10</value>
  </property>
```

指令截图：

 ![1537242945926](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537242945926.png)

### 2. HDFS的文件权限

> 和linux一样

```xml
<!--在 hdfs-site.xml 中设置如下，可以关闭权限控制-->
<property>
   <name>dfs.permissions.enabled</name>
   <value>false</value>
</property>
```

### 3. web访问

> 浏览器可以查看hdfs文件信息
>
> http://hadoop.baizhiedu.com:50070  可以访问到hdfs中的namenode


![1537241071516](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537241071516.png)

### 4. HDFS的Python客户端

> 需要安装一个程序包：`hdfs`

```python
#1.pip 安装hdfs模块 
pip install hdfs
#2.获得HDFS 连接
from hdfs import Client
client = Client("http://192.168.19.10:50070") #连接namenode
```
> **API操作**
>
> **注意需要在windows的hosts文件中定义映射**
>
> **192.168.5.9      hadoop1**
>
>   **虚拟机ip       虚拟机主机名**

```python
#文件清单
client.list("/"): # hdfs dfs -ls /
client.walk("/"): # hdfs dfs -ls -R /

#文件上传，但是需要注意  修改hdfs访问权限
#将当前目录下的test.txt 上传到hdfs的 /zhj/test.txt
client.upload("/zhj/test.txt","test.txt") #上传不存在的文件
client.upload("/zhj/test.txt","test.txt",overwrite=True) #若文件已存在，会覆盖原文件

#文件下载
client.download("/zhj/test.txt","zhj.txt") #下载到当前目录下
client.download("/zhj/test.txt", "e:/zhj.txt") #下载到E盘

#删除文件
client.delete("/zhj") #删除空目录
client.delete("/b.txt") #删除文件
client.delete("/zhj",True) #删除非空目录

#新建目录
client.makedirs("/zhj/a")

#文件改名，改路径
client.rename("/zhj/test.txt","/zhj/test2.txt") #重命名
client.rename("/zhj/test.txt", "/zz/test.txt")  # 移动位置

#读取文件
with client.read("/zhj/test.txt") as reader:
    for line in reader:
        print(line)
```

## 四、HDFS集群

### 1. 准备多台机器

> #### 克隆即可，有3台即可。

### 2. ssh 免密码登录

​     ![1537253558502](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537253558502.png)

#### 2.1 如何生成公私钥对

```markdown
linux中执行：ssh-keygen -t rsa
在目录：~/.ssh 中：
	id_rsa  ==私钥文件
	id_rsa.pub  ==公钥文件
```

#### 2.2 如何把公钥发送远端主机

```markdown
执行：
    yum -y install openssh-clients
    ssh-copy-id root@ip (ssh-copy-id 用户@主机)
则，会在 ~/.ssh目录中会出现 authorized_keys 文件
```
### 3. HDFS集群的搭建

#### 3.1 准备

```markdown
1. 网络设置
      为多台主机 设置ip地址、关闭防火墙、设置主机名、设置hosts文件
      每台主机的hosts中要映射所有主机的【ip和主机号】
2. 安装jdk并设置环境变量
3. 进行ssh免密码登录
4. 保证所有节点 下载并解压缩相同hadoop版本
```
#### 3.2 修改hadoop的配置文件

```markdown
如果克隆机的母机器中已经改好，且母机器就是namenode的话，就不用修改如下文件
1. hadoop-env.sh 不用修改
2. core-site.xml 不用修改 其中已经配置了哪个主机是namenode
   【主从都需要知道谁是namenode，不过只有主需要知道谁是从--只有namenode需要改slaves文件】
   (所有从机必须配置core-site.xml中的master的host，因为从机要连接master，做汇报)
   (所以其实主要每个机器知道谁是主机，然后把主机的namenode和各从机的datanode开启，集群就搭好啦)
   (主机有个slaves文件，要配置所有从机的host，目的是声明从机，可以在主机上一下把所有节点都启动起来)
   (./sbin/start-dfs.sh 会遍历slaves的host，把每个从机的datanode都启动起来)
3. hdfs-site.xml 副本集个数需要调整  (只在namenode上修改即可)
4. yarn-site.xml 不用修改
5. mapred-site.xml 不用修改
6. 在namenode主机的/opt/install/.../etc/hadoop/slaves中添加如下host：
   (只在namenode上修改即可)
    hadoop2
    hadoop3
    hadoop1
```
### 4. 启动hadoop集群

> **注意，如果之前启动过集群但失败，需要重新启动时，要将 data/tmp目录清空。**

```markdown
1. 格式化 NameNode节点做格式化
 bin/hdfs namenode -format
2. 启动集群 在NameNode节点上执行：
 开启：sbin/start-dfs.sh  (namenode中配置有slaves，会找到所有从节点，并为从节点启动datanode)
 关闭：sbin/stop-dfs.sh
3.集群的各个节点都启动后，每个从节点会在自己的core-site.xml中找到master的位置，并发起连接做汇报。
4. bin/hdfs dfsadmin -report 可以查看集群状态
   http://192.168.5.10:50070 也可以
```
