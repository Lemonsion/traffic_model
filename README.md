

# **基于 YOLOv8 的自动驾驶目标检测系统**

## **项目简介**

本项目是一个基于 YOLOv8 深度学习模型的**自动驾驶目标检测**系统，旨在实时检测道路上的车辆、行人、交通标志等目标，为自动驾驶提供可靠的**环境感知能力**。系统由以下部分组成：

- **目标检测算法**：基于 YOLOv8 的深度学习模型，用于目标检测。
- **后端服务**：使用 FastAPI 框架，提供 API 接口，处理模型推理和数据交互。
- **前端界面**：基于 Vue.js 框架，提供用户交互界面，展示检测结果和系统状态。

------

## **系统架构**

### 1. **整体架构**

- 前端（Vue.js）
  - 用户交互界面，用于上传图像/视频、用图像标记展示检测结果、配置参数等。
  - 数据可视化，通过表格和柱形图展示统计检测信息与分析结果。
- 后端（FastAPI）
  - 接收前端请求，调用 YOLOv8 模型进行推理，返回检测结果。
  - 提供 API 接口，支持图像/视频上传、大模型问答、结果查询等功能。
- 目标检测模型（YOLOv8）
  - 基于 Ultralytics YOLOv8 的预训练模型，支持自定义数据集训练。
  - 实现实时目标检测，输出目标类别、置信度和边界框。

### 2. **技术栈**

- **深度学习框架**：PyTorch-2.0
- **目标检测模型**：YOLOv8
- **后端框架**：FastAPI
- **前端框架**：Vue.js
- **模型部署与运维**：PyTorch
- **其他工具**：OpenCV（视频处理）、NumPy、Pandas

------

## **功能特性**

1. 目标检测
   - 支持车辆、行人、交通标志等10种驾驶视野可能出现的目标的实时检测。
   - 高精度检测，支持自定义数据集训练。
2. 前后端分离
   - 前端提供友好的用户界面，后端提供高效的 API 服务。
3. 实时推理
   - 支持单张图像和视频的实时检测与结果。
4. 动态参数调整
   - 支持前端实时调整 `conf` 与 `iou` 参数。
5. 区域预警逻辑
   - 支持左/右侧划分与底部“预警区”逻辑提示。
6. MySQL 数据统计
   - 记录检测与预警日志，支持每日统计与历史查询
7. 语音识别
   - 支持 PCM 音频文件解析为文字
8. 模型管理
   - 通过 Ollama 本地接口接入 LLM 提供法规问答服务
9. 结果可视化
   - 前端展示检测结果，包括目标边界框、类别标签和置信度。
   - 检测的目标类别统计，每个目标的位置。



## **模型训练**

### 1.数据集

- BDD100K：源自伯克利深度驾驶（Berkeley DeepDrive）实验室，是一个**大规模、多样化的自动驾驶数据集**。该数据集包含 10 万张高质量的视频片段，每段时长约为 10 秒，总计覆盖超过 160 小时的真实世界驾驶场景。这些数据在全球多个城市、多种天气条件下收集，涵盖了丰富的**道路、交通标志和行人等元素**。

  - 提供了 **10 万张关键帧图像的详细标注**，包括各类物体的边界框、类型、遮挡情况、是否被截断等信息。
  - 部分图像还进行了全帧实例分割标注，提供了像素级和实例级的详细注释。

- json格式转换为yolo格式

  `python  divide.py`
  
  数据集下载：https://www.kaggle.com/datasets/solesensei/solesensei_bdd100k

### 2.模型调参

​	修改模型参数进行训练以训练出较高精度的模型。

