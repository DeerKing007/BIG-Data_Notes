import happybase

connection = happybase.Connection(host='192.168.248.135',port=9090)#thrift服务端口：9090
connection.open()

# # 建表
# families = {
#     "fie1":dict(),
#     "fie2":{"max_versions":3}
# }
# connection.create_table('ai145:t_user',families)
#
# # 删除表
# connection.delete_table('ai145:t_user',disable=True)

# 插入一个数据
table = connection.table('ai145:t_user') #获取表对象
# table.put("001",{"fie1:name":"suns"})
# table.put('001',{'fie1:age':'18'})
# table.put('002',{'fie2:name':'lishi'})
# print(table.row('001'))
# print(table.scan())
print(list(table.scan()))


