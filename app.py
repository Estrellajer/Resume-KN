import streamlit as st
from pages import home, job_recommendations, capability_evaluation
from py2neo import Graph

# 设置页面配置，必须是第一条执行的 Streamlit 命令
st.set_page_config(page_title="简历分析系统", layout="wide")

# 设置侧边栏导航
st.sidebar.title("导航")
pages = {
    "首页": home,
    "职位推荐": job_recommendations,
    "能力评估": capability_evaluation,
}


selection = st.sidebar.radio("转到", list(pages.keys()))
page = pages[selection]
page.app()