```
from ultralytics import YOLO

# 加载预训练的YOLOv8模型（可选）
# 你可以选择不同的模型文件，如 'yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'
model = YOLO('yolov8n.pt') #'yolov8s.pt' （可选）

# 训练模型
results = model.train(
    # model=r"F:\pycharm\projectFiles\autonomous_driving_object_detection\ultralytics\cfg\models\v8\yoloe-v8-CBAM.yaml",  # 自定义模型配置文件路径（可选）
    data='BDD100k.yaml',  # 数据集配置文件路径
    imgsz=1280,  # 输入图像大小
    epochs=80,  # 训练轮数
    workers=6,  # 数据加载的工作线程数
    cache=True,  # 加快图片读取速度，通过缓存数据
    batch=32,  # 批量大小，根据硬件资源调整
    name='yolov8n_100K',  # 输出文件夹名称
    save_period=10,  # 每10个epoch保存一次模型
    project='runs/detect',  # 输出文件夹路径
    optimizer="SGD",  # 优化器类型，使用随机梯度下降
    lr0=0.01,  # 初始学习率
    lrf=0.0001,  # 最终学习率（相对于初始学习率的比例）
    momentum=0.937,  # 动量，用于加速收敛
    weight_decay=0.0005,  # 权重衰减，用于防止过拟合
    dropout=0.1,  # Dropout概率，用于防止过拟合
    hsv_h=0.015,  # 色调抖动，数据增强参数
    hsv_s=0.7,  # 饱和度抖动，数据增强参数
    hsv_v=0.4,  # 亮度抖动，数据增强参数
    mosaic=1.0,  # Mosaic数据增强的概率
    mixup=0.2,  # Mixup数据增强的概率
    patience=5,  # 早停耐心值，如果验证集指标在15个epoch内没有改善则停止训练
    warmup_epochs=3,  # 学习率预热轮数
    cos_lr=True,  # 使用余弦退火学习率调度器
    augment=True,  # 启用数据增强
    val=True  # 启用验证集评估
)

# 说明：
# - `model.train()` 方法用于训练YOLO模型，参数可以根据具体需求进行调整。
# - `data` 参数指定数据集配置文件路径，该文件应包含训练和验证数据集的路径信息。
# - `imgsz` 参数指定输入图像的大小，较大的图像大小可能提高检测精度，但会增加计算开销。
# - `epochs` 参数指定训练轮数，更多的轮数可能提高模型性能，但会增加训练时间。
# - `batch` 参数指定批量大小，较大的批量大小可以加速训练，但需要更多的GPU内存。
# - `optimizer` 参数指定优化器类型，SGD是一种常用的优化算法。
# - `lr0` 和 `lrf` 参数分别指定初始学习率和最终学习率，学习率调度器会根据这些参数调整学习率。
# - `momentum`、`weight_decay`、`dropout` 等参数用于控制模型的正则化和防止过拟合。
# - `hsv_h`、`hsv_s`、`hsv_v`、`mosaic`、`mixup` 等参数用于数据增强，提高模型的泛化能力。
# - `patience` 参数用于早停，当验证集指标在指定轮数内没有改善时停止训练。
# - `warmup_epochs` 参数指定学习率预热轮数，有助于模型在训练初期稳定收敛。
# - `cos_lr` 参数启用余弦退火学习率调度器，有助于在训练后期微调学习率。
# - `augment` 参数启用数据增强，提高模型的鲁棒性。
# - `val` 参数启用验证集评估，每轮训练后评估模型在验证集上的性能。
```

​	参数详情请参考官方文档：https://docs.ultralytics.com/zh/usage/cfg/

### 3.模型训练

​	我们对模型进行了多次训练，每次训练参数不同，结果有不同程度的变化。这都跟数据增强与否、学习率设置等参数调整，模型复杂度等因素有关。

​	我们先用最小的模型进行训练，进行三次参数的更改，得到不同训练结果。

​	接着发现模型指标虽有提升，但是精度并不高。又考虑到数据集较大，因此采用稍复杂的模型`yolov8s.pt` 进行训练。

### 4.实验结果

| 模型    | **图像大小 (像素)** | mAP50   | mAP50-95 |
| ------- | ------------------- | ------- | -------- |
| yolov8n | 640                 | 0.41488 | 0.22802  |
| yolov8n | 1280                | 0.54889 | 0.31334  |
| yolov8s | 1280                | 0.60755 | 0.35695  |

**F1分数（F1 Score）**：综合考虑精确率和召回率，是精确率和召回率的调和平均数。F1分数用于对精确率和召回率进行整体评价，取值范围介于0和1之间，1代表最佳性能，0代表最差性能。

**IoU（Intersection over Union）**：衡量模型检测出的区域与实际目标区域的重叠程度。IoU是目标检测中常用的指标，用于评估检测框的准确性。

