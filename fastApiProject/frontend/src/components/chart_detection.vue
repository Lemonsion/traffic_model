<template>
  <div class="container">
  <div class="echart" id="mychart" :style="myChartStyle"></div>
      </div>
</template>

<script>
import * as echarts from "echarts";

// 导入 markRaw
import { markRaw } from 'vue';
export default {
  props: {
    totalities_1: {
      type: Array,
      required: true
    }
  },

  data() {
    return {
      myChart: {}, // ECharts 实例
      myChartStyle: { width: "470px", height: "370px" }, // 图表样式
      dynamicSortZZTOption: {
        xAxis: {
          type: "value", // 设置 X 轴为值类型
          max: 20,// 设置 X 轴的最大值
        },
        yAxis: {
          type: "category",
          data: ["公交车", "路灯", "标志牌", "人", "自行车", "卡车", "摩托车", "小汽车", "火车", "骑手"],
          inverse: true,
          animationDuration: 300,
          animationDurationUpdate: 300,
          max: 9 // 只显示所有的条目
        },
        grid: {
          left: '13%',   // 左边距
          right: '5%',  // 右边距
          top: '10%',     // 上边距
          bottom: '10%',  // 下边距
        },
        series: [
          {
            type: "bar",
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            label: {
              show: true,
              position: "right",
              valueAnimation: false
            },
            itemStyle: {
              color: 'rgb(78,162,200)', // 柱形颜色
              barBorderRadius: [5, 5, 0, 0], // 圆角设置
            }
          }
        ],
        legend: {
          show: false,
          data: ['目标统计'], // Legend 数据
        },
        animationDuration: 1000,
        animationEasing: "cubicOut",
        tooltip: {
          trigger: 'item', // 鼠标悬停时显示内容
          formatter: '{b}: {c}' // 自定义提示内容
        }
      }
    };
  },

  watch: {
    // 监听 totalities_1 的变化，更新图表数据
    totalities_1(newVal) {
      this.updateChartData(newVal);
    }
  },

  methods: {
    updateChartData(totalities_1) {
      // 这里假设 totalities_1 是一个数组，每个值对应 yAxis 中的一个项
      this.dynamicSortZZTOption.series[0].data = totalities_1;
      // 更新图表
      if (this.myChart) {
        this.myChart.setOption(this.dynamicSortZZTOption);
      }
    }
  },

  mounted() {
    // 图表初始化
    this.myChart = markRaw(echarts.init(document.getElementById("mychart")));
    // 初次加载时赋值
    this.updateChartData(this.totalities_1);
  }
};
</script>

<style scoped>
.container {
  display: flex; /* 使用 flexbox */
  align-items: flex-start; /* 保证按钮在水平方向上居中 */
  justify-content: flex-end;
  width: 480px;  /* 确保容器占满父元素宽度 */
  transform: translate(890px, 30px);
}

.echart {
  right: 3px;
  /* 添加样式以更美观 */
  border-radius: 10px; /* 圆角 */
  box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2); /* 阴影效果 */
  background-color:  rgb(236, 244, 250); /* 背景颜色 */
  padding: 5px;
  }

  body.dark-theme .echart {
  background-color: rgb(227, 232, 235);
}

</style>