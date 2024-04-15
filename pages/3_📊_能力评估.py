# Title: 能力评估
# Order: 3

import streamlit as st
from py2neo import Graph
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

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

def query_specific_position(position_name):
    uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
    username = "neo4j"              # 修改为您的用户名
    password = "Lmq141592"          # 修改为您的密码
    graph = Graph(uri, auth=(username, password))
    query = """
    MATCH (p:Position)-[:EDUCATION]->(e:Education),
          (p)-[:SALARY]->(s:Salary),
          (p)-[r:REQUIRES_SKILL]->(sk:Skill),
          (p)-[:QUALITY]->(q:Quality)
    WHERE p.name = $position_name
    RETURN p.name AS Position, s.name AS Salary, collect({skill: sk.name, level: r.level}) AS Skills, e.name AS Education, q.name AS Quality
    """
    # 注意：这里使用参数化查询以提高安全性和性能
    results = graph.run(query, position_name=position_name)

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

def get_positions(min_salary, max_salary, pay_times, degree):
    uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
    username = "neo4j"              # 修改为您的用户名
    password = "Lmq141592"          # 修改为您的密码
    graph = Graph(uri, auth=(username, password))
    if pay_times == '12薪':
        salary_pattern = f"(?i)^{min_salary}-{max_salary}K$"
    else:
        salary_pattern = f"(?i)^{min_salary}-{max_salary}K·{pay_times}$"
    
    query = """
    MATCH (p:Position)-[:EDUCATION]->(e:Education),
          (p)-[:SALARY]->(s:Salary),
          (p)-[r:REQUIRES_SKILL]->(sk:Skill),
          (p)-[:QUALITY]->(q:Quality)
    WHERE s.name =~ $salary_pattern AND e.name = $degree
    RETURN p.name AS Position, s.name AS Salary, collect({skill: sk.name, level: r.level}) AS Skills, e.name AS Education, q.name AS Quality
    LIMIT 30
    """
    
    results = graph.run(query, {'salary_pattern': salary_pattern, 'degree': degree})
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

def convert_records_to_dataframe(records):
    data = []
    for record in records:
        # 初始化记录字典
        record_dict = {
            "Position": record['_fields'][0],
            "Salary": record['_fields'][1],
            "Skills": [],
            "Education": record['_fields'][3]['low'],  # 假设教育和质量字段是数字类型
            "Quality": record['_fields'][4]['low']
        }

        # 处理技能列表，每个技能是一个包含技能名和水平的字典
        for skill in record['_fields'][2]:
            skill_dict = {
                "skill": skill['skill'],
                "level": skill['level']['low']  # 处理可能的数值问题
            }
            record_dict["Skills"].append(skill_dict)
        
        # 将处理好的记录添加到数据列表
        data.append(record_dict)
    
    # 将数据列表转换为 DataFrame
    return pd.DataFrame(data)

def calculate_evaluate_score(resume, position_requirements):
    skill_match_score = 0
    total_skills = len(position_requirements['Skills'])
    matched_skills = 0  # 匹配到的技能数量

    for skill_requirement in position_requirements['Skills']:
        skill_name = skill_requirement['skill']
        required_level = skill_requirement.get('level')
        if skill_name in resume['basic_info']['skills']:
            level_achieved = resume['basic_info']['skills'].get(skill_name, 0)
            if required_level > 0:
                skill_match_score += 1 * min(1, level_achieved / required_level)
                matched_skills += 1

    skill_match_score = skill_match_score / total_skills if total_skills > 0 else 0

    education_match_score = 1 if resume['basic_info']['degree'] >= position_requirements['Education'] else 0
    if  position_requirements['Quality'] > 0 :
        quality_match_score = min(1, resume['basic_info']['quality'] / position_requirements['Quality']) 
    else :
        quality_match_score = 1
    return {
        'Education': education_match_score,
        'Quality': quality_match_score,
        'Skills': skill_match_score
    }

def plot_radar_chart(match_scores):
    labels = list(match_scores.keys())
    num_vars = len(labels)

    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    values = list(match_scores.values()) + [match_scores[labels[0]]]

    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids([a * 180/pi for a in angles[:-1]], labels)

    return fig

