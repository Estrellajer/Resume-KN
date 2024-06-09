import os
from pdf2image import convert_from_path
from PIL import Image
import io
import base64
from docx import Document
import requests
import pprint
import json

# 获取脚本文件的绝对路径
script_path = os.path.abspath(__file__)

# 获取脚本文件所在的目录
script_dir = os.path.dirname(script_path)

# 更改当前工作目录到脚本文件所在目录
os.chdir(script_dir)

API_URL = "https://n645a2a4mcrfldk1.aistudio-hub.baidu.com/ocr"
TOKEN = "60adec91ca3d86eae269595aaa6c64ab19bc70a8"
headers = {
    "Authorization": f"token {TOKEN}",
    "Content-Type": "application/json"
}

def process_file(file_path):
    # 获取文件的扩展名
    _, ext = os.path.splitext(file_path)

    if ext == '.pdf':
        # 将PDF文件转换为图像
        images = convert_from_path(file_path)

        # 将图像转换为Base64编码的字符串
        base64_images = []
        for image in images:
            byte_arr = io.BytesIO()
            image.save(byte_arr, format='PNG')
            base64_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
            base64_images.append(base64_image)

        texts = []
        for base64_image in base64_images:
            # 设置请求体
            payload = {
                "image": base64_image  # Base64编码的文件内容或者文件链接
            }

            # 调用
            resp = requests.post(url=API_URL, json=payload, headers=headers)

            # 处理接口返回数据
            assert resp.status_code == 200
            result = resp.json()["result"]
            texts.append(' '.join(result["texts"]))

        return '\n'.join(texts)

    elif ext == '.docx':
        doc = Document(file_path)
        text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
        return text

    elif ext in ['.jpg', '.png', '.jpeg']:
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode('ascii')

        # 设置请求体
        payload = {
            "image": base64_image  # Base64编码的文件内容或者文件链接
        }

        # 调用
        resp = requests.post(url=API_URL, json=payload, headers=headers)

        # 处理接口返回数据
        assert resp.status_code == 200
        result = resp.json()["result"]
        return ' '.join(result["texts"])

    else:
        print(f"Unsupported file type: {ext}")
        return None

def parse_text(text):
    url = "http://127.0.0.1:8190/taskflow/uie"
    headers = {"Content-Type": "application/json"}
    data = {"data": {"text": [text]}}
    
    # 发送 POST 请求
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    
    # 解析响应数据
    parsed_data = json.loads(response.text)
    
    return parsed_data

file_path = "../北京邮电大学-王欣-硕士-信通院.docx"
text = process_file(file_path)

# 进一步处理文本
parsed_data = parse_text(text)
print("\n解析后的数据:")
pprint.pp(parsed_data)
