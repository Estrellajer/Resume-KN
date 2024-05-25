# Title: 职场趋势
# Order: 4

import pandas as pd
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Map, Timeline, Bar
from pyecharts.faker import Faker
from pyecharts.globals import ChartType
import os
import json
import branca
from streamlit_echarts import st_pyecharts
from streamlit_echarts import Map as st_Map
import streamlit.components.v1 as components

# 读取数据
df = pd.read_csv('./location_data.csv')
df['city'] = df['city']

# 计算每个城市的岗位数量
job_counts = df['city'].value_counts().reset_index()
job_counts.columns = ['city', 'count']
job_counts = list(zip(job_counts['city'].tolist(), job_counts['count'].tolist()))

# 过滤出岗位数多于10的城市
job_counts_filtered_10 = [(city, count) for city, count in job_counts if count > 10]

# 计算每个城市的平均薪资
avg_salaries = df.groupby('city')['annual_salary'].mean().round(0).reset_index()
avg_salaries.columns = ['city', 'average_salary']
avg_salaries = list(zip(avg_salaries['city'].tolist(), avg_salaries['average_salary'].tolist()))

# 过滤出岗位数多于10的城市
filtered_cities = [city for city, count in job_counts_filtered_10]
job_counts_filtered_10_salary = [(city, average_salary) for city, average_salary in avg_salaries if city in filtered_cities]

# 过滤出岗位数多于500的城市
job_counts_filtered = [(city, count) for city, count in job_counts if count > 500]

# 创建时间线
timeline = Timeline()

map1 = (
    Map()
    .add(
        series_name="岗位数量（热力图）", 
        data_pair=job_counts, 
        maptype="china-cities", 
        label_opts=opts.LabelOpts(is_show=False), 
        is_map_symbol_show=False,
        center=[114.114129, 37.550339],
        zoom=1.5,
    )
    .add(
        series_name="岗位数量（标签）", 
        data_pair=job_counts_filtered, 
        maptype="china-cities", 
        label_opts=opts.LabelOpts(is_show=True), 
        is_map_symbol_show=False,
        center=[114.114129, 37.550339],
        zoom=1.5,
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="岗位数量"),
        visualmap_opts=opts.VisualMapOpts(max_=200),
    )
)
timeline.add(map1, "岗位数量")

# 添加平均薪资数据
map2 = (
    Map()
    .add(
        series_name="平均薪资", 
        data_pair=avg_salaries, 
        maptype="china-cities", 
        label_opts=opts.LabelOpts(is_show=False), 
        is_map_symbol_show=False,
        center=[114.114129, 37.550339],
        zoom=1.5,
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="平均薪资"),
        visualmap_opts=opts.VisualMapOpts(max_=200000),
    )
)
timeline.add(map2, "平均薪资")

# 将图表转换为 HTML 字符串
timeline_html = timeline.render_embed()

# 对岗位数量进行排序并取前5个
top5_job_counts = sorted(job_counts, key=lambda x: x[1], reverse=True)[:5]

# 对平均薪资进行排序并取前5个
top5_avg_salaries = sorted(job_counts_filtered_10_salary, key=lambda x: x[1], reverse=True)[:5]

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
    

    st.title('职场趋势')

    #  在 Streamlit 应用中显示图表
    components.html(timeline_html, height=600, width=1000)



    # 创建岗位数量图表
    bar1 = (
        Bar()
        .add_xaxis([item[0] for item in top5_job_counts])
        .add_yaxis("岗位数量", [item[1] for item in top5_job_counts])
        .set_global_opts(title_opts=opts.TitleOpts(title="岗位数量最多的5个城市"))
    )

    # 在 Streamlit 应用中显示图表
    st_pyecharts(bar1)

    # 创建平均薪资图表
    bar2 = (
        Bar()
        .add_xaxis([item[0] for item in top5_avg_salaries])
        .add_yaxis("平均薪资", [item[1] for item in top5_avg_salaries])
        .set_global_opts(title_opts=opts.TitleOpts(title="平均薪资最高的5个城市"))
    )

    # 在 Streamlit 应用中显示图表
    st_pyecharts(bar2)