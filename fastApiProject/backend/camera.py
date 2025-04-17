import threading
import cv2
import torch
from starlette.websockets import WebSocketDisconnect
from websocket import WebSocket
from fastApiProject.backend.video import frame_queue, run_inference
from fastApiProject.backend.state import executor



# --------------采集帧的协程-------------
# 异步函数，用于从摄像头采集帧数据
async def capture_frames(cap):
    """独立协程采集帧"""
    global is_camera_running
    while is_camera_running and cap.isOpened():  # 检查摄像头是否正在运行
        ret, frame = cap.read()  # 从摄像头读取一帧
        if ret:  # 如果成功读取帧
            frame_queue.append(frame)  # 将帧添加到队列中
        await asyncio.sleep(0.01)  # 控制采集速度，防止过度消耗资源

# --------------处理并发送帧到前端的协程-------------
# 异步函数，用于从队列中取出帧并发送给客户端
async def process_and_send_frames(websocket):
    """独立协程处理并发送帧"""
    while True:
        if frame_queue:  # 如果队列中有帧
            frame = frame_queue.popleft()  # 从队列中取出一帧
            with torch.no_grad():  # 禁用梯度计算
                loop = asyncio.get_event_loop()  # 获取事件循环
                # 使用后台线程进行推理处理
                processed_frame, detection_data = await loop.run_in_executor(executor, run_inference, frame)
            _, jpeg = cv2.imencode('.jpg', processed_frame)  # 将处理后的帧编码为JPEG格式
            await websocket.send_json({"detections": list(detection_data.values()),  # 发送检测数据
                                       # "summary": summary  # 发送检测总结数据（注释掉了）
                                      })
            await websocket.send_bytes(jpeg.tobytes())  # 发送JPEG格式的图像帧
            print("向前端传送完毕")
        else:
            await asyncio.sleep(0.01)  # 如果队列为空，稍微等待一段时间再进行检查


cap = None
cap_lock = threading.Lock()  # 用于线程同步

import asyncio

# --------------摄像头任务管理变量-------------
# 用于管理摄像头任务的变量
capture_task = None
process_task = None

is_camera_running = False  # 摄像头运行状态标志


# --------------WebSocket摄像头控制接口-------------
# 用于处理WebSocket连接和控制摄像头的启停
async def websocket_camera(websocket: WebSocket):
    global cap, is_camera_running, capture_task, process_task
    await websocket.accept()  # 接受WebSocket连接

    try:
        while True:
            message = await websocket.receive_text()  # 接收客户端发送的消息

            if message == "start_camera":  # 客户端请求启动摄像头
                print("启动摄像头")
                with cap_lock:  # 使用锁，确保线程安全
                    if cap is None or not cap.isOpened():  # 如果摄像头未开启或已释放
                        cap = cv2.VideoCapture(0)  # 打开默认摄像头
                        if cap.isOpened():  # 如果成功打开摄像头
                            is_camera_running = True  # 启动摄像头
                            print("摄像头已启动")
                            # 启动捕获和处理任务
                            capture_task = asyncio.create_task(capture_frames(cap))
                            process_task = asyncio.create_task(process_and_send_frames(websocket))
                        else:
                            await websocket.send_text("无法打开摄像头")  # 无法打开摄像头，向客户端发送错误信息
                    else:
                        await websocket.send_text("摄像头已在运行中")  # 如果摄像头已经在运行，告知客户端

            elif message == "stop_camera":  # 客户端请求停止摄像头
                print("停止摄像头")
                with cap_lock:  # 使用锁，确保线程安全
                    if cap and cap.isOpened():  # 如果摄像头正在运行
                        is_camera_running = False  # 停止摄像头
                        cap.release()  # 释放摄像头资源
                        cap = None
                        print("摄像头已停止")
                        await websocket.send_text("摄像头已停止")  # 向客户端发送摄像头停止的消息

                        # 取消捕获和处理任务
                        if capture_task:
                            capture_task.cancel()  # 取消捕获任务
                            try:
                                await capture_task
                            except asyncio.CancelledError:
                                print("捕获任务已取消")

                        if process_task:
                            process_task.cancel()  # 取消处理任务
                            try:
                                await process_task
                            except asyncio.CancelledError:
                                print("处理任务已取消")
                    else:
                        await websocket.send_text("摄像头未启动")  # 如果摄像头未启动，告知客户端

    except WebSocketDisconnect:  # 客户端断开连接时
        print("客户端已断开连接")
    finally:
        with cap_lock:
            if cap and cap.isOpened():  # 如果摄像头仍在运行，释放资源
                cap.release()
            await websocket.close()  # 关闭WebSocket连接