def plot_skills_histogram(resume, position_requirements):
    skills_df = pd.DataFrame(position_requirements['Skills'])
    skills_df['Resume Level'] = skills_df['skill'].map(resume['basic_info']['skills']).fillna(0)
    skills_df.set_index('skill', inplace=True)

    fig, ax = plt.subplots()
    skills_df[['level', 'Resume Level']].plot(kind='bar', ax=ax, color=['skyblue', 'lightgreen'])
    ax.set_ylabel('Skill Level')
    ax.set_title('Position Skill Requirements vs. Resume Skills')
    ax.legend(["Required Level", "Resume Level"])

    return fig

def generate_recommendations(match_scores):
    recommendations = []

    # 检查教育匹配得分
    if match_scores['Education'] < 1:
        recommendations.append("建议考虑提升学历，如报读相关专业的研究生课程或获取专业证书。")

    # 检查素质匹配得分
    if match_scores['Quality'] < 1:
        recommendations.append("建议参与更多实践活动以提高个人素质，比如志愿者工作、行业会议或相关培训课程。")

    # 检查技能匹配得分
    if match_scores['Skills'] < 1:
        recommendations.append("建议针对职位要求的关键技能进行专门训练和提升，特别是那些你目前匹配程度不高的技能。")

    return recommendations

def app():
    st.title('Capability Evaluation')
    st.write("Capability evaluation details here based on the processed resume data.")

    resume = st.session_state.get('resume_data')
    # Add an input box in the sidebar
    position_name = st.sidebar.text_input("Position Name", "Software Engineer")

    # Query the specific position
    position_requirements = query_specific_position(position_name)

    # Calculate the evaluate score
    match_scores = calculate_evaluate_score(resume, position_requirements[0])

    # Plot the radar chart
    fig1 = plot_radar_chart(match_scores)
    st.pyplot(fig1)

    # Plot the skills histogram
    fig2 = plot_skills_histogram(resume, position_requirements[0])
    st.pyplot(fig2)

    # Display the data
    st.dataframe(position_requirements)
def app():
    st.title('Job Matching and Capability Evaluation')
    min_salary = st.selectbox("选择最低薪资（K）", range(1, 101))  # 假设薪资范围1K到100K
    max_salary = st.selectbox("选择最高薪资（K）", range(1, 101))
    pay_times_options = ["12薪", "13薪", "14薪", "15薪", "16薪"]
    pay_times = st.selectbox("选择薪资次数（默认为12薪）", options=pay_times_options, index=0)
    # 用户选择教育水平，返回值是教育水平的名称
    degree_name = st.selectbox("教育要求", list(education_keywords.keys()), index=2)

    # 从education_keywords字典中获取对应的数字值
    degree_required = education_keywords[degree_name]

    if st.button("查询岗位"):
        if min_salary > max_salary:
            st.error("最低薪资不能高于最高薪资！")
        else:
            result = get_positions(min_salary, max_salary, pay_times, degree_required)
            if not result:
                st.write("没有找到符合条件的岗位。")
            else:
                for job in result:
                    job['Skills'] = ', '.join([skill['skill'] for skill in job['Skills']])
                st.subheader("推荐的岗位")
                df_jobs = pd.DataFrame(result)
                st.dataframe(df_jobs)
                # 提取所有职位名称
                positions = [job['Position'] for job in result]
                # Display job positions in a select box
                selected_position = st.selectbox("Select a Job Position to Evaluate", positions)

                # Retrieve the full details of the selected job position
                if selected_position:
                    position_details = query_specific_position(selected_position)

                    st.dataframe(position_details[0])
                    
                    # Assuming a placeholder for resume data structure
                    resume = st.session_state.get('resume_data')
                    match_scores = calculate_evaluate_score(resume, position_details[5])
                    
                    # Visualization
                    col1, col2 = st.columns(2)  # 创建两列

                    with col1:  # 在第一列中展示第一张图
                        fig1 = plot_radar_chart(match_scores)
                        st.pyplot(fig1)

                    with col2:  # 在第二列中展示第二张图
                        fig2 = plot_skills_histogram(resume, position_details[5])
                        st.pyplot(fig2)
                        
                    recommendations = generate_recommendations(match_scores)
                    with st.container():  # 创建一个容器放置建议
                        st.header("提升建议")
                        for recommendation in recommendations:
                            st.markdown(f"- {recommendation}")

if __name__ == "__main__":
    app()
