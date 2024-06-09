import json
import requests
import time  # 导入 time 模块

url = "http://127.0.0.1:8190/taskflow/uie"

headers = {"Content-Type": "application/json"}
texts = [
    "姓名：陈梦|电话号码：13812345678|邮箱：chenmeng@outlook.com|专业：信息系统|学历：本科|技能：精通系统分析和设计，熟悉SQL及数据库应用开发，曾在电信行业内部署和优化企业级信息系统|个人素质：具有良好的逻辑思维能力和项目管理经验，能够迅速适应新环境并解决复杂问题|个人经历：毕业于西安电子科技大学信息系统专业，曾为系内多个研究项目编写和维护代码，参与校内软件开发竞赛并获奖|个人性格：细致入微，决策力强，具备良好的沟通和协调能力。"
]

data = {"data": {"text": texts}}

# 记录请求发送前的时间
start_time = time.time()

# 发送 POST 请求
r = requests.post(url=url, headers=headers, data=json.dumps(data))

# 记录请求完成时的时间
end_time = time.time()

# 计算请求处理时间
elapsed_time = end_time - start_time

# 解析响应数据
datas = json.loads(r.text)

# 打印响应数据和处理时间
print(datas)
print(f"请求处理时间: {elapsed_time:.2f} 秒")
