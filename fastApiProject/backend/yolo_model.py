# -------------------- 基础导入 --------------------
import re  # 正则表达式，用于提取英文
import torch  # PyTorch，用于模型是否能使用 GPU
from fastapi import WebSocket, WebSocketDisconnect  # WebSocket 实时通信
from ultralytics import YOLO  # YOLO 目标检测模型
import requests  # 用于调用外部 HTTP API
import json  # JSON 格式处理

# 百度翻译 API 的密钥
API_KEY = "9xNveMRBSPmOHfhVJsfCOAv7"
SECRET_KEY = "HaPwYy7Pdesk9ifFrR3V7yI3wgIpl9mP"



# 提取字符串中的英文部分（包括字母、数字、标点等）
def extract_english(text: str):
    return re.findall(r'[a-zA-Z0-9,.!?;:"()&\'-]+', text)

# 将文本中的英文部分翻译为中文，保留 "think" 这个词不翻译
def translate_english_in_text(text: str):
    english_parts = extract_english(text)

    if not english_parts:
        return text  # 没有英文则直接返回原文本

    for part in english_parts:
        if part.lower() == "think":  # "think" 这个词不翻译（无论大小写）
            continue
        translated_part = translate_baidu(part)  # 调用百度翻译
        text = text.replace(part, translated_part)  # 替换原文中的英文

    return text


# 调用百度翻译 API，将英文翻译成中文
def translate_baidu(part: str):
    url = "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token=" + get_access_token()

    payload = json.dumps({
        "from": "en",
        "to": "zh",
        "q": part
    }, ensure_ascii=False)  # 防止中文被转义
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # 发起 POST 请求进行翻译
    response = requests.post(url, headers=headers, data=payload.encode("utf-8"))
    result = response.json()

    # 打印返回内容，便于调试
    print(result)

    # 提取翻译结果
    try:
        translated_text = result["result"]["trans_result"][0]["dst"]
        return translated_text
    except Exception as e:
        print("翻译失败:", e)
        return part  # 出错时返回原文


# 获取百度翻译接口的 access_token（访问令牌）
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    return str(requests.post(url, params=params).json().get("access_token"))



model = YOLO(r'..\weights\best.pt').to(
    'cuda' if torch.cuda.is_available() else 'cpu')
# # 调用 Ollama 模型接口
OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"  # Ollama API地址
OLLAMA_MODEL = "traffic_model"  # 你的模型名称

prompt_style = """以下是一项任务的描述，附带提供背景信息的输入内容。
请撰写能恰当完成该请求的响应。在回答前，请仔细思考问题并建立分步推理链条，以确保回答的逻辑性和准确性。

### Instruction:
您是一位资深的交通法规专家、博士，在道路交通法律法规、交通事故责任认定、驾驶行为规范和交通安全教育方面拥有深厚的专业知识。请回答以下交通规则相关问题。

### Question:
{}

### Response:
{}"""

# WebSocket 实时通信处理函数
async def websocket_endpoint_t(websocket: WebSocket):
    await websocket.accept()  # 接收连接

    try:
        while True:
            # 1. 从前端接收问题文本
            question = await websocket.receive_text()

            # 2. 格式化 prompt，把问题嵌入模板中
            formatted_prompt = prompt_style.format(question, "")

            # 3. 构造大模型请求体
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a traffic law expert."},  # 系统提示角色
                    {"role": "user", "content": formatted_prompt}  # 用户输入内容
                ]
            }

            headers = {
                "Content-Type": "application/json"
            }

            # 4. 向本地 Ollama 模型发送请求
            response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)

            # 5. 错误处理
            if response.status_code != 200:
                await websocket.send_text("Ollama API request failed")
                continue

            # 6. 解析响应
            response_json = response.json()

            # 7. 获取模型回答内容
            answer = response_json['choices'][0]['message']['content']

            # 8. 将回答中的英文部分翻译成中文（保留 think）
            translated_answer = translate_english_in_text(answer)

            # 9. 返回翻译后的结果给前端
            await websocket.send_text(translated_answer)

    except WebSocketDisconnect:
        print("Client disconnected")  # 客户端断开连接时的提示