**mAP（mean Average Precision）**：多类别目标检测任务中，各类别的AP的平均值。mAP是目标检测任务中常用的综合评价指标，能够全面反映模型在不同类别上的性能。

**损失函数相关指标**

- **定位损失（box_loss）**：衡量预测框与标注框之间的误差，通常使用GIoU来度量，值越小表示定位越准确。
- **置信度损失（obj_loss）**：计算网络对目标的置信度，通常使用二元交叉熵损失函数，值越小表示模型判断目标的能力越准确。
- **分类损失（cls_loss）**：计算锚框对应的分类是否正确，通常使用交叉熵损失函数，值越小表示分类越准确。

- yolov8n模型（第一次）训练结果：

  ![results](./results2.png)

- yolov8n模型（第二次）训练结果：

  ![results](./results3.png)

- yolov8s模型（第一次）训练结果：

  ![results](./results4.png)

- yolov8s模型（第二次）训练结果：

  ![results](./results.png)

  ![F1_curve](F1_curve.png)

  ​	根据F1-Confidence Curve图，我们可以分析模型对各类目标的检测性能。在理想情况下，F1曲线会接近顶部左侧，表示即使在较低置信度阈值下也能保持较高的F1分数。我们可以观察到，不同类别的F1分数在置信度阈值变化时展现出不同的趋势，这些趋势揭示了模型在识别各类目标时的性能差异。

  ![](confusion_matrix.png)

  ​	混淆矩阵，用于评估多类别分类模型的性能。混淆矩阵展示了模型在各个类别上的预测情况，其中行表示真实类别，列表示预测类别。其中car的预测率较高，但train的预测率就相对很低，这个数据集中目标类别的占比有关，BDD100K数据集中car的占比较大，而train较少。

  ​	由于计算资源有限，只能训练到yolov8s模型，有条件可以尝试后面更复杂的模型进行训练。

------

## **安装与部署**

### 1. **环境要求**

- Python >= 3.9
- FastAPI
- Uvicorn
- OpenCV
- Ultralytics (YOLOv8)
- SQLAlchemy
- PyMySQL
- WebSockets
- requests
- Ollama 本地部署（支持 LLaMA3、Mistral 等模型）

### 2. **安装步骤**

#### 后端（FastAPI）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
 
# 安装依赖
 pip install requirements.txt
```

#### 前端（Vue.js）

```bash
# 进入前端目录
cd ../frontend
 
# 安装依赖
npm install
 
# 启动开发服务器
npm run serve
```

### 3. **模型准备**

- 下载训练好的 YOLOv8 模型权重（`best.pt`）。

- 或使用自定义数据集训练模型，参考 [Ultralytics YOLOv8 文档](https://docs.ultralytics.com/)。

  ```python
  #请在yolo_model.py文件里修改
  model = YOLO(r'D:\python\bestyolo\ultralytics\Carscanner\runs\detect\train2\weights\best.pt').to(
      'cuda' if torch.cuda.is_available() else 'cpu')
  
  #请按照自己的模型所在文件路径修改
  ```

  

### 4. **启动服务**

###### 请在对应的目录下进行操作

#### 后端

##### bash复制代码：

```bash
# 启动后端
uvicorn main:app --host 127.0.0.1 --port 8000
# 启动法规模型
ollama run llama3 #请更改为自己的模型
```

#### 前端

```bash
bash复制代码

