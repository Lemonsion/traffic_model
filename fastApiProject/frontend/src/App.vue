<template>
  <div id="app">
    <!-- 背景和透明遮罩层 -->
    <div class="background">
      <div class="overlay">
        <div class="container">
          <header class="header">
            <img src="@/assets/drive.png" class="drive_icon" alt="Drive Icon" />
            <h1>自动驾驶目标检测系统</h1>
            <nav class="menu">
              <router-link to="/" class="menu-item_main">首页</router-link>
              <router-link to="/systemview" class="menu-item_main">进入系统</router-link>
              <router-link to="/chatview" class="menu-item_main">交规助手</router-link>
              <router-link to="/dataview" class="menu-item_main">数据视图</router-link>

              <!-- 右侧菜单项 -->
  <div class="menu-right">
    <a role="button" class="menu-item" id="theme-toggle">
      <img src="@/assets/moon.png" alt="浅色/深色模式" class="menu-icon"> 浅色/深色模式
    </a>
    <a role="button" class="menu-item" id="about-us-toggle">
      <img src="@/assets/info.png" alt="关于我们" class="menu-icon">关于我们
    </a>
    <a role="button" class="menu-item" id="feature-toggle">
      <img src="@/assets/help.png" alt="功能介绍" class="menu-icon">功能介绍
    </a>
  </div>
            </nav>
          </header>
        <!-- 包裹 router-view 的 div -->
          <div class="router-view-wrapper">
            <router-view></router-view>
          </div>

      <!-- 关于我们弹窗部分 -->
      <div id="about-us-modal" class="modal">
          <div class="modal-content">
              <span class="close-btn" id="close-about-us">&times;</span>
              <h2>关于我们</h2>
              <p class="indent-text">我们是一个由多名热衷于人工智能和自动驾驶技术的成员组成的团队。我们的项目目标是研发一套高效、精准的自动驾驶目标检测系统，为自动驾驶技术的发展贡献力量。</p>
              <p class="indent-text">在这个项目中，我们结合了先进的计算机视觉技术和深度学习算法，设计并实现了一个可以实时检测和识别自动驾驶过程中遇到的各种目标的系统。该系统能够在复杂的道路环境中，快速准确地识别行人、其他车辆、交通标志、障碍物等关键目标，从而帮助自动驾驶车辆做出智能决策，提高行车安全性。</p>
              <p class="indent-text">通过这个项目，我们不仅提升了团队成员在自动驾驶领域的技术能力，也为自动驾驶技术的普及和应用提供了有力的技术支持。我们相信，随着技术的不断进步，自动驾驶将在未来的交通运输中发挥重要作用，我们的目标检测系统将是实现这一愿景的重要组成部分。</p>
          </div>
      </div>

           <!-- 功能介绍的弹窗部分 -->
        <div id="feature-modal" class="modal">
          <div class="modal-content">
            <span class="close-btn" id="close-feature">×</span>
            <h2>功能介绍</h2>
            <p class="indent-text">自动驾驶目标检测系统是一种高效、智能的技术解决方案，专为自动驾驶领域设计，能够提供多种实时监控和数据处理功能。系统支持静态检测、视频检测以及实时监控，能够精准识别周围环境中的各种目标，确保驾驶安全。系统不仅具备强大的目标检测能力，还能通过智能分析提供详细的数据统计，包括表格和柱形图的展示，帮助用户清晰了解检测结果。同时，系统支持调节检测精度，用户可以根据需求自定义调整检测的Conf值和IoU值，以优化目标检测效果。</p>
            <p class="indent-text">此外，系统内置语音播报功能，能够实时反馈检测状态，及时提醒用户异常情况。页面弹窗提示和AI语音交互功能，使得用户在操作过程中更加便捷、直观。在数据管理方面，系统提供了全面的AI问答数据看板，实时显示总检测数、当日检测数以及预警数等重要信息，为管理人员提供实时的数据监控和预警功能，助力决策和安全管理。综合来看，该系统在提高自动驾驶的智能化、安全性和便捷性方面，具有极大的优势。</p>
          </div>
        </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
    methods: {

    // 切换主题的方法
    toggleTheme() {
      document.body.classList.toggle("dark-theme");
    },

    // 显示“功能介绍”弹窗
    showFeatureModal() {
      const modal = document.getElementById('feature-modal');
      modal.style.display = "block"; // 显示弹窗
    },

    // 显示“关于我们”弹窗
    showAboutUsModal() {
      const modal = document.getElementById('about-us-modal');
      modal.style.display = "block"; // 显示弹窗
    },

    // 关闭弹窗的方法
    closeModal(modalId) {
      const modal = document.getElementById(modalId);
      modal.style.display = "none"; // 隐藏弹窗
    },

    // 点击弹窗外区域也关闭弹窗
    handleWindowClick(event) {
      const aboutUsModal = document.getElementById('about-us-modal');
      const featureModal = document.getElementById('feature-modal');
      if (event.target === aboutUsModal) {
        aboutUsModal.style.display = "none";
      }
      if (event.target === featureModal) {
        featureModal.style.display = "none";
      }
    },
  },
    mounted() {
    // 在组件挂载后添加事件监听器
    const toggleButton = document.getElementById("theme-toggle");
    const aboutUsToggle = document.getElementById('about-us-toggle');
    const featureToggle = document.getElementById('feature-toggle');
    const closeAboutUsBtn = document.getElementById('close-about-us');
    const closeFeatureBtn = document.getElementById('close-feature');

    // 确保按钮和事件存在
    if (toggleButton) {
      toggleButton.addEventListener("click", this.toggleTheme);
    }

    if (aboutUsToggle) {
      aboutUsToggle.addEventListener("click", this.showAboutUsModal);
    }

    if (featureToggle) {
      featureToggle.addEventListener("click", this.showFeatureModal);
    }

    if (closeAboutUsBtn) {
      closeAboutUsBtn.addEventListener("click", () => this.closeModal('about-us-modal'));
    }

    if (closeFeatureBtn) {
      closeFeatureBtn.addEventListener("click", () => this.closeModal('feature-modal'));
    }

    // 点击窗口外区域关闭弹窗
    window.addEventListener("click", this.handleWindowClick);
  },

   beforeUnmount() {
    // 在组件销毁之前移除事件监听器
    const toggleButton = document.getElementById("theme-toggle"); // 确保ID一致
    if (toggleButton) {
      toggleButton.removeEventListener("click", this.toggleTheme);
    }
  },
}
</script>

