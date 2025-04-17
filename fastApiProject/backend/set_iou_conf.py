
import traceback
from fastapi import HTTPException,Form
from starlette.responses import JSONResponse
from fastApiProject.backend.config import Config


# --------------接收并更新conf和iou值的接口-------------
async def set_conf_iou(conf: float = Form(...), iou: float = Form(...)):
    """接收前端滑动条的 conf 和 iou 值并更新全局变量"""
    try:
        # --------------更新全局变量--------------
        Config.global_conf = conf  # 更新全局 conf
        Config.global_iou = iou  # 更新全局 iou

        # 打印更新后的值，方便调试
        print(f"Updated conf: {Config.global_conf}, iou: {Config.global_iou}")

        # --------------返回成功消息-------------
        # 返回一个JSON响应，告知前端更新成功，并返回新的配置值
        return JSONResponse(content={"message": "配置更新成功", "conf": conf, "iou": iou})

    except Exception as e:
        # --------------异常处理-------------
        traceback.print_exc()  # 打印堆栈信息，方便调试
        # 如果发生错误，抛出一个HTTP 500错误
        raise HTTPException(500, detail=f"处理失败: {str(e)}")