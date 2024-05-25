# Title: 职位推荐
# Order: 2

import streamlit as st
import base64
import requests
import json
import difflib
from py2neo import Graph
import pandas as pd
import re


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

# 定义省市数据
province_city_data = {
    "广东省": ["中山", "梅州", "广州", "深圳", "潮州", "肇庆", "珠海", "惠州", "江门", "汕头", "湛江", "韶关", "东莞", "佛山"],
    "河北省": ["衡水", "保定", "石家庄", "邢台", "唐山", "邯郸", "沧州", "廊坊", "张家口", "秦皇岛"],
    "河南省": ["郑州", "南阳", "洛阳", "开封", "济源", "平顶山", "焦作", "许昌", "三门峡", "信阳", "驻马店", "漯河"],
    "湖北省": ["武汉", "襄阳", "宜昌", "荆州", "荆门", "黄冈", "十堰", "鄂州", "孝感", "黄石", "仙桃"],
    "陕西省": ["西安", "咸阳", "商洛", "铜川", "渭南", "延安", "榆林", "宝鸡", "安康"],
    "江西省": ["南昌", "九江", "景德镇", "上饶", "鹰潭", "赣州", "宜春", "吉安", "抚州"],
    "贵州省": ["贵阳市", "遵义", "安顺", "六盘水", "铜仁", "毕节", "黔南布依族苗族自治州", "黔东南苗族侗族自治州", "黔西南布依族苗族自治州"],
    "湖南省": ["娄底", "长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "永州"],
    "浙江省": ["杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水"],
    "福建省": ["福州", "厦门", "泉州", "漳州", "莆田", "三明", "南平", "龙岩", "宁德"],
    "山东省": ["青岛", "济南", "烟台", "潍坊", "威海", "淄博", "临沂", "济宁", "泰安", "日照", "滨州", "德州", "聊城", "东营", "枣庄", "菏泽"],
    "江苏省": ["南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁"],
    "北京市": ["北京"],
    "上海市": ["上海"],
    "天津市": ["天津"],
    "重庆市": ["重庆"],
    "未知": ["未知"],
}

def build_query(city, education_levels, limit):
    uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
    username = "neo4j"              # 修改为您的用户名
    password = "Lmq141592"          # 修改为您的密码
    graph = Graph(uri, auth=(username, password))
    query = """
    MATCH (cn:Company)-[:HAS]->(cp:CompanyPosition)-[:POSITION]->(p:Position),
        (cp)-[:CITY]->(c:City),
        (cp)-[sa:SALARY]->(s:Salary),
        (cp)-[r:REQUIRES_SKILL]->(sk:Skill),
        (cp)-[:QUALITY]->(q:Quality),
        (cp)-[:EDUCATION]->(e:Education)
    WHERE e.name IN $education_levels AND c.name = $city
    RETURN p.name AS Position, cn.name AS Company, cp.id AS CompanyPosition, s.name AS Salary, collect({skill: sk.name, level: r.level}) AS Skills, e.name AS Education, q.name AS Quality, sa.level AS SalaryLevel
    ORDER BY sa.level DESC
    LIMIT $limit
    """
    # 注意：这里使用参数化查询以提高安全性和性能
    results = graph.run(query, city=city, education_levels=education_levels, limit=limit)

    # 将结果转换为字典列表
    results_list = []
    for result in results:
        # 将每个结果项转换为字典
        result_dict = {
            "Position": result["Position"],
            "Company": result["Company"],
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
def recommend_positions(resume, city, sort_by='match'):
    degree_to_education = {
        1: [2, 3],
        2: [2, 3],
        3: [3, 4],
        4: [3, 4]
    }

    education_levels = degree_to_education.get(resume['basic_info']['degree'], [])
    results_limit = 30

    # 使用修改后的查询函数获取岗位列表
    positions = build_query(city, education_levels, results_limit)

    # 如果一个岗位也没有，返回空列表
    if not positions:
        return []

    # 为每个岗位计算匹配度
    for position in positions:
        position['match_score'] = calculate_match_score(resume, position)
    
    # 根据sort_by参数排序
    if sort_by == 'match':
        # 按匹配度排序
        positions.sort(key=lambda x: x['match_score'], reverse=True)
    else:
        # 按薪酬排序
        positions = [position for position in positions if position['match_score'] >= 0.3]
        positions.sort(key=lambda x: sum([salary['sum'] for salary in x['Salary']]), reverse=True)

    # 如果岗位数量少于10个，返回所有岗位
    if len(positions) < 10:
        return positions

    # 否则，返回前10个岗位
    return positions[:10]

def app():
    st.title('岗位推荐')
    
    resume_data = st.session_state.get('resume_data')
    if resume_data:
        sort_by = st.selectbox("选择排序方式", ["match", "salary"])
        selected_province = st.selectbox("选择省份", list(province_city_data.keys()))

        # 根据选中的省份显示对应的市
        selected_city = None
        if selected_province:
            selected_city = st.selectbox("选择城市", province_city_data[selected_province])
            st.write(f"你选择的城市是: {selected_city}")

        recommended_jobs = recommend_positions(resume_data, selected_city, sort_by=sort_by)
        if recommended_jobs:
            for job in recommended_jobs:
                job['Skills'] = ', '.join([skill['skill'] for skill in job['Skills']])
                job['Salary'] = ', '.join([salary['salary'] for salary in job['Salary']])
            st.subheader("推荐的岗位")
            df_jobs = pd.DataFrame(recommended_jobs)
            st.dataframe(df_jobs)
        else:
            st.write(f"在{selected_city}没有找到合适的岗位。")
    else:
        st.write("请在主页上传简历.")

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
