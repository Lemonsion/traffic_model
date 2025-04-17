# --------------导入相关模块-------------
import base64  # 用于编码和解码base64数据
import os  # 用于文件和目录操作
import shutil  # 用于高层次的文件操作（如删除文件夹）
import cv2  # OpenCV库，用于处理图像和视频
import uuid  # 用于生成唯一标识符
import traceback  # 用于追踪和显示异常信息
from PIL import Image  # Python图像库，用于打开和处理图片
from fastapi import UploadFile, File, HTTPException, BackgroundTasks  # FastAPI相关模块
from starlette.responses import JSONResponse  # 用于返回JSON响应
import magic  # 用于检查文件的MIME类型
# 导入数据库操作函数
from crud import insert_today_detection_record, update_today_config, update_today_processed_file
from fastApiProject.backend.config import Config
from fastApiProject.backend.video import process_image


def clear_folder(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹 '{folder_path}' 不存在")

    # 确保路径指向的是目录
    if not os.path.isdir(folder_path):
        raise ValueError(f"'{folder_path}' 不是目录")

    # 遍历并删除所有内容
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件或符号链接
            else:
                shutil.rmtree(file_path)  # 删除子目录
        except Exception as e:
            print(f"删除失败: {file_path} - {e}")

# --------------检查是否是图像文件-------------
def is_image_file(file: UploadFile):
    """检查上传的文件是否为图像文件"""
    mime = magic.Magic(mime=True)
    file.file.seek(0)
    detected_type = mime.from_buffer(file.file.read(1024))
    file.file.seek(0)
    return detected_type.startswith('image/')

# --------------上传文件并处理-------------
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """上传图像或视频文件并返回处理后的结果"""
    folder_to_clear = "./temp_videos"
    clear_folder(folder_to_clear)  # 清理临时视频文件夹

    Config.warning_count = 0  # 重置警告计数
    Config.warning_or_not = 0  # 重置警告标志
    try:
        # 处理图像文件
        if is_image_file(file):
            
            insert_today_detection_record("", 0)  # 插入当天检测记录
            image = Image.open(file.file)  # 使用PIL打开图像
            processed_img, detection_data = process_image(image)  # 处理图像并获取检测结果
            processed_img_cv = np.array(processed_img)
            processed_img_cv = cv2.cvtColor(processed_img_cv, cv2.COLOR_RGB2BGR)
            _, encoded_img = cv2.imencode(".jpg", processed_img_cv)  # 转换为JPEG格式
            img_base64 = base64.b64encode(encoded_img.tobytes()).decode("utf-8")  # 将图像转换为Base64编码字符串

            update_today_processed_file(img_base64)  # 更新当天处理的文件路径
            update_today_config(conf=Config.global_conf, detection_data=detection_data)  # 更新配置和检测数据
            response_data = {
                "confidence": Config.global_conf,
                "iou": Config.global_iou,
                "image_base64": img_base64,  # 返回Base64编码的图像
                "detections": detection_data,  # 返回检测结果
            }

            return JSONResponse(content=response_data)

        # 处理视频文件
        elif file.content_type == "video/mp4":
            Config.video_or_not = 1  # 设置视频标志
            stream_id = str(uuid.uuid4())  # 生成唯一的流ID
            temp_dir = "./temp_videos"
            os.makedirs(temp_dir, exist_ok=True)  # 创建临时视频文件夹
            temp_path = os.path.join(temp_dir, f"{stream_id}.mp4")

            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)  # 保存视频文件
            response_data = {
                "confidence": Config.global_conf,
                "iou": Config.global_iou,
                "stream_id": stream_id,  # 返回视频流的ID
            }
            insert_today_detection_record("", 0)  # 插入当天检测记录

            return JSONResponse(content=response_data)
        else:
            raise HTTPException(400, detail="不支持的文件类型")  # 处理不支持的文件类型

    except Exception as e:
        traceback.print_exc()  # 打印异常信息
        raise HTTPException(500, detail=f"处理失败: {str(e)}")  # 返回500错误
    finally:
        file.file.close()  # 关闭文件


