
from typing import Optional
from fastapi import WebSocket, UploadFile, File, BackgroundTasks, Form
from starlette.responses import JSONResponse
from fastapi import  Request
from starlette.middleware.cors import CORSMiddleware
from db import engine
from models import Base
from fastApiProject.backend.Processing import upload
from fastApiProject.backend.camera import websocket_camera
from fastApiProject.backend.crud import get_detection_data_by_date
from fastApiProject.backend.set_iou_conf import set_conf_iou
from fastApiProject.backend.video import websocket_endpoint
from fastApiProject.backend.yolo_model import websocket_endpoint_t
from fastApiProject.backend.crud import get_detection_summary_endpoint
from fastapi import FastAPI


Base.metadata.create_all(bind=engine)
# 你原来的接口继续保留...

app = FastAPI()
# 线程池


# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 再添加一个动态 origin 检测中间件
@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and (origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    return await call_next(request)

# --------------设置IOU阈值-------------
# 接口用于设置对象检测的IOU阈值
@app.post("/set_conf_iou/")
async def set_conf_iou_(conf: float = Form(...), iou: float = Form(...)):
    return await set_conf_iou(conf, iou)

# --------------上传文件接口-------------
# 上传文件接口，后台处理上传的文件
@app.post("/upload/")
async def upload_(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    return await upload(background_tasks, file)

# --------------获取指定日期的检测数据-------------
# 根据日期查询检测数据，返回 JSON 格式的响应
@app.get("/get_detection_data/")
def get_detection_data_by_date_(date: Optional[str] = None):
    data_ = get_detection_data_by_date(date)
    return JSONResponse(content=data_)

# --------------WebSocket端点（视频流）-------------
# 用于视频流的 WebSocket 连接，允许与客户端进行实时数据交互
@app.websocket("/ws/{stream_id}")
async def websocket_endpoint_(websocket: WebSocket, stream_id: str):
    return await websocket_endpoint(websocket, stream_id)

# --------------WebSocket端点（摄像头）-------------
# 用于摄像头的视频流 WebSocket 连接
@app.websocket("/camera")
async def websocket_camera_t(websocket: WebSocket):
    return await websocket_camera(websocket)

# --------------WebSocket端点（API）-------------
# 用于API的 WebSocket 连接
@app.websocket("/api")
async def websocket_endpoint_t_(websocket: WebSocket):
    return await websocket_endpoint_t(websocket)


# --------------检测总结接口-------------
# 获取检测总结信息
@app.post("/detection_summary")
async def get_detection_summary_endpoint_(request: Request):
    return await get_detection_summary_endpoint(request)

if __name__ == "__main__":
    import uvicorn

    # --------------启动 FastAPI 应用-------------
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