<style scoped>
/* 背景和透明遮罩层 */
.background {
  position: relative;
  width: 100%;
  height: 100vh;
  background-image: url('@/assets/background.png'); /* 背景图片 */
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.6); /* 透明白色遮罩层 */
  display: flex;
  justify-content: center;
  align-items: center;
}

body.dark-theme .overlay{
  background-color: rgba(193, 213, 226, 0.6);
}
.header {
  background-color: #2c6dad;
  color: white;
  padding: 5px 0;
  text-align: left;
  font-size: 10px;
  left: 0;
  top: 0;
  right: 0;
  width: 100%;
  position: fixed;
  display: flex;
  flex-direction: row;
  align-items: center;
  z-index: 1000;
}

.header h1 {
  margin-left: 10px;
  font-weight: 600;
  white-space: nowrap; /* 防止标题换行 */
}

.drive_icon {
  margin-left: 50px;
  width: 30px;
  height: 30px;
}

.menu {
  display: flex;
  justify-content: space-between; /* 将左右两部分分开 */
  width: 100%; /* 使菜单宽度占满父容器 */
}

/* 新增的样式，用于右侧菜单项 */
.menu-right {
  margin-left: auto; /* 将右侧菜单项推到最右边 */
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  margin-right: 30px; /* 增加与最右边的间隔 */
}

/* 禁用按钮的文本选择 */
.menu-item[role="button"] {
  user-select: none; /* 禁止文本选择 */
  -webkit-user-select: none; /* 针对Webkit浏览器 */
  -moz-user-select: none; /* 针对 Firefox */
  -ms-user-select: none; /* 针对 IE/Edge */
}
.menu-icon {
  width: 20px;
  height: 20px;
  margin-right: 0px;
}

.menu-item {
  margin-left: 20px;
  color: white;
  text-decoration: none;
  font-weight: 400;
  font-size: 12px;
  padding: 5px;
  display: flex;
  align-items: center;
}

.menu-item_main {
  font-size: 18px;
  font-weight: bold;
  margin-right: 0px;  /* 右侧的间距 */
  margin-left: 60px !important;   /* 使用 !important 确保左侧间距生效 */
  text-decoration: none;
  color: white;
  margin-left: 30px;
}

.menu-item:hover,
.menu-item_main:hover:hover {
  color: #007BFF;
}

.modal {
  display: none;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.4);
  padding-top: 60px;
}

.indent-text {
  text-indent: 2em !important;
}

.modal-content {
  color: #3e3e3e;
  border-radius: 10px;
  background-color: rgb(243, 251, 253);
  box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
  margin: 5% auto;
  padding: 30px;
  border: 1px solid #888;
  width: 80%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 400px;
}

.modal-content h2 {
  font-size: 21px;
  font-weight: bold;
}

.close-btn {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  position: absolute;
  top: 10px;
  right: 10px;
}

.close-btn:hover,
.close-btn:focus {
  color: #3e3e3e;
  text-decoration: none;
  cursor: pointer;
}

/* 给 router-view 设置样式 */
.container {
  padding: 20px;
}

.router-view-wrapper {
  width: 80%; /* 设置宽度为80%，你可以根据需要调整 */
  max-width: 1800px; /* 最大宽度设置为1200px，避免过宽 */
  margin: 0 auto; /* 水平居中 */
  padding: 20px; /* 添加左右内边距 */
  box-sizing: border-box; /* 使内边距不影响宽度 */
}
body.dark-theme .header {
  background-color: rgb(20, 38, 57);
}

body.dark-theme .menu-item {
  color: #ddd;
}

body.dark-theme .menu-item:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

</style>
