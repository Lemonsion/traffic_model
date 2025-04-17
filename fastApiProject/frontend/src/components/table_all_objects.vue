<template>
  <div class="container">
    <div class="table-wrapper">
      <table border="1">
        <thead>
          <tr>
            <th>序号</th>
            <th>目标类型</th>
            <th>位置</th>
            <th>置信度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(target, index) in targets" :key="index">
            <td>{{ target.id }}</td>
            <td>{{ target.type }}</td>
            <td>{{ target.location }}</td>
            <td>{{ target.confidence }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Table_1',
  props: {
    targets: {
      type: Array,
      required: true
    }
  },
};
</script>

<style scoped>
.container {
  display: flex;     /* 使用 flexbox */
  align-items: flex-start; /* 保证按钮在垂直方向上居中 */
  height: 340px;       /* 设置容器高度为视口高度 */
  width: 600px;         /* 根据内容自适应宽度 */
  background-color: rgb(236, 244, 250); /* 设置背景框的颜色 */
  padding: 20px; /* 增加内边距使背景框更明显 */
  border-radius: 10px; /* 圆角 */
  box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); /* 背景框的阴影效果 */
  position: absolute;
}

.table-wrapper {
  width: 600px; /* 设置表格容器的宽度 */
  max-height: 320px; /* 设置表格的最大高度 */
  overflow-y: auto;  /* 启用垂直滚动条 */
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  text-align: center;
  border: 1px solid #d3d3d3; /* 设置灰色边框 */
}

th {
  background-color: #2c6dad;
  color: white; /* 字体颜色 */
}

body.dark-theme th {
  background-color: rgb(48, 82, 119);
}
body.dark-theme .container{
  background-color: rgb(227, 232, 235);
}

/* 控制表头的对齐 */
thead tr {
  position: static;
}
</style>
