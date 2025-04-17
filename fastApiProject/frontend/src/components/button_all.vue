<template>
  <div>
    <div class="control-buttons">
      <el-button class="custom-blue" icon="Files" @click="selectProjectFile" size="medium">选择项目文件</el-button>
      <el-button class="custom-blue" icon="Camera" @click="startRealTimeCamera" size="medium">启动实时摄像</el-button>
      <el-button class="custom-blue" icon="Close" @click="stopRealTimeCamera" size="medium">停止摄像</el-button>
      <!-- 隐藏原生的文件选择框 -->
      <input type="file" id="fileInput" accept="image/*,video/*" style="display: none;" @change="handleFileSelect">
      </div>
      <div class="wrapper">
        <div class="alarm_header">
        </div>
        <div class="previewContainer">
          <img id="imagePreview" style="display: none; width: 750px; height: 750px;" />
          <video id="videoPreview" style="display: none;width: 750px; height: 750px;" controls></video>
        </div>
        <div class="processedContainer">
          <img id="processedImage" style="display:none;width: 750px; height: 750px;">
          <canvas id="processedCanvas" style="display:none; width: 750px; height: 750px;"></canvas>
          <canvas id="processedCamera" style="display:none; width: 750px; height: 750px;"></canvas>
        </div>
        <!-- 新增虚线方框和文本 -->
        <div class="dashed-box" id="dashedBox" style="display: block;">
          请先上传图片或视频！
        </div>
            <div class="control-buttons1">
          <el-button class="custom-blue" @click="processFile()" >处理</el-button>
          <el-button class="custom-blue" @click="stopWebSocket()">停止</el-button>
        </div>
      </div>
  </div>
