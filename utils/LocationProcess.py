import pandas as pd
import re
import requests
def parse_salary(salary_str):
    """解析薪资字符串，计算年平均薪资"""
    match = re.match(r'(\d+)-(\d+)K·(\d+)薪', salary_str)
    if match:
        low, high, times = map(int, match.groups())
        return (low + high) / 2 * times * 1000
    else:
        match = re.match(r'(\d+)-(\d+)K', salary_str)
        if match:
            low, high = map(int, match.groups())
            return (low + high) / 2 * 12 * 1000
    return 0

def get_coordinates(city, key):
    """通过腾讯地图API获取城市的经纬度。"""
    base_url = "https://apis.map.qq.com/ws/geocoder/v1/"
    params = {"address": city, "key": key}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 0:
            location = data['result']['location']
            return location['lat'], location['lng']
    return None, None

def process_data(filepath, api_key):
    data = pd.read_csv(filepath)
    data['average_salary'] = data['salary'].apply(parse_salary)
    data['latitude'] = None
    data['longitude'] = None

    for i, row in data.iterrows():
        lat, lng = get_coordinates(row['city'], api_key)
        data.at[i, 'latitude'] = lat
        data.at[i, 'longitude'] = lng

    # 保存处理后的数据到新文件
    data.to_csv('../location_data.csv', index=False)

# 如果需要手动运行处理脚本，取消下面的注释
process_data('../processed_data.csv', 'FZPBZ-X4XLA-PAXKI-C7SKG-L5LM5-GLBOT')
