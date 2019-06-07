# Hive_Day2

## 一、hive中的表

### 1.管理表【重点】

1. 基本语法

   ```sql
   create table if not exists table_name(
   id int,
   name string
   )row format delimited fields terminated by '\t'
   ```

2. 指定表的路径【重点】

   ```sql
   #如果不想表在默认位置，而是想自定义表的位置
   #如果已有某个目录，可以为目录映射一张表,目录中的所有文件自然成为表的内容
   create table if not exists table_name(
   id int,
   name string
   )row format delimited fields terminated by '\t' location 'hdfs_path'
   ```

3. as关键字创建表

   ```sql
   # 把as 关键字后的查询内容，作为新表的表结构，并且填充查询结果的数据为新表数据
   create table if not exists t_user_as as select name from t_user;
   ```

4. like关键字创建表

   ```sql
   #新表的表结构 和 like关键字 后面的表一致，但不会copy数据
   create table if not exists stu_like like student
   ```

【describe formatted 表名  

​    desc formatted 表名

​    可以看到表的类型】

### 2.外部表【重点】

```sql
create external table if not exists t_user_ex(
id int,
name string
)row format delimited fields terminated by '\t';
注意：和管理表一样，as和like同样适用。导入数据同样。指定目录一样。
```

1. 管理表语外部表的区别

   ```markdown
   1. hive删除管理表，同时删除管理表在hdfs上所对应的路径，及其文件
   2. hive删除外部表，不会删除hdfs上对应的路径及其文件，删除的是metastroe
   ```

2. 管理表与外部表应用场景

   **管理员==>管理表**

   **普通用户==>外部表**

   【为管理员创建管理表；为客户只能建立外部表，是的即使客户删除了表，数据也还是安全的】

### 3.分区表 Partition【重点】

作用：查询优化

> hive表  ：  user1.txt     user2.txt    user3.txt
>
> user1.txt：1    a     18
>
> ​                    2    b     18
>
> user2.txt :   3   c      19
>
> ​                    4     d     19
>
> hql: select id,name,age from hive表  where age=18
>
> 一个表下 会映射多个文件，在做查询时，如果查询结果只来自某一个文件，运行过程中也依然会从所有文件中查询一遍，效率差。
>
> 实例：每小时一个日志文件
>
> 可以做一个分区表：分区的标志是【年-月-日】，则可以每天一个分区
>
> ​                                   分区的标识是【年月日 时分秒】，则可以每小时一个分区
>
> 则所有的日志都在一张表中，但是做了分区标识；则既可以汇总查询，又可以分区查询

```sh
#创建分区表：
create table t_user_part3(
    id int,
    name string
)partitioned by (abc string) row format delimited fields terminated by '\t';
#注意abc是随意的一个命名，其会成为t_user_part3中的一个列，列类型是string (通过desc可见)
#表中导入数据，并设置分区命名，如此则一张表的多个内容被分区标识
load data local inpath '/root/data' into table t_user_part partition (abc='07');
load data local inpath '/root/data' into table t_user_part partition (abc='06');
#则可以进行如下查询：【既可分区查，又可汇总查】
select xxx from t_user_part where abc='07';#只会从07分区的文件中查找
select xxx from t_user_part where abc='06';#只会从06分区的文件中查找
select xxx from t_user_part;#从表的所有文件中查找
```
> 如下表中定义两个分区列

   ```sql
create table user2(
    id int,
    name string
)partitioned by (day string,hour string) row format delimited fields terminated by '\t';

day               hour
2018-12-12        2018-12-12 15


【load data local inpath '/root/user.txt' into table user2 
 partition(day='2019-01-03',hour='2019-01-03 22');】
【load data local inpath '/root/user2.txt' into table user2 
  partition(day='2019-01-03',hour='2019-01-03 23');】

select * from user2 where day='2019-01-03'; #查询某天分区
select * from user2 where hour='2019-01-03 22'; #查询某小时分区
   ```

### 4. 桶表、临时表(略)

### 5.表的删除

   ```sql
#表删除 数据删除
drop table table_name
#表保留 数据删除
truncate table table_name 
   ```

## 二、Hive表导入和导出数据

### 1.导入

1. 本地数据的导入【重点】

   ```markdown
   load data local inpath 'local_path' into table table_name
   load data local inpath 'local_path' into table table_name partition (分区列='xx')
   ```

2. HDFS输入导入 【用的较少】

   ```markdown
   #本质 文件在hdfs 移动
   load data inpath 'hdfs_path' into table table_name
   ```