npm run serve
```

------

## **API 文档**

### 1. **API 接口**

```
POST /upload
```

- 上传图像：

  - 参数：图像文件（image/jpeg）
  
  - 返回：JSON 格式的检测数据（含base64格式的二进制形式的图片）

    ###### 示例：

    ```json
    {
      "confidence": 0.5,
      "iou": 0.5,
      "image": "<Base64 编码图像>",
      "detections": {
        "0": {
          "class_id": 0,
          "class_name": "car (0.98)",
          "targets": [{"x": 123, "y": 456, "confidence": 0.98}],
          "count": 1
        }
      }
    }
    ```
  
- 视频检测：

  - 参数：视频文件（video/mp4）
  
  - 返回：JPEG 编码图像的二进制帧和JSON 格式的检测数据

    ###### 示例：

    ```json
    {
      "confidence": 0.5,
      "iou": 0.5,
      "stream_id": "uuid1234-..."
    }
    ```
  



```
POST /set_conf_lou
```

- 上传置信度和交并比：	

  - 参数：conf和iou(都为float类型)

  - 返回：JSON 格式的提示数据

    ###### 示例：

    ```
    {
      "message": “配置更新成功”,
      "conf": 0.5,
      "iou": 0.7
    }
    ```



```
POST /get_detection_data
```

- 上传每日数据：	

  - 参数：查询的日期date

  - 返回：JSON 格式的每日统计数据

    ###### 示例：

    ```
    {
      "success": True,
      "data":{
            "detection_id": 1,
            "processed_file": processed_images\20250414_172047.jpg,
            "bus": 0,
            "trafficlight": 0,
            "trafficsign": 0,
            "person": 5,
            "bike": 0,
            "truck": 0,
            "motor": 0,
            "car":30,
            "train": 0,
            "rider": 0,	
            "conf": 0.5
      }
    }
    ```

    

```
Websocket /ws/{stream_id}
```

- 建立连接，处理视频：	
  - 参数：websocket和前面生成的stream_id
  - 调用：视频处理函数process_video_stream()



```
Websocket /camera
```

- 建立连接，处理实时视频（摄像头）：	
  - 参数：websocket
  - 调用：处理函数process_and_send_frames()



```
Websocket /api
```

- 建立连接，调用微调模型，回答交规相关问题：	

  - 参数：websocket

  - 返回：微调模型返回的response结果

    ###### 示例：

    ```
    user：驾驶机动车时未随车携带驾驶证，应受到何种处罚？
    system：根据《道路交通安全法》第95条，未随车携带驾驶证属于违法行为，但不同于无证驾驶。需核查是否能够及时提供有效证件，处罚方式会根据具体情况而定。 根据《道路交通安全法》第95条，可处警告或20-200元罚款，并扣留机动车至违法状态消除。若能及时提供有效驾驶证，处罚可减轻。
    ```

    

### 2. **示例请求**

```bash
curl -X POST "http://127.0.0.1:8080/upload" \
-F "file=@path/to/image.jpg"
##jpg图片也可改成MP4格式的视频
```

------

## 数据库存储说明

- 每次检测都会记录 `检测ID`、源文件名、处理后文件名、提示语、检测时间
- 每 5 秒检测一次左右侧或预警区内的目标，统计 `warning_count`
- 每日形成汇总表，记录当天总检测数、预警数与所有记录ID

#### 数据库配置

###### 请在db.py中将以下代码修改：

```
DATABASE_URL = "mysql+pymysql://root:yx220111@localhost:3306/traffic_db"
#请修改为自己的数据库 用户名，密码以及对应的ip和端口
```



## **前端界面说明**

1. 主页

   - 上传图像/视频、上传文件夹、打开摄像头按钮。
   - 检测结果展示区域。
2. 配置页面
   - 选择置信度阈值等参数。
3. 结果页面

   - 可视化检测结果，包括目标边界框和标签。
   - 数据可视化展示，用表格和柱形图展示与统计目标检测，帮助了解图像中各类目标的分布情况。
------

## **项目结构**

```
yolov8-autonomous-driving/
├── backend/
│   ├── main.py          # FastAPI 主程序
│   ├── models.py        # 数据库的汇总表模型
│   ├── crud.py			 # 插入 / 查询 / 动态建表逻辑
│   ├── db.py			 # 数据库连接
│   ├── Processing.py 	 # 处理函数
│   ├── set_iou_conf.py  # 置信度和交并比的设置
│   ├── state.py 	 	 # 存储websocket链接和线程池
│   ├── yolo_model.py 	 # 调用微调模型回答程序
│   ├── models/  		 # YOLOv8 模型相关代码
│   └── requirements.txt # 后端依赖
├── frontend/
│   ├── public/          # 静态资源
│   ├── src/             # Vue.js 源代码
│   └── package.json     # 前端依赖
├── README.md            # 项目说明文档
└── weights/             # 模型权重文件
```

------

