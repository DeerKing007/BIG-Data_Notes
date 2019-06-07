# Hive_Day1

## 一、Hive引言

> apache的顶级项目(hive.apache.org)，基于hadoop的数据仓库处理，底层应用MapReduce. facebook 开源的项目。
>
> 数据库：数据量小(单表千万条)，核心数据，应对的是日常的业务交互，注册一个用户，增加一个订单.
>
> 数据仓库：数据量非常大，非核心数据，单条数据价值不大；用于数据分析。

## 二、Hive的核心实现思路

```markdown
Hive 把HQL语句 通过MetaStore找到表和文件的映射关系后，将hql语句转换为MapReduce任务进行运行
HQL==Hive Query Language，类似sql
```

![1534385788963](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hive/png/1534385788963.png)

 ![hive_思路](https://github.com/DeerKing007/BIG-Data_Notes/blob/master/Hive/png/hive_思路.png)



> Hive 别名 SQL On  Hadoop
> presto
> impala
> sql on spark  = sparkSQL

## 三、Hive的安装

```markdown
1. 启动Hadoop相关进程 namenode datanode resourcemanager nodemanager
2. 获取Hive的安装tar包 hive.apache.org
3. 解压缩:tar -zxvf xxxx.tar.gz -C /opt/install
4. 修改hive的配置文件 hive-env.sh (需要从hive-evn.sh.template复制)
HADOOP_HOME=/opt/install/hadoop-2.5.2 (hadoop的安装目录)
export HIVE_CONF_DIR=/opt/install/apache-hive-0.13.1-bin/conf (配置文件所在目录)
5. 启动hive
执行：bin/hive  (会有一个runJar进程)
```

## 四、Hive的基本命令

### 1. 数据库操作

> 数据库：每个数据库实际是HDFS  上的一个目录
>
> 默认是在/user/hive/warehouse/下的某个目录

#### 1.1 创建数据库

```sh
create database [if not exists] 数据库名
```

#### 1.2 显示所有数据库

```
show databases
#默认数据库  default 
```

#### 1.3 切换数据库

```
use 数据库名
```

#### 1.4 显示库名 (可选)

> hive-site.xml 
>
> 通过hive-default.xml.template复制即可
>
> 原有的所有配置全部删除，只留自己配置信息

```xml
<!--在文件中只需保留如下信息:-->
<property>
    <name>hive.cli.print.current.db</name>
    <value>true</value>
</property>
```

### 2. 表操作

> 对应一个HDFS上面的目录
>
> 数据库目录下的一个目录

#### 2.1 建表

```mysql
create table if not exists t_user(
	id int,
	name string
)row format delimited fields terminated by '\t';
```

#### 2.2 查看表信息

```sh
describe t_user; #简略表信息
describe extended t_user;  #详细表信息
describe formatted t_user; #详细表信息(格式更规矩)
#describe 可简写成 desc
```

#### 2.3 删除表

```sh
drop table 表名  #删除表
```

#### 2.4 显示库下所有表

```markdown
show tables
```

#### 2.5 Hive表的数据导入  

> 本质：把对应的数据文件 放置到表中的目录中
>
> 表中的数据，本质上是这个表目录中 所有文件的数据。

```markdown
load data local inpath '本地路径' into table t_user;
load data inpath 'hdfs路径' into table t_user;(注意会将文件移动到表格所映射的目录下)
```

> 可向一个表，导入多个文件，在对表进行查询时，会查询所有文件；
>
> 而且如果多个文件有同名会自动改名；
>
> 导入的多个文件的内容总和==表的内容.

#### 2.6 查询

```markdown
1. 查询数据
	select * from t_user;
	select id from t_user;
2. select * from t_user;  不会启动MR
3. select id from t_user; 启动MR 但是因为没有汇总，所有只有Map没有reduce
4. where条件查询
   =  >  <  >= <=  !=
   between .. and 
   in  
   is null  is not null
5. 聚合函数 count sum avg max min
	select count(*) from t_user
6. group by  having
	select max(id) from t_emp group by deptno;
7. 分页  limit
	hive  select * from t_user limit 2  前2条 (不能是 limit 1,3 只能有一个参数)
8. 消除重复 distinct   【select distinct name from xxx;】
9. 多表连接  join
   inner join
   left [outer] join
   right [outer] join
   full join
select e.name,e.salary,d.name
from t_emp e
inner join t_dept d
on e.deptno = d.id;
10. 查询结果中显示表头
hive-site.xml
<property>
	  <name>hive.cli.print.header</name>
	  <value>true</value>
</property>
```

## 五、 修改默认的MetaStore

```markdown
1. matestore的作用：用于存储 Hive表 与 HDFS 目录/文件 对应关系的
2. metastore存储在关系型数据库中。  默认 derby数据库  java内置数据库，极小型数据库
3. derby作为metastore 最大问题：只能允许 一个 终端访问
```

### 1. 安装mysql

```markdown
1. 安装MySQL
yum -y install mysql-server
service mysqld start  启动 mysql 服务
chkconfig mysqld on   自启动mysql
/usr/bin/mysqladmin -u root password '123456' 修改管理员密码
进入mysql
mysql -uroot -p123456
2. 打开MySQL远程访问
use mysql
grant all privileges  on *.* to root@'%' identified by "123456";
flush privileges;
```

### 2. mysq驱动

> 上传 mysql-connector
>
> 将mysql-connector-java-5.1.27-bin.jar 复制 hive_home/lib
>
> 使得hive可以连接mysql，进而最终促成metastore从derby到mysql的转换

### 3. hive设置

> **把默认的derby数据库 替换成 MySQL**

```xml
<!-- hive-site.xml -->
<!-- mysql连接的url，连接地址 -->
<property>
	  <name>javax.jdo.option.ConnectionURL</name>
	  <value>jdbc:mysql://hadoop1:3306/metastore?
             createDatabaseIfNotExist=true</value>
</property>
<!-- mysql的java驱动类 -->
<property>
	   <name>javax.jdo.option.ConnectionDriverName</name>
	   <value>com.mysql.jdbc.Driver</value>
</property>
<property>
	  <name>javax.jdo.option.ConnectionUserName</name>
	  <value>root</value>
</property>
<property>
	  <name>javax.jdo.option.ConnectionPassword</name>
	  <value>123456</value>
</property>
```

### 4.  重启hive

> 会在mysql中建立 metastore库，其中好多表用于存储 hive表和 hdfs文件间中的映射

## 六、细节

### 1. shell 补充

```markdown
1. bin/hive 基本启动hive的方式
2. bin/hive -help 查看hive的帮助信息
3. 指定启动的数据库  bin/hive --database baizhi125
4. 启动hive的时候，可以直接执行 相关命令  bin/hive -e 'show databases'
5. -e 启动hive时 执行命令  bin/hive --database baizhi125  -e 'show tables'  
   将结果输出到指定文件中： bin/hive -e 'show databases' > localpath (覆盖文件内容)
   将结果输出到指定文件中： bin/hive -e 'show databases' >> localpath (追加文件内容)
6. -f 启动hive时，直接执行sql命令 bin/hive -f /opt/datas/hive.sql
bin/hive --database baizhi125 -f /root/hive.sql > localpath  (会覆盖文件内容)
bin/hive --database baizhi125 -f /root/hive.sql >> localpath  (会在文件中追加)
```

### 2. hive中的配置信息

```markdown
1. hive> set hive.cli.print.current.db 获取
   hive> set hive.cli.print.current.db=true 设置
2. hive-site.xml 【推荐】【自己定义hive-site.xml，在其中可以选择覆写某些默认配置】
3. hive-default.xml.tmplate【hive的所有的 默认的 配置】
```