3. overwrite

   ```markdown
   #默认导入数据，会在当前目录中追加相应的数据文件
   #加入overwrite,会覆盖掉目录中的所有内容
   #本质就是先删除原有内容，在进行导入
   load data [local] inpath 'hdfs_path' overwrite into table t_user
   ```

4. as 方式

   ```markdown
   create table t_user_as as select name from t_user;
   # 根据as后面的查询 建表
   # 根据查询结果 导入数据
   ```

5. insert方式 【重点】

   ```markdown
   t_user  分区表
   id  name  part1  part2
   1   zzz    1     10
   2   aaa    1     11
   3   bbb    2     10
   
   t_user2  普通表
   id  name  day  hour 
   1   zzz    1   10
   2   aaa    1   11
   3   bbb    2   10
   
   insert into table t_user  select id,name from t_user2;
   #为分区表插入数据(静态分区)
   insert into table t_user partition (part1='xx',part2='xxx') \
   select id,name from t_user2;#静态分区的查询中，不用包括分区列的值
   
   #为分区表插入数据(动态分区)set hive.exec.dynamic.partition.mode=momstrict;
   insert into table t_user partition(part1,part2) \
   select id,name,day,hour from t_user2; #动态分区的查询中，要包含分区列的值
   
   #insert只负责根据查询结果，导入数据【插入数据】，不负责建表
   ```

6. location 【重点】

   ```markdown
   # hdfs 已有一个目录
   # 在目录之上 套一张表
   create table t_user_hdfs_location(
   id int,
   name string
   )row format delimited fields terminated by '\t' location '/hdfs_path';
   ```

### 2.hive表中导出数据

1. insert方式【重点】

   ```markdown
   # hive 自动运行mr 把查询结果 生成一个文件 0000_0 导出到本地路径下
   # 本地目录可以不存在
   insert overwrite local directory '/root/xiaohei' select name from t_user; 
   
   # hive 自动运行mr 把查询结果 生成一个文件 0000_0 导出到hdfs路径下
   # hdfs目录必须已存在
   insert overwrite directory '/root/xiaohei' select name from t_user; 
   ```

2. 在Linux的命令行使用hive的-e -f参数，将输出重定向保存到本地文件 【了解】

   ```markdown
   bin/hive --database 'baizhi129' -f /localpath/hive.sql > /localpath
   ```

3. sqoop方式【重点】

   ```markdown
   sqoop hadoop专门提供的一种工具
   作用：  HDFS/Hive表  <--->  RDB(关系型数据库)
   扩展：  
   HDFS/Hive表  <--->  RDB(关系型数据库) <---> django-Model <--->（view,template,浏览器）
   ```

4. Hive导入 导出命令【了解】

   ```markdown
   1. export 导出
   	export table tb_name to 'hdfs_path'
   2. import 导入
   	import table tb_name from 'hdfs_path'
   ```

## 三、hive优化

> Hive中与MapReduce相关的参数设置

```markdown
hive-site.xml
<property>
	  <name>hive.exec.reducers.bytes.per.reducer</name>
	  <value>1000000000</value>
	  <!-- 每个reduce可以处理的字节数：1G -->
</property>
<property>
     <name>hive.exec.reducers.max</name>
     <value>999</value>
     <!-- 1个job，最多可以开启的reduceTask的个数 -->
</property>
<!-- map的细节hive无法干预，map个数==文件的block个数 -->
```

```xml
mapred-site.xml
<property>
     <name>mapreduce.job.reduces</name>
     <value>1</value>
</property>
```



> Hive中特殊参数设置

```markdown
hive-site.xml
<property>
  <name>hive.fetch.task.conversion</name>
  <value>minimal</value>
  <description>
    1. minimal : SELECT STAR, FILTER on partition columns, LIMIT only
    2. more    : SELECT, FILTER, LIMIT only (TABLESAMPLE, virtual columns)
  </description>
</property>
```

> Hive服务发布【了解】

目的为了让其他编程语言开发的程序访问hive

1. hiveserver2

```markdown
bin/hiveserver2  #启动服务
```

2. 客户端（c++ python) beeline

``` mark
1. bin/beeline -u jdbc:hive2://hadoop.baizhiedu.com:10000 -n root -p 123456

2. python
3. c++
```

> 意义不大，一般不用用python、java去直接访问hive，而是会用sqoop将hive数据导入mysql，然后python、java去访问mysql，这样更直接，速度更快。

