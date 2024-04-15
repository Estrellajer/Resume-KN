import streamlit as st

# 设置页面配置，必须是第一条执行的 Streamlit 命令
st.set_page_config(page_title="简历分析系统", layout="wide")

st.title('简历分析系统')

# 项目介绍
st.header("项目介绍")
st.markdown("""
    本系统旨在帮助大学生明确自身在意向岗位上的知识和技能短板，快速定位到理想职位。
    通过智能简历分析系统，我们降低了企业与求职者之间的匹配成本，并提高了求职和招聘的效率。
""")

# 创意描述
st.header("创意描述")
st.markdown("""
    系统通过自然语言处理和实体识别技术提取简历关键信息，利用机器学习算法进行职位匹配，
    并通过知识图谱对职位信息和求职者资料进行深入分析，从而提供个性化的职位推荐。
""")

# 功能简介
st.header("功能简介")
st.markdown("""
    - **知识图谱构建**：构建职位和技能要求的知识图谱，为推荐系统提供支持。
    - **简历上传与解析**：深入聚合和分析用户的简历和职业特征。
    - **职位推荐模型**：基于内容的推荐，通过技能匹配、教育水平匹配、经验匹配提供职位推荐。
    - **能力评估**：提供针对感兴趣职位的深入能力评估和可视化展示。
""")



# 结语
st.header("结语")
st.markdown("""
    通过智能简历分析系统，我们提供了一种创新的方式来洞察和影响求职市场，提高了求职者和招聘人员的互动效率。
    我们将持续优化和升级系统，以适应市场的变化，提供最佳的用户体验。
""")

# # 设置侧边栏导航
# st.sidebar.title("导航")
# pages = {
#     "首页": home,
#     "职位推荐": job_recommendations,
#     "能力评估": capability_evaluation,
# }


# selection = st.sidebar.radio("转到", list(pages.keys()))
# page = pages[selection]
# page.app()
