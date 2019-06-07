# Hadoop_Day1

## 一、linux相关的网络操作

> 1. 查看linux IP地址方式

```
ifconfig 
```
> 2. 临时设置服务器的IP

```markdown
ifconfig eth0 192.168.19.10
```

![1537164634419](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537164634419.png)

> 3. 永久设置IP地址

```markdown
vi /etc/sysconfig/network-script/ifcfg-eth0 
```
![1537164634419](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537164634419.png)

> 4. 关闭防火墙

```
servie iptables stop #临时关闭防火墙  当前关闭 
service iptables status #查看防火墙的状态  
chkconfig iptables off #永久关闭防火墙  下一次从新启动时 也是关闭
```
> 5. 修改linux服务器的主机名

```markdown
vi /etc/sysconfig/network
HOSTNAME = hadoop1
#注意：修改完毕后，需要重新启动linux
```
> 6. 修改主机映射

* window

```
C:\Windows\System32\drivers\etc
hosts
192.168.xx.xx hadoop1
```
* linux

```
vi /etc/hosts
192.168.5.9 hadoop1
```
> 7. 克隆机网络设置

```markdown
1. clone机器mac地址 
   rm -rf /etc/udev/rules.d/70-persistence-net.rules
2. 把clone机器  修改静态ip 
   vi /etc/sysconfig/network-script/ifcfg-eth0
   删除两条：uuid和 hwaddr 所在行
3. 修改主机名
   vi /etc/sysconfig/network
4. 修改hosts文件
   vi /etc/hosts
```
> 8. 集群中文件的复制

```markdown
scp 本机文件名字 root@ip:/新机器的位置
scp /etc/hosts root@192.168.19.11:/etc    #传送文件
scp -r /etc/文件夹 root@192.168.19.11:/etc    #传送文件夹
```
## 二、Linux操作系统安装软件

> 1. rpm (红帽子)

```markdown
rpm -ivh xxxx.rpm
rpm -qa #查询所有已经安装的软件
rpm -e 软件包名  #写在某软件
```
> 2. yum (红帽子)

```markdown
不需要安装依赖
yum -y install xxxx
yum -y install mysql-server

yum安装的提速
设置yum源 
1. mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
2. 下载CentOS6-Base-163.repo【资料】 上传 /etc/yum.repos.d/
3. yum clean all
   yum makecache
```
> 3. tar直接解压缩

```markdown
tar -zxvf xxxx.tar.gz
```
> 4. 源码编译安装

```markdown
1. 解压缩tar
tar -zxvf xxx.tar.gz
2. ./configure [可省略]
3. make xxxx
4. make install xxxx
```
## 三、大数据技术

> hadoop=分布式的文件系统

### 1. 什么是大数据

> 数据量级很大的应用处理。TB级 ，日数据增长GB级 

```
K -- M---- G ---- T ----PB  ---- EB  ---ZB  1024
```
> 大数据的特点 4V

```
1. Volume (大量) 
   数据量很大，至少是TB或者日均增加GB级
2. Variety (多样) 
   结构化数据
         数据库中的数据 
   半结构化数据
          JSON  
          XML  
   非结构化数据
         音频
         视频
3. Velocity（快速） 
   处理数据 快
4. Value （价值） 
   海量没有价值的数据中，分析出有价值的内容
```

### 2. 大数据处理过程中涉及的问题

#### 2.1 怎么存

 ![hadoop基本结构](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/hadoop基本结构.png)

#### 2.2 怎么运算（处理）

​       ![1537172748203](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hadoop/png/1537172748203.png)

#### 2.3 大数据技术方案（Hadoop）

1. Google 3篇论文   GFS    MapReduce   BigTable 
2. Doug Cutting 写 Hadoop 
   HDFS --- GFS
   MapReduce ---- MapReduce
   HBase  ---- BigTable 
3. Hadoop 贡献 Apache组织
4. Hadoop 版本
   1. apache组织的 开源版  互联网 
   2. cloudera CDH
      雇佣 Doug Cutting  4000美金
   3. Hortonworks
      最初apache组织 hadoop的开发人员 创立公司 12000美元 （10个节点）

### 3. 搭建Hadoop的伪分布式集群

#### 1.准备工作

```
设置ip、关闭防火墙、设置主机名、设置主机名和ip的映射
```

#### 2.安装jdk

> hadoop是用java语言写的，所以需要安装java的运行环境

```markdown
1. 官方网站下载JDK安装版
   RPM
2. 减压java包
	rpm -ive xxxx.rpm
3. 默认安装目录
   /usr/java/jdk1.7.0_71
4. 配置jdk环境变量
   vi /etc/profile
	export JAVA_HOME=/usr/java/jdk1.7.0_71
	export CLASSPATH=.
	export PATH=$JAVA_HOME/bin:$PATH:$HOME/bin
5. source /etc/profile  #是文件修改生效
6. java -version 验证安装是否成功
```
#### 3.安装hadoop

> 3.1 安装hadoop

```sh
获得hadoop安装包，并解压缩
#/opt/module  放置所有需要的相关软件
#/opt/install 安装相关软件
tar -zxvf hadoopxxxx.tar.gz -C  /opt/install   #解压到/opt/install 目录中
```

#### 4.配置hadoop相关配置文件

 ```sh
#1.在HADOOP_HOME/etc/hadoop/hadoop-env.sh 文件
export JAVA_HOME=/usr/java/jdk1.7.0_71
 ```

```xml
<!--2. 在HADOOP_HOME/etc/hadoop/core-site.xml 文件 
       8020也可以写其他端口
-->
<property>		
    <name>fs.default.name</name>
    <value>hdfs://hadoop1:8020</value>  <!-- hadoop1映射了本机的ip -->
</property>
<property>
    <name>hadoop.tmp.dir</name>
    <value>/opt/install/hadoop-2.5.2/data/tmp</value>
</property>
```
```xml
<!--3. 在HADOOP_HOME/etc/hadoop/hdfs-site.xml中 
       datanode中存储的数据块要存几份
       1=没有副本
       2=每个块都存2份
-->
<property>
    <name>dfs.replication</name>
    <value>1</value>
</property>
```
```xml
<!--4. 在HADOOP_HOME/etc/hadoop/yarn-site.xml中 -->
<property>
       <name>yarn.nodemanager.aux-services</name>
       <value>mapreduce_shuffle</value>
</property>
```
```xml
<!-- 先复制：cp mapred-site.xml.template mapred-site.xml -->
<!--5. 在HADOOP_HOME/etc/hadoop/mapred-site.xml 中-->
<property>	 	        		
	<name>mapreduce.framework.name</name>
    <value>yarn</value>
</property>
```
#### 5.启动hadoop的伪分布式集群

```markdown
1. 格式化Hadoop集群 第一次启动hadoop集群时 需要做
   bin/hdfs namenode -format
2. 启动相关进程
   sbin/hadoop-daemon.sh start namenode
   sbin/hadoop-daemon.sh start datanode
   sbin/yarn-daemon.sh start resourcemanager
   sbin/yarn-daemon.sh start nodemanager
 3. 执行：【jps】 查看所有java进程
 4. 通过网络访问
    HDFS   http://ip:50070 访问namenode
    yarn   http://ip:8088  访问resourcemanager
```
