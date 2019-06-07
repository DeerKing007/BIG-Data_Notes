# Sqoop

```
hdfs(mapred)====hive(映射+hql=mr)<==sqoop==>rdb(mysql,oracel,ss)==python-web
sqoop核心价值：hdfs/hive 和 rdb之间交换数据 (工具)
```

## 一 、Sqoop安装

```markdown
1. 解压缩Sqoop
2. 修改配置 sqoop_home/conf
   修改conf/sqoop-env.sh
   export HADOOP_COMMON_HOME=/opt/install/hadoop-xxx
   export HADOOP_MAPRED_HOME=/opt/install/hadoop-xxx
   export HIVE_HOME=/opt/install/hive-0.13.1-xxx
3. 将MySQL的java驱动：mysql-connect-xxx.jar copy sqoop_home/lib
4. 测试sqoop是否正常使用（测试连接mysql）
   bin/sqoop list-databases -connect jdbc:mysql://hadoop1:3306 -username root -password 123456
```
## 二、Sqoop相关命令

### 1. 准备工作 

```sql
# mysql 创建数据库 创建表
create database db145;

create table t_user(
id int primary key,
name varchar(12)
)engine=innodb default charset=utf8;

insert into t_user values (1,'zzz1');
insert into t_user values (2,'zzz2');
insert into t_user values (3,'zzz3');
insert into t_user values (4,'zzz4');
insert into t_user values (5,'zzz5');
insert into t_user values (6,'zzz6');
insert into t_user values (7,'zzz7');
insert into t_user values (8,'zzz8');
insert into t_user values (9,'zzz6');
insert into t_user values (10,'zzz7');
insert into t_user values (11,'zzz8');
```
### 2. 基本的语法形式

```sh
#第一种写法
bin/sqoop list-databases -connect jdbc:mysql://hadoop1:3306 -username root -password 123456

#第二种写法
bin/sqoop list-databases \
--connect \
jdbc:mysql://hadoop1:3306 \
--username root \
--password 123456
```

### 3. 数据导入

> **(MySQL数据导入HDFS/Hive)**

#### 3.1 基本导入方式

> 数据默认导入到   hdfs:/user/root/t_user   【ops : t_user==表名】
>
> sqoop导入数据，底层应用的都是MapReduce,没有reduce

```sh
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user

#将mysql的db145中的t_user表的数据导入hdfs
```
#### 3.2 制定hdfs导入的目录

> **【注意：导入的目录，必须不能存在，会被自动创建】**

```sh
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--target-dir /sqoop
```
#### 3.3 删除已经存在的hdfs目录

> 如果目录已经存在则删除目录，然后重新创建

```sh
#--delete-target-dir 
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--target-dir /sqoop \
--delete-target-dir 
```
#### 3.4 指定Sqoop中Map的个数

> 默认map个数：4个(ops：数据行数>=4)
>
> ​                            (ops：数据行数<4，则每行启动一个map)
>
> (ops : cdh版的sqoop默认是有多少行数据，就有多少个map)

```sh
#--num-mappers 1
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--target-dir /sqoop \
--delete-target-dir \
--num-mappers 1
```
#### 3.5 设置导入数据，列的分隔符

> 导入后，hdfs文件中每列的内容是用逗号分隔的
>
> 1,zzz1
> 3,zzz3
> 2,zzz2
>
> 可以改成制表符

```sh
#--fields-terminated-by '\t'
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--target-dir /sqoop \
--delete-target-dir \
--num-mappers 1 \
--fields-terminated-by '\t'
```
#### 3.6 快速导入

```markdown
# --direct
# 底层通过 mysql dump操作==批量导数据 (批处理)
# mysql数据库 必须和 sqoop 放置在同一个机器 才可以使用快速导入
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--target-dir /sqoop \
--delete-target-dir \
--num-mappers 1 \
--fields-terminated-by '\t' \
--direct
```
#### 3.7 增量导入

> 数据导入时，目录不能存在，或者要强制删除已存在的目录。
>
> **如果希望：多次导入数据到一个hdfs目录中，不断追加内容：**

```sh
t_user                    hdfs:/xx
1   a
2   b
3   c
4   d

# 增量导入
--check-column <column>        根据哪列判断是否是新数据    id
--last-value <value>           id列上上次更新到的值   2
--incremental <import-type>    增长方式     append
```

```markdown
# 一定不要加入 --delete-target-dir 不能删除
bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--target-dir /sqoop \
--num-mappers 1 \
--fields-terminated-by '\t' \
--direct \
--check-column id \
--last-value 11 \
--incremental append
```
### 4. 数据导出

> **HDFSexport (HDFS/Hive导出到MySQL数据库)**

