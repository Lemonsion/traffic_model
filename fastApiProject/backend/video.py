import os
import threading
import time
from collections import deque
import cv2
import numpy as np
import torch
from websocket import WebSocket
import traceback
from fastApiProject.backend.config import Config
from fastApiProject.backend.crud import update_today_warning_count
from fastApiProject.backend.state import active_connections
from fastApiProject.backend.yolo_model import model



# --------------run_inference函数-------------
def run_inference(frame):
    """在不进行梯度计算的情况下运行推理"""
    with torch.no_grad():
        return process_image(frame)

# --------------process_image函数-------------
def process_image(image: np.ndarray) -> np.ndarray:
    """使用 YOLO 处理图像"""
    # 将图像从RGB转换为BGR（YOLO模型需要BGR格式的图像）
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # 使用YOLO模型进行推理
    results = model(image, conf=Config.global_conf, iou=Config.global_iou)
    detection_data = {}

    # 获取图像的高和宽，用于计算检测框位置
    height, width = img_cv.shape[:2]
    warning_zone_y = int(height * 2 / 3)  # 设置警告区域的y坐标阈值

    # 遍历检测结果中的每个检测框
    for r in results:
        for box in r.boxes:
            xyxy = box.xyxy.cpu().numpy().squeeze()  # 获取检测框的坐标
            if xyxy.size != 4:
                continue
            x1, y1, x2, y2 = map(int, xyxy)
            cls_id = int(box.cls.cpu().numpy().squeeze())  # 类别ID
            conf = float(box.conf.cpu().numpy().squeeze())  # 检测框的置信度
            label = f"{model.names[cls_id]} ({conf:.2f})"  # 标签

            # 计算检测框中心坐标
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            site = ""

            # 判断检测框是否在警告区域，更新警告计数
            if y2 > warning_zone_y:
                if width / 2 > center_x > width / 6:
                    site = "左侧"
                elif width / 2 < center_x < 5 * width / 6:
                    site = "右侧"

                if Config.warning_or_not == 0:
                    Config.warning_count += 1  # 更新警告计数
                    Config.warning_or_not = 1  # 标记警告已触发
                    update_today_warning_count(Config.warning_count)  # 更新数据库中的警告计数

            # 将检测结果存储到detection_data中
            if cls_id not in detection_data:
                detection_data[cls_id] = {
                    "class_id": cls_id,
                    "class_name": label,
                    "targets": [],
                    "count": 0
                }

            detection_data[cls_id]["targets"].append({
                "x": center_x,
                "y": center_y,
                "confidence": round(conf, 2),
                "site": site
            })
            detection_data[cls_id]["count"] += 1

            # 在图像上绘制检测框
            cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_cv, label, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 如果没有视频流，重置警告状态
    if Config.video_or_not == 0:
        Config.warning_or_not = 0

    # 返回处理后的图像和检测数据
    return cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB), detection_data

# --------------reset_warning_loop函数-------------
def reset_warning_loop():
    """用于定时重置警告状态"""
    while Config.video_or_not == 1:
        time.sleep(3)  # 每3秒重置一次警告状态
        Config.warning_or_not = 0
    Config.reset_thread_running = False

# --------------try_start_reset_timer函数-------------
def try_start_reset_timer():
    """启动定时器来重置警告状态"""
    if Config.video_or_not == 1 and not Config.reset_thread_running:
        Config.reset_thread_running = True
        t = threading.Thread(target=reset_warning_loop, daemon=True)  # 启动一个后台线程
        t.start()

# --------------websocket_endpoint函数-------------
async def websocket_endpoint(websocket: WebSocket, stream_id: str):
    """WebSocket端点，用于传输视频处理结果"""
    await websocket.accept()  # 接受WebSocket连接
    video_path = f"./temp_videos/{stream_id}.mp4"  # 视频路径

    # 如果视频文件不存在，返回错误消息并关闭连接
    if not os.path.exists(video_path):
        await websocket.send_text("错误: 未找到视频")
        await websocket.close()
        return

    active_connections[stream_id] = websocket  # 保存当前连接
    try_start_reset_timer()  # 尝试启动定时器以重置警告状态
    await process_video_stream(websocket, video_path)  # 处理视频流
    del active_connections[stream_id]  # 完成后删除当前连接

frame_queue = deque(maxlen=5)  # --------------帧队列-------------
# 限制最大缓冲帧，防止爆内存

is_camera_running = False  # 全局标志，控制摄像头的运行

# --------------process_video_stream函数-------------
async def process_video_stream(websocket: WebSocket, file_path: str):
    """处理视频并通过WebSocket发送处理后的帧"""
    try:
        cap = cv2.VideoCapture(file_path)  # 打开视频文件
        fps = cap.get(cv2.CAP_PROP_FPS) or 25  # 获取视频帧率，默认为25

        while cap.isOpened():
            start_time = time.time()  # 记录处理开始时间
            ret, frame = cap.read()  # 读取视频帧
            if not ret:
                break  # 如果没有读取到帧，则结束

            # 对图像进行处理并获取检测数据
            with torch.no_grad():
                processed_frame, detection_data = process_image(frame)

            # 将检测数据发送给WebSocket
            await websocket.send_json({"detections": list(detection_data.values())})

            # 编码处理后的帧为JPEG格式
            _, jpeg = cv2.imencode('.jpg', processed_frame)

            # 发送帧数据到WebSocket
            await websocket.send_bytes(jpeg.tobytes())

            # 控制帧率，确保视频播放速度不受处理时间影响
            processing_time = time.time() - start_time
            time.sleep(max(0, (1 / fps) - processing_time))

        await websocket.send_text("completed")  # 视频处理完成，发送结束标记
    except Exception as e:
        traceback.print_exc()  # 捕获并打印异常
    finally:
        cap.release()  # 释放视频捕获对象
        os.remove(file_path)  # 删除临时视频文件
        await websocket.close()  # 关闭WebSocket连接
