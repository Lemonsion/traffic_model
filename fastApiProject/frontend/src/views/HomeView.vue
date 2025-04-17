<script setup>

</script>

<template>
  <div class="content">
    <h1>欢迎进入自动驾驶检测系统</h1>
    <p>我们为您提供高效、安全、精准的自动驾驶目标检测解决方案。让自动驾驶更加智能和安全。</p>
    <p>通过我们的系统，您可以实时监控并分析道路上的目标，提升驾驶决策的准确性。</p>
    <router-link to="/systemview">
      <button class="enter-btn">进入系统</button>
    </router-link>
  </div>
</template>

<style scoped>

.content {
  text-align: center;
  color: #4d4d52; /* 调整为深灰色，更柔和 */
  padding: 40px 20px;

  border-radius: 10px; /* 圆角边框 */
}
h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 20px;
}

p {
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.enter-btn {
  background: linear-gradient(145deg, #007bff,#2c6dad); /* 渐变背景 */
  color: white;
  padding: 12px 30px; /* 稍微增加内边距 */
  font-size: 1.2rem;
  border: none;
  border-radius: 30px; /* 圆角效果 */
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease; /* 平滑过渡 */
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2), 0 6px 20px rgba(3, 100, 205, 0.1); /* 添加阴影 */
}

body.dark-theme .enter-btn{
  background:  linear-gradient(145deg, #066ddb, #1b4874);
}

body.dark-theme .enter-btn:hover{
  background: linear-gradient(145deg, #02448b, #011d39);
}

.enter-btn:hover {
  background: linear-gradient(145deg, #0056b3, #003366); /* 悬浮时渐变颜色变化 */
  transform: translateY(-3px); /* 提升按钮 */
  box-shadow: 0 6px 12px rgba(0, 123, 255, 0.3), 0 8px 25px rgba(0, 123, 255, 0.2); /* 强化阴影 */
}



.enter-btn:active {
  transform: translateY(1px); /* 按钮按下时稍微向下 */
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1), 0 4px 15px rgba(0, 123, 255, 0.1); /* 按下时阴影减弱 */
}
</style>