#### 4.1 全表导出

> 每次执行，都会将hdfs/hive的所有内容写入到 mysql
>
> 如果导出是定期执行的，还需要其他参数

```markdown
bin/sqoop export \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user145 \
--export-dir /sqoop \
--num-mappers 1 \
--input-fields-terminated-by '\t'  #如果文件中分割是逗号用 '\001' 

【ops：把如上命令中的hdfs目录换成hive表所在目录，就可以对接hive导入导出 (略)】
```
#### 4.2 增量导出

> 每次执行，只将新数据写入到 mysql
>
> --update-key  id  判断是否是新数据的列
> --update-mode allowinsert   插入新数据到mysql表中

```
bin/sqoop export \
--connect \
jdbc:mysql://hadoop:3306/db145 \    #mysql的ip:端口号/数据库
--username root \					#用户
--password 123456 \					#密码
--table t_status \					#目标mysql的表，已经建好的
--export-dir /user/hive/warehouse/db145.db/yhd_status \   #来源路径的表
--num-mappers 1 \					
--input-fields-terminated-by '\t' \
--update-key id \					#通过id判断是否是新数据的列
--update-mode allowinsert			#插入新数据到mysql表中
```



### 5.  Hive Import (补充，了解)

> sqoop有一些专门的命令面向hive导入导出
>
>
>
> 注意：需要从hive的lib中导入一些jar到 sqoop的lib，以满足sqoop的依赖：
>
> cp  hive_home/lib/hive-common-0.13.1.jar   sqoop_home/lib/  【将hive的jar拷贝给sqoop】
>
> cp  hive_home/lib/hive-shims*.jar  sqoop_home/lib/   【将hive的jar拷贝给sqoop】

```sh
#--hive-import \
#--hive-database db145 \
#--hive-table t_user \

bin/sqoop import \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user \
--delete-target-dir \
--hive-import \
--hive-database db145 \
--hive-table t_user \
--num-mappers 1 \
--fields-terminated-by '\t'
```



## 三、脚本化的Sqoop指令

> 把对应的Sqoop命令，存储文件或者作业中，便于日后重复利用

### 1. 把Sqoop命令存在文件

> **存到linux的本地文件中**

```sql
-- 先建表
create table filetomysql(
 id int,
 name varchar(12)
);
```

```markdown
# 创建一个Sqoop文件 == 普通文件 /root/sqoop.file,在文件中定义如下内容：
# 建议为导出逻辑，建立一个新的mysql表
【bin/sqoop==不需要定义】
export
--connect
jdbc:mysql://hadoop1:3306/db145
--username
root
--password
111111
--table
filetomysql
--export-dir
/sqoop
--num-mappers
1
--input-fields-terminated-by
'\t'
```
```sh
# 执行文件 /root/sqoop.file
bin/sqoop --options-file /root/sqoop.file
```



### 2. Sqoop命令存在job中

> sqoop中可以创建job，job中定义命名
>
> 需要在sqoop的lib中导入一个jar：java-json.jar

```markdown
# 创建作业
bin/sqoop job \
--create test_job145 \
-- \
export \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password 123456 \
--table t_user145 \
--export-dir /sqoop \
--num-mappers 1 \
--input-fields-terminated-by '\t' \
--update-key id \
--update-mode allowinsert
```
```sh
# 执行job
bin/sqoop job --exec test_job2   [ops:需要输入 mysql 的密码]
```

> 细节 : 每一次执行job ，都需要输入密码 
>
> ​           不利于自动化处理 所以定密码的存储文件

```sh
# 将linux密码存入一个本地文件中
echo -n "123456"  >> /root/pwd
```

```sh
# 创建作业时，关联密码文件 ，如此job在执行时，不再需要输入密码
bin/sqoop job \
--create test_job146 \
-- \
export \
--connect \
jdbc:mysql://hadoop1:3306/db145 \
--username root \
--password-file file:///root/pwd \
--table t_static \
--export-dir /user/hive/warehouse/source.db/yhd_statistics \
--num-mappers 1 \
--input-fields-terminated-by '\t' \
--update-key id \
--update-mode allowinsert
```

## 四、定时处理

```markdown
1. 安装crontab 
 yum -y install crontab
2. 执行： crontab -e 
【crontab -e 会进入编辑界面，定义cron表达式，以及相应的任务
  表达式组成：minute   hour   day   month   week   command 】

*/5 * * * * command
*/1 * * * * echo 'zzz' >> /root/abc
*/1 * * * * /opt/install/sqoop-1.4.7-xxx5.3.6/bin/sqoop job --exec test_job2

3. 启动关闭服务
service crond start
service crond stop
```


