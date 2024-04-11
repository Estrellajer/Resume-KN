import streamlit as st
import base64
import requests
import json
import difflib
from py2neo import Graph
import pandas as pd

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
    
    appcode = '9a95262e27054f318e64757acd129825'
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

    # # 评价和推荐逻辑
    # evaluation = "未评价"
    # recommended_positions = []

    # # 示例评价逻辑：基于学位和技能等级
    # if basic_info['degree'] >= 3:  # 硕士及以上
    #     evaluation = "适合高级研发岗位"
    #     recommended_positions.append('高级软件开发工程师')
    


    # 返回处理结果
    return {
        'basic_info': basic_info,
        # 'evaluation': evaluation,
        # 'recommended_positions': recommended_positions
    }

def build_query(education_levels, limit):

    query = """
    MATCH (p:Position)-[:EDUCATION]->(e:Education),
          (p)-[:SALARY]->(s:Salary),
          (p)-[r:REQUIRES_SKILL]->(sk:Skill),
          (p)-[:QUALITY]->(q:Quality)
    WHERE e.name IN $education_levels
    RETURN p.name AS Position, s.name AS Salary, collect({skill: sk.name, level: r.level}) AS Skills, e.name AS Education, q.name AS Quality
    ORDER BY s.name DESC
    LIMIT $limit
    """
    # 注意：这里使用参数化查询以提高安全性和性能
    results = graph.run(query, education_levels=education_levels, limit=limit)

    # 将结果转换为字典列表
    results_list = []
    for result in results:
        # 将每个结果项转换为字典
        result_dict = {
            "Position": result["Position"],
            "Salary": result["Salary"],
            "Skills": result["Skills"],
            "Education": result["Education"],
            "Quality": result["Quality"]
        }
        results_list.append(result_dict)

    return results_list

# 假设以下权重基于对于岗位的重要性
WEIGHTS = {
    'skill_match': 0.4,
    'skill_level_match': 0.3,
    'education_match': 0.1,
    'quality_match': 0.1,
    'skill_coverage': 0.1  # 新增的技能覆盖率权重
}

def calculate_match_score(resume, position_requirements):
    skill_match_score = 0
    skill_level_match_score = 0
    education_match_score = 1 if resume['basic_info']['degree'] >= position_requirements['Education'] else 0
    quality_match_score = 1 if resume['basic_info']['quality'] >= position_requirements['Quality'] else 0
    total_skills = len(position_requirements['Skills'])
    total_resume_skills = len(resume['basic_info']['skills'])
    matched_skills = 0  # 匹配到的技能数量

    for skill_requirement in position_requirements['Skills']:
        skill_name = skill_requirement['skill']
        required_level = skill_requirement.get('level') 
        if skill_name in resume['basic_info']['skills'] and required_level is not None:
            level_achieved = resume['basic_info']['skills'][skill_name]
            # 确保required_level不为None且不为0来避免除以0的情况
            if required_level > 0:
                skill_match_score += 1 * min(1, level_achieved / required_level) 
                matched_skills += 1
            else:
                # 处理required_level为0或其他非预期值的情况
                print(f"Unexpected skill level for {skill_name}: {required_level}")

    if total_skills > 0:
        skill_match_score /= total_skills
        skill_coverage = matched_skills / total_resume_skills  # 计算技能覆盖率
    else:
        skill_match_score = 0
        skill_coverage = matched_skills / total_resume_skills
        
    if skill_coverage < 0.5:
        skill_coverage = 0
    
    # Calculate the weighted average match score
    match_score = (
        WEIGHTS['skill_match'] * skill_match_score +
        WEIGHTS['skill_level_match'] * skill_level_match_score +
        WEIGHTS['education_match'] * education_match_score +
        WEIGHTS['quality_match'] * quality_match_score +
        WEIGHTS['skill_coverage'] * skill_coverage  # 加入技能覆盖率权重
    )
    
    return match_score
def recommend_positions(graph, resume, sort_by='match'):
    degree_to_education = {
        1: [2, 3],
        2: [2, 3],
        3: [3, 4],
        4: [3, 4]
    }

    education_levels = degree_to_education.get(resume['basic_info']['degree'], [])
    results_limit = 30

    # 使用修改后的查询函数获取岗位列表
    positions = build_query(education_levels, results_limit)

    # 为每个岗位计算匹配度
    for position in positions:
        position['match_score'] = calculate_match_score(resume, position)
    
    # 根据sort_by参数排序
    if sort_by == 'match':
        # 按匹配度排序
        positions.sort(key=lambda x: x['match_score'], reverse=True)
        # 返回匹配度最高的10个岗位的全部信息
        return positions[:10]
    else:
        # 按薪酬排序
        positions = [position for position in positions if position['match_score'] >= 0.3]
        positions.sort(key=lambda x: x['Salary'], reverse=True)
        # 返回匹配度大于0.5的薪酬最高的10个岗位
        return positions[:10]

# Neo4j 连接配置
uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
username = "neo4j"              # 修改为您的用户名
password = "Lmq141592"          # 修改为您的密码

# 初始化 Neo4j 连接
graph = Graph(uri, auth=(username, password))

st.title('简历上传和岗位推荐')

uploaded_file = st.file_uploader("选择你的简历", type=['docx', 'pdf'])

if uploaded_file is not None:
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

    # Flatten resume_data for better display in DataFrame
    flat_resume_data = {**resume_data['basic_info'], **resume_data['basic_info']['skills']}
    del flat_resume_data['skills']

    # Create a reverse dictionary
    reverse_education_keywords = {v: k for k, v in education_keywords.items()}

    # Convert degree back to its original form
    flat_resume_data['degree'] = reverse_education_keywords[flat_resume_data['degree']]
    st.subheader("简历数据")
    df_resume = pd.DataFrame(flat_resume_data, index=[0])
    st.dataframe(df_resume)

    sort_by = st.selectbox("选择排序方式", ["match", "salary"])
    recommended_jobs = recommend_positions(graph, resume_data, sort_by=sort_by)
    for job in recommended_jobs:
        job['Skills'] = ', '.join([skill['skill'] for skill in job['Skills']])
    st.subheader("推荐的岗位")
    df_jobs = pd.DataFrame(recommended_jobs)
    st.dataframe(df_jobs)