import streamlit as st

# 设置页面配置，必须是第一条执行的 Streamlit 命令
st.set_page_config(page_title="简历分析系统", layout="wide")

from modules.auth import (get_auth, get_login, get_register,
                          get_logout, get_forgot_password)

authenticator = get_auth()

# 检查是否已认证
if st.session_state["authentication_status"]:
    user_info = st.session_state.username
    # 显示主页
    st.sidebar.success(f"欢迎用户 {user_info}")
    # 显示注销按钮
    get_logout(authenticator)
        # st.session_state["authentication_status"] = False
    # 构建带有Streamlit Ant Design组件的侧边菜单
    st.sidebar.page_link("app.py", label=":red[首页]", icon="🏠")
    st.sidebar.page_link("pages/1_🏠_简历.py", label=":violet[简历上传]", icon="📑")
    st.sidebar.page_link("pages/2_🔍_职位推荐.py", label=":blue[岗位推荐]", icon="🔍")
    st.sidebar.page_link("pages/3_📊_能力评估.py", label=":green[能力评价]", icon="📊")
    st.sidebar.page_link("pages/4_🗺️_职场趋势.py", label=":orange[就业趋势]", icon="🗺️")

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

else:
    
    st.title(':world_map: _:blue[职能图谱]_ ：开启职业新未来，助力精准就业！')
    col1, col2 = st.columns(2)
    
    with col1:
        st.image('utils/test.png', use_column_width=True)
        
    with col2:
        tab1, tab2, tab3 = st.tabs(['Login', 'Register', 'ForgotPassword'])

        with tab1:
            get_login(authenticator)

        with tab2:
            get_register(authenticator)

        with tab3:
            get_forgot_password(authenticator)
