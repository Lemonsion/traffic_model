<template>
      <div class="chat-control">
      <Chat_1 />
        </div>
</template>

<script>
import Chat_1 from '../components/chat_with_robot.vue';

export default {
   components: {
    Chat_1
  },
  data() {
    return {
      drive: require('@/assets/drive.png'),
    };
  },

};
</script>

<style scoped>
.chat-control{
  width: 1370px;
  max-width: 100%; /* 防止超出视口 */
  margin: 0 auto; /* 水平居中 */
}
body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  overflow-x: hidden; /* 禁用横向滚动条 */
}

* {
  box-sizing: border-box; /* 确保padding和border包含在元素的总宽度和高度内 */
}
</style>