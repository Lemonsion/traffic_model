<template>
  <el-card>
    <div class="chat-box" ref="chatBox">
      <!-- 欢迎信息，初始显示，发送第一条消息后隐藏 -->
      <div v-if="showWelcome" class="welcome-message">
        <img :src="robot" class="robot_icon" />
        欢迎使用交通知识科普问答工具！
      </div>
      <div v-for="(msg, index) in messages" :key="index" class="message">
        <div v-if="msg.type === 'user'" class="user-message">
          <img :src="avatar" alt="User" class="avatar_user" />
          <div class="message-content user-message-content">{{ msg.content }}</div>
        </div>
        <div v-if="msg.type === 'bot'" class="bot-message">
          <img :src="avatar_bot" alt="Bot" class="avatar" />
         <div class="message-content bot-message-content" v-html="msg.content"></div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <el-input
        v-model="input"
        :placeholder="isThinking ? '正在思考中，请稍候...' : '请输入您的问题...'"
        :disabled="isThinking"
        @keyup.enter="sendMessage"
        class="input-field"
        :style="{ width: '100%' }"
      ></el-input>
       <!-- 圆形语音输入按钮 -->
      <el-button
        :type=" isRecording ?  'danger' : (isDarkTheme ? 'info' : 'primary')"
        :disabled="isThinking "
        @click="toggleRecording"
        class="recording-button"
        circle
      >
        <!-- 引入并使用麦克风图标 -->
        <el-icon v-if="!isRecording" class="microphone-icon">
          <mic />
        </el-icon>
        <el-icon v-if="isRecording" class="microphone-icon">
          <mic />
        </el-icon>
      </el-button>
      <el-button
          :type=" isDarkTheme ? 'info' : 'primary'"
         :disabled="isThinking || input.trim() === ''"
         @click="sendMessage">发送</el-button>
    </div>
  </el-card>
</template>
<script>

import { marked } from 'marked';

export default {
  data() {
    return {
      input: '', // 用户输入
      messages: [], // 消息列表
      avatar: require('@/assets/img.png'), // 用户头像
      avatar_bot: require('@/assets/logo.png'), // 机器人头像
      robot: require('@/assets/robot.png'), // 机器人图标
      showWelcome: true, // --------------控制是否显示欢迎信息-------------
      isRecording: false, // --------------录音状态-------------
      recognition: null, // 语音识别对象
      loadingTimer: null, // 动态加载点
      isThinking: false, // 是否正在思考中
      stream: null, // 麦克风音频流对象
      isDarkTheme: document.body.classList.contains('dark-theme'), // 主题模式
    };
  },
  mounted() {
    // --------------初始化时检查主题-------------
    this.updateTheme();

    // --------------监听主题变化-------------
    const observer = new MutationObserver(this.updateTheme);
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class'],
    });
    console.log('isDarkTheme:', this.isDarkTheme);
  },
  methods: {
    // --------------更新主题的方法-------------
    updateTheme() {
      this.isDarkTheme = document.body.classList.contains('dark-theme');
    },

    // --------------处理用户输入并发送到 WebSocket 请求-------------
    handleUserInput(userInput) {
      this.isThinking = true;

      // 添加用户消息
      this.messages.push({ type: 'user', content: userInput });
      this.scrollToBottom();

      // 添加“正在思考中”占位
      this.messages.push({ type: 'bot', content: '正在思考中' });
      const loadingIndex = this.messages.length - 1;

      // 启动“...”动态加载提示
      let dotCount = 1;
      this.loadingTimer = setInterval(() => {
        const dots = '.'.repeat(dotCount);
        this.messages[loadingIndex].content = `正在思考中${dots}`;
        dotCount = (dotCount % 3) + 1;
        this.scrollToBottom();
      }, 500);

      // 调用统一的 WebSocket 请求函数
      this.sendWebSocketRequest(
        userInput,
        (data) => {
          clearInterval(this.loadingTimer);
          this.isThinking = false;

          const content = data;
          let index = 0;
          this.messages[loadingIndex].content = '';  // 先清空

          const typingInterval = setInterval(() => {
            if (index < content.length) {
              this.messages[loadingIndex].content += content[index];
              index++;
              this.scrollToBottom();
            } else {
              clearInterval(typingInterval);

              // 渲染 Markdown
              this.messages[loadingIndex].content = marked.parse(content);
              this.scrollToBottom();
            }
          }, 30); // 每 30ms 输出一个字符，可调节速度
        }
      );
    },

    // --------------发送消息-------------
    sendMessage() {
      if (this.input.trim() === '') return;
      this.showWelcome = false;
      const userInput = this.input;
      this.input = '';
      this.handleUserInput(userInput);
    },

    // --------------WebSocket 请求函数-------------
    sendWebSocketRequest(userInput, onResponse, onError) {
      const socket = new WebSocket("ws://127.0.0.1:8000/api");

      socket.onopen = () => {
        socket.send(userInput); // 发送消息
      };

      socket.onmessage = (event) => {
        onResponse(event.data); // 处理返回数据
        socket.close();
      };

      socket.onerror = (error) => {
        onError(error); // 处理错误
        socket.close();
      };
    },

    // --------------切换录音状态-------------
    toggleRecording() {
      if (this.isToggling) return;  // 防止短时间内重复切换
      this.isToggling = true;

      if (this.isRecording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }

      setTimeout(() => {
        this.isToggling = false;
      }, 500);  // 0.5 秒内不能再次切换
    },

    // --------------开始录音-------------
    startRecording() {
      if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
        alert("语音识别不支持！");
        return;
      }

      this.isRecording = true;
      this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      this.recognition.lang = 'zh-CN';

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript.trim() === '') return;
        this.showWelcome = false;
        this.handleUserInput(transcript);
      };

      this.recognition.onend = () => {
        this.isRecording = false;
      };

      this.recognition.start();
    },

    // --------------停止录音-------------
    stopRecording() {
      if (this.recognition) {
        this.recognition.stop(); // 停止录音
        this.isRecording = false;
      }
    },

    // --------------滚动到底部-------------
    scrollToBottom() {
      this.$nextTick(() => {
        this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight;
      });
    }
  }
};
</script>