</template>
  
  <script>
  import { ElButton } from 'element-plus';

  // import { useRouter } from 'vue-router'
  let uploadedFile = null;
  let streamId = null;
  let ws = null; // WebSocket 变量
  // let currentTime = 0; // 用于存储当前播放时间
  let canUpdateAlarm = true;  // 控制是否可以继续语音播报和提示
  // let isPaused = false; // 用于控制是否暂停绘制
  // let drawInterval = null; // 存储定时器ID，以便在暂停时清除
  const typeMapping = {
  person: "人",
  car: "小汽车",
  bike:"自行车 ",
    bus:"公交车",
    light:"路灯",
    truck:"卡车",
    traffic:"标志牌",
    motor:"摩托车",
    rider:"骑手",
    train:"火车",
  // 可以根据需求继续添加更多类型
};

  export default {
  components: {
    ElButton,
  },
    data() {
    return {
      isImage: false,  // 标记是否是图片文件
      isVideo: false,  // 标记是否是视频文件
    };
  },
  methods: {
    // 选择项目文件的逻辑，触发文件选择框
    selectProjectFile() {
// 触发文件选择框
      document.getElementById("fileInput").click();
    },

    // 启动实时摄像头的逻辑
    startRealTimeCamera() {
       if (!ws || ws.readyState === WebSocket.CLOSED) {  // 只在没有连接时初始化
      alert('启动实时摄像');
      const ws = new WebSocket("ws://localhost:8000/camera");

      ws.binaryType = "arraybuffer"; // 接收后端发来的图像帧（binary）

      ws.onopen = () => {
        // 发送命令启动摄像头
        ws.send("start_camera");
      };

      ws.onmessage = (event) => {
        console.log("收到消息:", event.data);  // 🔍 确认类型和数

        // 处理 JSON 数据（检测信息）
        if (typeof event.data === "string") {
          try {
            const detections = JSON.parse(event.data);
            console.log("检测到json信息", detections);
            const detectionsArray2 = Array.isArray(detections.detections) ? detections.detections : Object.values(detections.detections);
            this.updateTarget(detectionsArray2);
            this.updateTotality(detectionsArray2);
            this.updateAlarm(detectionsArray2);
            // 在这里更新目标框、标签等，处理检测信息
          } catch (error) {
            console.error("解析 JSON 错误:", error);
          }
        }

        // 处理视频帧（binary data）
        else if (event.data instanceof ArrayBuffer) {
          console.log("检测到图片信息");

          const blob = new Blob([event.data], { type: "image/jpeg" });
          const imgUrl = URL.createObjectURL(blob);

          const processCamera = document.getElementById("processedCamera");
          const processCanvas = document.getElementById("processedCanvas");
          const processedImg = document.getElementById("processedImage");
          const previewImg = document.getElementById("imagePreview");
          const previewVideo = document.getElementById("videoPreview");
          const dashedBox = document.getElementById("dashedBox");
          const ctx = processCamera.getContext("2d");

          const img = new Image();

          img.onload = () => {
            // 设置 canvas 大小为图像尺寸
            processCamera.width = img.width;
            processCamera.height = img.height;

            // 渲染函数
            const renderFrame = () => {
              ctx.clearRect(0, 0, processCanvas.width, processCanvas.height);  // 清除画布
              ctx.drawImage(img, 0, 0);  // 绘制图像

              // 请求下一帧
              requestAnimationFrame(renderFrame);
            };

            renderFrame();  // 启动渲染
          };
          img.src = imgUrl;

            // 显示 canvas 并隐藏其他元素
            processedImg.style.display = "none";
            previewImg.style.display = "none";
            previewVideo.style.display = "none"; // 隐藏视频预览
            processCamera.style.display = "block";
            processCanvas.style.display = "none";
            dashedBox.style.display = "none";
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket 发生错误:", error);
        };

        ws.onclose = () => {
          console.log("WebSocket 连接关闭");
        };
      }
    },

    // --------------停止实时摄像头-------------
    stopRealTimeCamera() {
      const ws = new WebSocket("ws://localhost:8000/camera");
      ws.onopen = () => {
        // alert("发送摄像头停止命令");
          ws.send("stop_camera"); // 发送命令启动摄像头
      };

      ws.onmessage = (event) => {
      console.log("收到消息:", event.data);
      if (event.data === "摄像头已停止") {
          alert("摄像头已停止");
          this.$emit('clearTotalities');
          this.$emit('clearTargets');
          // 在前端停止摄像头画面显示
          const processCamera = document.getElementById("processedCamera");
          const dashedBox = document.getElementById("dashedBox");
          dashedBox.style.display="block";
          processCamera.style.display = "none";  // 停止显示摄像头画面
      }
    };

      ws.onerror = (error) => {
        console.error("WebSocket 错误:", error);
      };

      ws.onclose = () => {
        console.log("WebSocket 连接已关闭");
      };
    },

    // --------------更新语音报警-------------
      updateAlarm(detections) {
  if (!canUpdateAlarm) return;

  let messages = [];

  detections.forEach(detection => {
    detection.targets.forEach(target => {
      const site = target.site;
      const type = detection.class_name;
      const typeName = type.split(' ')[0];
      const chineseType = typeMapping[typeName] || typeName;

      if (site === '右侧') {
        messages.push(`右方${chineseType}`);
      } else if (site === '左侧') {
        messages.push(`左方${chineseType}`);
      }
    });
  });

  if (messages.length === 0) return;

  const uniqueMessages = [...new Set(messages)];
  const alarmMessage = `请注意${uniqueMessages.join('、')}！`;

  let alarmHeader = document.querySelector('.alarm_header');
  alarmHeader.textContent = alarmMessage;

  const utterance = new SpeechSynthesisUtterance(alarmMessage);
  utterance.lang = 'zh-CN';
  utterance.onend = () => {
    alarmHeader.textContent = '';
  };
  window.speechSynthesis.speak(utterance);

  canUpdateAlarm = false;
  setTimeout(() => {
    canUpdateAlarm = true;
  }, 3000);
},


    // --------------更新检测总数-------------
    updateTotality(detections) {
      this.$emit('clearTotalities');
      let newTotalities = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

      detections.forEach(detection => {
        newTotalities[detection.class_id] = detection.count;
      });

      this.$emit('updateTotalities', newTotalities);
    },

    // --------------更新目标-------------
    updateTarget(detections) {
      let number = 1;  // 初始化计数器，从1开始
      this.$emit('clearTargets');
      detections.forEach(detection => {
        detection.targets.forEach(target => {
          const confidence = target.confidence;  // 置信度
          const x = target.x;  // 目标的 x 坐标
          const y = target.y;  // 目标的 y 坐标
          const type = detection.class_name;  // 目标的类型（类别）
          const typeName = type.split(' ')[0]; // 获取 "person" 或 "car" 部分
          const chineseType = typeMapping[typeName] || typeName;

          // 将每个目标的详细信息通过事件发送出去
          this.$emit('sendDataToApp', {
            id: number++,
            type: chineseType,
            location: `(${x}, ${y})`,  // 传递位置作为对象
            confidence: confidence
          });
        });
      });
    },

    // --------------处理文件上传-------------
    processFile() {
      if (!uploadedFile) {
        alert("请先上传文件！");
        return;
      }
      let formData = new FormData();
      formData.append("file", uploadedFile);
      fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
        mode: "cors",
        credentials: "include"
      })

      .then(response => response.json())
      .then(data => {
        if (data.stream_id) {
          // 服务器返回 stream_id，启动 WebSocket 连接
          streamId = data.stream_id;
          this.isVideo = true;  // 设置为视频
          this.isImage = false;  // 确保不是图片
          this.startWebSocket(streamId);
        } else if (data.image) {
          // 处理返回的图片数据
          this.isImage = true;  // 设置为图片
          this.isVideo = false;  // 确保不是视频
          let processedImg = document.getElementById("processedImage");
          let previewImg = document.getElementById("imagePreview");
          let previewVideo = document.getElementById("videoPreview");
          let processCanva = document.getElementById("processedCanvas");
          let processCamera = document.getElementById("processedCamera");
          let dashedBox = document.getElementById("dashedBox");
          processedImg.src = `data:image/jpeg;base64,${data.image}`;
          processedImg.style.display = "block";
          previewImg.style.display = "none";
          previewVideo.style.display = "none"; // 隐藏视频预览
          processCanva.style.display="none";
          processCamera.style.display="none";
          dashedBox.style.display = "none";
          const detectionsArray = Array.isArray(data.detections) ? data.detections : Object.values(data.detections);
          this.updateTarget(detectionsArray);
          this.updateTotality(detectionsArray);
          this.updateAlarm(detectionsArray);
        }


    console.log("JSON 数据:", data);
      })
      .catch(error => console.error("错误:", error));
    },

    // WebSocket启动的函数
    startWebSocket(streamId) {
        if (ws && ws.readyState !== WebSocket.CLOSED) {
            console.log("WebSocket 已经连接，无需重新连接");
            return;
          }

      if (ws) {
        ws.close();
        ws=null;
      }

      ws = new WebSocket(`ws://localhost:8000/ws/${streamId}`);
      let previewImg = document.getElementById("imagePreview");
      let processImg = document.getElementById("processedImage");
      const canvas = document.getElementById("processedCanvas");
      const camera = document.getElementById("processedCamera");
      let dashedBox = document.getElementById("dashedBox");
      const ctx = canvas.getContext("2d");
      previewImg.style.display = "none";
      processImg.style.display="none";
      canvas.style.display = "block";
      camera.style.display = "none";
      dashedBox.style.display = "none";
      // // 设置视频当前时间为停止时的时间点
      // previewVideo.currentTime = currentTime;
      // 引入一个计数器来统计帧数
      let frameCount = 0;

      // 当收到消息时处理
      ws.onmessage =  (event) => {
        if (event.data === "completed") {
          console.log("视频处理完成，关闭 WebSocket");
          this.$emit('clearTargets');
          this.$emit('clearTotalities');
          ws.close();
          return;
        }
        if(canvas.style.display == "none") // 如果视频被关闭，则不处理
        {
          console.log("视频处理完成，关闭 WebSocket");
          this.$emit('clearTargets');
          this.$emit('clearTotalities');
          ws.close();
          return;
        }
        if (event.data instanceof Blob) {
          let blob = new Blob([event.data], { type: "image/jpeg" });
          let img = new Image();
          img.onload = function() {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
          }
           img.src = URL.createObjectURL(blob);
        }
        else if (typeof event.data === "string") {
          try {
            const data = JSON.parse(event.data);
            console.log("detections:", data.detections);
            const detectionsArray1 = Array.isArray(data.detections) ? data.detections : Object.values(data.detections);

            // 仅在是视频时处理每一帧
            if (this.isVideo) {
              this.updateTarget(detectionsArray1);
              this.updateTotality(detectionsArray1);
              // 每十帧调用一次 this.updateAlarm
              frameCount++;
              if (frameCount % 20 === 0) {
                this.updateAlarm(detectionsArray1);
              }
            }
             // 遍历 detections 数组
          } catch (error) {
            console.error("JSON 解析错误:", error);
          }
        } else {
          console.warn("收到未知类型的数据:", event.data);
        }
      };

      ws.onclose = ()=> {
        console.log("WebSocket 连接关闭");
      };

      ws.onerror = (error) => {
        console.error("WebSocket 发生错误:", error);
        // 在发生错误时尝试重新连接
        setTimeout(() => {
          console.log("尝试重新连接 WebSocket");
          this.startWebSocket(streamId);  // 这里的 `this` 就是 Vue 组件实例
        }, 3000); // 3秒后尝试重新连接
      };

      // 启动WebSocket连接的逻辑
      console.log('启动WebSocket连接，Stream ID:', streamId);
    },

// 暂停处理帧
stopWebSocket() {
  if (ws) {
    ws.close();
    ws = null;  // 确保 ws 被置为 null
    console.log("关闭连接");
  }

        canUpdateAlarm = false; // 禁止继续更新警告信息
        window.speechSynthesis.cancel(); // 取消语音播报
        let alarmHeader = document.querySelector('.alarm_header');
        alarmHeader.textContent = " ";

  let previewVideo = document.getElementById("videoPreview");
  previewVideo.pause();  // 暂停视频播放
},

    handleFileSelect(event) {
      let file = event.target.files[0];
      if (!file) return;
      uploadedFile = file; // 存储文件，供后续处理
      streamId = null; // 重置 streamId
      let alarmHeader = document.querySelector('.alarm_header');
      alarmHeader.textContent = " ";
      // 清除之前的预览内容
      // 可以根据需要处理所有文件
      let previewImg = document.getElementById("imagePreview");
      let previewVideo = document.getElementById("videoPreview");
      let processImg = document.getElementById("processedImage");
      let processCanva = document.getElementById("processedCanvas");
      let processCamera = document.getElementById("processedCamera");
      let dashedBox = document.getElementById("dashedBox");
      let fileURL = URL.createObjectURL(file);
      this.$emit('clearTargets');
      this.$emit('clearTotalities');
      if (file.type.startsWith("image/")) {
                previewImg.src = fileURL;
                previewImg.style.display = "block";
                previewVideo.style.display = "none"; // 隐藏视频预览
                processImg.style.display="none";
                processCanva.style.display="none";
                processCamera.style.display="none";
                dashedBox.style.display = "none";
            }
       else if (file.type.startsWith("video/")) {
                previewVideo.src = fileURL;
                previewVideo.style.display = "block";
                previewImg.style.display = "none"; // 隐藏图片预览
                processCanva.style.display="none";
                processImg.style.display="none";
                processCamera.style.display="none";
                dashedBox.style.display = "none";
            }
    }
  },
};
</script>
  
  <style scoped>
  .control-buttons {
    display: flex;
    flex-direction: column; /* 设置为竖直方向 */
    align-items: flex-start; /* 保证按钮在水平方向上居中 */
    width: 195px; /* 调整区域宽度 */
    height: 1250px; /* 调整区域高度为视口高度 */
    background-color: rgb(236, 244, 250); /* 设置背景框的颜色 */
    padding: 40px; /* 增加内边距使背景框更明显 */
    box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); /* 背景框的阴影效果 */
    position: absolute;
    left:8px; /*使左侧背景被铺满*/
    top:20px;
    margin-top: 45px; /*调整高度，越小越高*/
  }

  body.dark-theme .control-buttons {
  background-color: rgb(227, 232, 235);
}

  .control-buttons button {
    margin: 20px 0; /* 按钮之间的间隔 */
    width: 180px; /* 设置按钮宽度 */
  }
  .custom-blue {
    background-color: #347ec6; /* 蓝色背景 */
    color: white; /* 白色文本 */
  }

    body.dark-theme .custom-blue {
  background-color: rgb(48, 82, 119);
}

   .control-buttons1 {
    display: flex;
    flex-direction: row; /* 设置为水平方向 */
    align-items: flex-start; /* 保证按钮在水平方向上居中 */
    height: 100px;
    position: absolute;
  }
     .control-buttons1 button {
    margin: 400px 60px; /* 第一个参数可调整按钮高度 第二个参数可调按钮间距 */
    width: 200px; /* 设置按钮宽度 */
  }

  .wrapper {
    position: absolute;
    background-color:  rgb(236, 244, 250); /* 设置背景框的颜色 */
    padding: 20px; /* 增加内边距使背景框更明显 */
    border-radius: 10px; /* 圆角 */
    box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); /* 背景框的阴影效果 */
    height: 800px; /* 设置与图片相同的高度 */
    width: 1070px; /* 设置与图片相同的宽度 */
    display: flex;
    justify-content: center;
    align-items: center;
    transform: translate(-220px, -60px);/*越大越下*/
  }

  body.dark-theme .wrapper {
  background-color: rgb(227, 232, 235);
}

  .alarm_header{
  position: absolute;
  top: 20px; /* 根据需要调整距离顶部的位置 */
  left: 50%; /* 水平居中 */
  transform: translateX(-50%); /* 确保水平居中 */
  font-size: 22px; /* 根据需要调整字体大小 */
  font-weight: 600;
  color: #c60d21;
}


  /* 虚线方框样式 */
  .dashed-box {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border: 2px dashed rgba(136, 136, 136, 0.42);
    padding: 20px;
    font-size: 14px;
    color: #888888;
    background-color: rgba(255, 255, 255, 0.7);
    text-align: center;
    border-radius: 5px;
    width: 80%; /* 可调整大小 */
    height: 70%;
    box-sizing: border-box;
}

#imagePreview,
#videoPreview,
#processedImage,
#processedCanvas ,
#processedCamera{
    object-fit: contain;  /* 保持图片比例 */
    position: absolute;
    max-width: 100%;
    max-height: 100%;
    transform: translate(-400px, -430px);
}

  </style>
  