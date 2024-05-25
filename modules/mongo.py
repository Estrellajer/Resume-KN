import streamlit as st
from pymongo.mongo_client import MongoClient

@st.cache_resource
def connect_to_mongo(uri):
    # 创建新的客户端并连接到服务器
    client = MongoClient(uri)
    return client

def get_collection(client):
    # 选择数据库和集合
    db = client['用户信息']
    collection = db['用户数据']
    return collection

def insert_document(collection, doc):
    # 插入文档
    collection.insert_one(doc)

def find_document(collection, query):
    # 查询文档
    return collection.find_one(query)

def replace_document(collection, query, new_document):
    # 替换文档
    collection.replace_one(query, new_document)

def delete_document(collection, query):
    # 删除文档
    collection.delete_one(query)