<style scoped>
.el-card {
display: flex;
flex-direction: column;
justify-content: center; /* 垂直居中 */
transform: translate(40px, 20px); /* 越小越向左,越小越向上 */
  border-radius: 10px;
  background-color:  rgb(236, 244, 250);
}


.chat-box {
  height: 650px;  /* 调整聊天框的高度 */
  overflow-y: auto;
  padding: 10px;
  border-bottom: 1px solid #dcdfe6;
  border: 2px dashed #dcdfe6; /* 添加虚线边框 */
  width: 100%; /* 这里确保聊天框宽度为100% */
  box-sizing: border-box; /* 包括边框和内边距 */
}

  body.dark-theme .el-card {
    background-color: rgb(227, 232, 235);
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 25px;
  color: rgba(85, 85, 85, 0.8);
  font-weight: 600;
}

.input-area {
  display: flex;
  align-items: center;
  margin-top: 10px;
  width: 100%;
}

.message {
  margin: 10px 0;
  display: flex;
  align-items: center;
}

.user-message{
  margin-top: 2px;
  display: flex;
  align-items: flex-start; /* 顶部对齐头像和消息 */
}

.bot-message {
  margin-top: 2px;
  display: flex;
  align-items: flex-start; /* 顶部对齐头像和消息 */
}

.robot_icon{
  width: 40px;
  height: 40px;
}

.avatar{
  border-radius: 50%;
  margin-right: 10px;
  width: 38px;
  height: 38px;

}
.avatar_user{
  border-radius: 50%;
  margin-right: 10px;
  width: 35px;
  height: 35px;
}

.input-field {
  flex: 1;
  margin-right: 10px;
  max-width: calc(100% - 100px);
}

.message-content {
  max-width: 100%; /* 确保消息内容框不超过聊天框宽度 */
  background-color: #f0f0f0; /* 随意选择背景颜色 */
  padding: 10px; /* 内边距 */
  overflow-wrap: break-word; /* 使长文本换行 */
  white-space: normal; /* 允许文本在标签内换行 */
  word-wrap: break-word; /* 兼容旧版浏览器 */
}

.user-message-content {
  background-color: #d1e7dd; /* 用户消息的背景颜色 */
  font-size: 13px;   /* 设置字体大小 */
}

.bot-message-content {
  background-color: #cfe2ff;
  font-size: 13px;
}

.recording-button {
  margin-left: 10px;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  border-radius: 50%;
}

.recording-button.primary {
  background-color: #007bff;
  color: white;
}

.recording-button.danger {
  background-color: #dc3545;
  color: white;
}

/* 通过类名增加加粗样式 */
.microphone-icon {
  font-weight: bold;
  font-size: 25px; /* 设置图标的大小 */
}
</style>
