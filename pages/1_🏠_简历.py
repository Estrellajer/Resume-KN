# Title: 简历解析
# Order: 1

import streamlit as st
import base64
import requests
import json
import difflib
from py2neo import Graph
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
import time
level_keywords = {
    "精通": 4,
    "熟练": 3,
    "熟悉": 2,
    "了解": 1,
}
education_keywords = {
    "博士": 4,
    "硕士": 3,
    "本科": 2,
    "大专": 1, 
}
# 定义技能和个人素质列表
skills_list = [
    "HTML5", "JavaScript", "CSS3", "Vue", "Python", "JAVA", "React", "PHP", "C++", "C语言",
    "uni-app", "jQuery", "Angular", "Bootstrap", "Node.js", "Express", "Vue.js",
    "Git", "Webpack", "MySQL", "Oracle", "SQL Server", "Linux", "Windows", "Android",
     "CAD绘图", "系统集成", "电路设计", "BIM技术", "ERP系统","控制系统", "电子信息", "通信协议", "智能化", "机器人技术", "控制算法",
    "网络设备", "网络安全", "防火墙", "TCP/IP", "OSPF", "BGP", "VPN", "交换机", "路由器", "网络系统", "网络通信",
    "软件测试", "测试计划", "测试报告", "单元测试", "功能测试", "测试用例", "软件工程", "设计模式", "架构设计", "面向对象设计", "软件开发", "系统维护", "项目管理", "API开发",
    "数据分析", "数据结构", "数据库管理", "信息化", "信息安全", "信息系统", "数据中心", "图像处理", "音视频处理"
]

qualities_list = [
    "表达能力", "PPT制作", "售后服务", "技术支持", "方案设计", 
    "责任心", "上进心", "逻辑思维", "实践经验", "团队精神", "吃苦耐劳", "认真负责", "解决问题", "主动性","积极性", "沟通","语言表达"
]

def parse_resume(fname):
    # 读取文件内容
    cont = open(fname, 'rb').read()
    base_cont = base64.b64encode(cont).decode('utf8')  # python3
        
    # 构造json请求
    data = {
            'file_name': fname,         # 简历文件名（需包含正确的后缀名）
            'file_cont': base_cont,     # 简历内容（base64编码的简历内容）
            'need_avatar': 0,            # 是否需要提取头像图片
            'ocr_type': 1,                 # 1为高级ocr
            }
    
    appcode = '590aa3d7dff14b6f832bb0b4b5edaf07'
    headers = {'Authorization': 'APPCODE ' + appcode,
               'Content-Type': 'application/json; charset=UTF-8',
               }
    # 发送请求
    data_js = json.dumps(data)
    url = 'http://resumesdk.market.alicloudapi.com/ResumeParser'
    res = requests.post(url=url, data=data_js, headers=headers)
    
    # 解析结果
    res_js = json.loads(res.text)
    return res_js

def find_closest_skill(skill_name, skills_list):
    matches = difflib.get_close_matches(skill_name, skills_list, n=1, cutoff=0.5)
    return matches[0] if matches else None

def process_resume_data(resume_data):
    # 提取基本信息
    basic_info = {
        'name': resume_data['result']['name'],
        'email': resume_data['result']['email'],
        'phone': resume_data['result']['phone'],
        'major': resume_data['result']['major'],
        'degree': education_keywords.get(resume_data['result']['degree'], 0),  # 使用转换后的学历等级
        'skills': resume_data['result']['skills_objs'],
        'quality': resume_data['result']['cont_my_desc']
    }
    # 过滤技能
    
    basic_info['quality'] = sum(basic_info['quality'].count(quality) for quality in qualities_list)

    # 简化技能列表：提取技能名和转换等级
    skills = {}
    for skill in basic_info['skills']:
        closest_skill = find_closest_skill(skill['skills_name'], skills_list)
        if closest_skill:
            skill_level = skill.get('skills_level', '了解')  # 默认等级为了解
            skill_level_value = level_keywords.get(skill_level, 1)
            if closest_skill not in skills or skill_level_value > skills[closest_skill]:
                skills[closest_skill] = skill_level_value  # 使用技能等级的数值，而不是等级关键词
                
    basic_info['skills'] = skills  # 更新技能列表为简化后的字典

    
    # 返回处理结果
    return {
        'basic_info': basic_info,
        # 'evaluation': evaluation,
        # 'recommended_positions': recommended_positions
    }
def app():
    st.title('简历上传')
    uploaded_file = st.file_uploader("选择你的简历", type=['docx', 'pdf'])

    # 检查是否有存储的简历数据
    resume_data = st.session_state.get('resume_data')

    if uploaded_file is not None or resume_data is not None:  # 如果上传了新的简历文件或者之前已经解析过简历
        if uploaded_file is not None:  # 如果上传了新的简历文件
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                file_extension = ".pdf"
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_extension = ".docx"
            else:
                st.error("不支持的文件类型")

            file_name = "resume" + file_extension
            with open(file_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            resume_data = parse_resume(file_name)
            resume_data = process_resume_data(resume_data)

            # 将解析结果存储在 session_state 中
            st.session_state.resume_data = resume_data

        # time.sleep(5)

        # 展示简历数据
        flat_resume_data = {**resume_data['basic_info'], **resume_data['basic_info']['skills']}
        del flat_resume_data['skills']
        reverse_education_keywords = {v: k for k, v in education_keywords.items()}
        flat_resume_data['degree'] = reverse_education_keywords[flat_resume_data['degree']]

        st.subheader("简历数据")
        df_resume = pd.DataFrame(flat_resume_data, index=[0])
        st.dataframe(df_resume)
    else:
        st.write("请上传简历文件。")

if __name__ == "__main__":
    if "username" in st.session_state:
        user_info = st.session_state.username
        # 显示主页
        st.sidebar.success(f"欢迎用户 {user_info}")

    if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
        st.sidebar.page_link("app.py", label=":red[首页]", icon="🏠")
        st.sidebar.page_link("pages/1_🏠_简历.py", label=":violet[简历上传]", icon="📑")
        st.sidebar.page_link("pages/2_🔍_职位推荐.py", label=":blue[岗位推荐]", icon="🔍")
        st.sidebar.page_link("pages/3_📊_能力评估.py", label=":green[能力评价]", icon="📊")
        st.sidebar.page_link("pages/4_🗺️_职场趋势.py", label=":orange[就业趋势]", icon="🗺️")
        app()
