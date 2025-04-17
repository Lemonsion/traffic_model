<template>
  <div class="dashboard">
    <!-- 使用 Element Plus 的布局组件展示数据看板 -->
    <el-row :gutter="20" class="data-board">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <el-card>
          <div class="stat-label">{{ item.label }}</div>
          <div class="stat-value">{{ item.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 按钮触发更新数据 -->
    <div class="refresh-button">
      <el-button @click="handleRefreshData" type="primary">刷新数据</el-button>
    </div>

    <!-- 查询时间选择器和查询按钮 -->
    <div class="query-section" style="margin-top: 20px; display: flex; align-items: center;">
      <!-- 查询时间选择器 -->
      <el-date-picker
        v-model="selectedDate"
        type="date"
        placeholder='选择查询日期'
        format="yyyy-MM-dd"
        style="margin-right: 20px;"
      ></el-date-picker>

      <!-- 查询按钮 -->
      <el-button @click="handleQuery" type="primary">查询</el-button>
    </div>

    <!-- 显示历史查询记录 -->
    <div class="history-records" style="margin-top: 40px;">
      <h3>历史查询记录</h3>
        <div class="table-wrapper" style="overflow-x: auto;">
      <el-table :data="history" style="width: 100%">
        <el-table-column label="检测ID" prop="detection_id"></el-table-column>
<!--        <el-table-column label="处理文件" prop="processed_file"></el-table-column>-->

        <!-- 图片列 -->
        <el-table-column label="图片">
          <template #default="{ row }">
            <!-- 显示图片 -->
              <img :src="`data:image/jpeg;base64,${row.processed_file}`" alt="Processed Image" style="width: 100px;" />
          </template>
        </el-table-column>

        <el-table-column label="车辆类型（自行车）" prop="vehicle_types.bike" width="120" ></el-table-column>
        <el-table-column label="车辆类型（公交车）" prop="vehicle_types.bus"  width="120"></el-table-column>
        <el-table-column label="车辆类型（小车）" prop="vehicle_types.car" width="120"></el-table-column>
        <el-table-column label="车辆类型（摩托车）" prop="vehicle_types.motor" width="120"></el-table-column>
        <el-table-column label="车辆类型（行人）" prop="vehicle_types.person" width="120"></el-table-column>
        <el-table-column label="车辆类型（骑行者）" prop="vehicle_types.rider" width="120"></el-table-column>
        <el-table-column label="车辆类型（交通信号灯）" prop="vehicle_types.trafficlight" width="120"></el-table-column>
        <el-table-column label="车辆类型（交通标志）" prop="vehicle_types.trafficsign" width="120"></el-table-column>
        <el-table-column label="车辆类型（火车）" prop="vehicle_types.train" width="120"></el-table-column>
        <el-table-column label="车辆类型（卡车）" prop="vehicle_types.truck" width="120"></el-table-column>
        <el-table-column label="置信度" prop="conf" width="120"></el-table-column>
      </el-table>
          </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'

// 定义响应式数组，保存仪表板的统计数据
const stats = ref([
  {label: '总检测数', value: 0},
  {label: '当日检测数', value: 0},
  {label: '总预警数', value: 0},
  {label: '当日预警数', value: 0}
])

// 定义响应式数组，保存历史记录
const history = ref([])

// 定义响应式变量，保存选择的日期
const selectedDate = ref(new Date().toISOString().split('T')[0]) // 初始化为当前日期


// 处理查询操作
function formatDateLocal(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')  // 注意：月份从 0 开始
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
function handleQuery() {
  // 将 selectedDate 转换为 Date 对象
  const date = new Date(selectedDate.value)
  const formattedDate = formatDateLocal(date)
  fetchDashboardData(formattedDate)  // 请求选择日期的数据
}

// 请求后端数据并更新仪表板
async function fetchDashboardData(date) {
  // console.log("请求后端数据并更新仪表板")
  try {
    const response = await fetch(`http://127.0.0.1:8000/get_detection_data/?date=${date}`, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'},
    })

    if (response.ok) {
      // console.log('请求成功，响应数据：', response)
      const data = await response.json()
      // console.log("获取数据成功:", data)

      // 如果没有查询到数据，则清空表格内容
      if (!data.success || !data.data || data.data.length === 0) {
        history.value = []  // 清空历史记录
      } else {
        // 处理查询结果并更新表格
        const records = data.data.map(record => ({
          detection_id: record.detection_id,
          processed_file: record.processed_file,
          vehicle_types: {
            bike: record.bike,
            bus: record.bus,
            car: record.car,
            motor: record.motor,
            person: record.person,
            rider: record.rider,
            trafficlight: record.trafficlight,
            trafficsign: record.trafficsign,
            train: record.train,
            truck: record.truck,
          },
          conf: record.conf
        }))
        history.value = records  // 更新历史记录数据
      }
    } else {
      // console.log('请求失败，响应数据：', response)
      console.error('请求失败，状态码：', response.status)
    }
  } catch (error) {
    // console.log('请求失败，错误信息：', error)
    console.error('获取数据失败:', error)
  }
}

// 处理刷新数据的函数
function handleRefreshData() {
  // console.log("刷新数据")
  const date = new Date().toISOString().split('T')[0]  // 获取当前日期
  fetchDashboardData(date)  // 请求当天的数据
  // console.log("刷新数据结束")
}


// 通过 API 获取统计数据
const fetchSummaryData = async () => {
  try {
    console.log("正在请求数据...");
    const response = await fetch(`http://localhost:8000/detection_summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log("响应状态:", response.status);

    if (!response.ok) {
      throw new Error('网络响应不正常');
    }

    const summaryData = await response.json();
    console.log("获取到的统计数据:", summaryData);

    // 更新 stats 数组的值
    stats.value = [
      { label: '总检测数', value: summaryData.total_detection_count },
      { label: '当日检测数', value: summaryData.today_detection_count },
      { label: '总预警数', value: summaryData.total_warning_count },
      { label: '当日预警数', value: summaryData.today_warning_count }
    ]
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

// 在组件挂载时获取数据（只请求一次）
onMounted(() => {
  console.log("组件挂载")
  const date = new Date().toISOString().split('T')[0]  // 获取当前日期
  fetchDashboardData(date)  // 请求当天的数据
  fetchSummaryData();
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  margin-top: 80px;
  max-width: 100%; /* 防止超出视口 */
}

.el-card {
  background-color: rgb(236, 244, 250); /* 设置卡片背景颜色 */
}

body.dark-theme .el-card{
    background-color: rgb(227, 232, 235);
}
.stat-label {
  font-size: 16px;
  color: #666;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-top: 10px;
  transition: transform 0.3s ease; /* 添加动画效果 */
}

.stat-value:hover {
  transform: scale(1.05); /* 鼠标悬停时放大 */
  color: #007bff; /* 颜色变化 */
}

.refresh-button {
  margin-top: 20px;
  text-align: center;
}

.query-section {
  display: flex;
  align-items: center;
}

.history-records {
  margin-top: 40px;
}

.history-records h3 {
  font-size: 24px;
  margin-bottom: 20px;
}
.table-wrapper {
  width: 100%;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
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
