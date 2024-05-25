from pymongo.mongo_client import MongoClient

# MongoDB连接URI
uri = "mongodb+srv://EstarHsh:Data141592@cluster0.eelcdog.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# 创建新的客户端并连接到服务器
client = MongoClient(uri)

# 尝试发送ping以确认成功连接到MongoDB
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# 选择数据库和集合
# db = client['数据库名']
# collection = db['集合名']

db = client['用户信息']
collection = db['用户数据']

# 插入文档
# doc = {'name': 'John', 'age': 30, 'city': 'New York'}
# collection.insert_one(doc)

# 创建一个包含配置信息的字典
# config = {
#     'config': {
#         'credentials': {
#             'usernames': {
#                 'test': {
#                     'email': 'test@gmail.com',
#                     'name': 'test',
#                     'password': '1234'
#                 },
#                 'admin': {
#                     'email': 'admin***@gmail.com',
#                     'name': '管理员',
#                     'password': '1234'
#                 }
#             }
#         },
#         'cookie': {
#             'name': 'some_cookie_name',
#             'key': 'some_signature_key',
#             'expiry_days': 10
#         },
#         'preauthorized': []
#     }
# }

# 将这个字典插入到MongoDB的集合中
collection.insert_one(config)

# 查询文档
# for doc in collection.find():
#     print(doc)

doc = collection.find_one({'config': {'$exists': True}})
print(doc['config']['credentials'])


# # 更新文档
# collection.update_one({'name': 'John'}, {'$set': {'age': 31}})

# # 删除文档
# collection.delete_one({'config': {'$exists': True}})

# doc = collection.find_one({'config': {'$exists': True}})
# print(doc['config']['credentials'])
