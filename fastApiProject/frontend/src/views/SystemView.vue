<template>
    <div class="control-sliders">
    <Sliderbar_1/>
    </div>
    <div>
      <Button_1  @clearTargets="clearTargets" @sendDataToApp="updateTargets" @clearTotalities="clearTotalities" @updateTotalities="updateTotalities"/>
    </div>
    <!-- 下方表格 -->
    <div class="table-container">
    <Table_1 :targets="targets" />
  </div>
 <div class="col-md-3">
       <Chart_1 :totalities_1="totalities"/>
      </div>
</template>

<script>
import 'element-plus/dist/index.css';
import Table_1 from '../components/table_all_objects.vue';
import Chart_1 from '../components/chart_detection.vue';
import Sliderbar_1 from '../components/sliderbar.vue';
import Button_1 from '../components/button_all.vue';  // 导入 Button 组件
export default {
   components: {
    Table_1,
    Chart_1,
    Sliderbar_1,
    Button_1
  },

  data() {
    return {
      imageSrc: '',  // 图片或视频源
      conf: 0,       // 置信度
      iou: 0,        // IoU
      targets: [],    // 检测到的目标数据
      totalities: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  // 检测到各种类型的总数
      drive: require('@/assets/drive.png'),  // 驱动图标
    };
  },
   methods: {
    // --------------更新目标数据-------------
    updateTargets(newTarget) {
      // 将新的目标添加到 targets 数组中
      this.targets.push(newTarget);
    },

    // --------------清空目标数据-------------
    clearTargets() {
      this.targets = [];
      console.log("清空target!!");
    },

    // --------------更新统计数据-------------
    updateTotalities(newTotalities) {
      this.totalities = newTotalities;
    },

    // --------------清空统计数据-------------
    clearTotalities() {
      this.totalities = [];
      console.log("清空统计图!!");
    }
  },

};
</script>


<style scoped>
.spacing {
  margin-left: 0px; /* 调整 CONF 和 IOU 之间的间距 */

}

span {
  padding: 0px 0px;           /* 设置左右的内边距，调整间距 */
  margin-left: -10px;  /* 设置文本与滑动条之间的间距 */
}

.extra-space {
    display: inline-block;  /* 确保元素作为内联块级元素渲染 */
    width: 120px;            /* 设置滑动条之间的间距 */
}

.status-display {
  display: flex; /* 使用Flexbox布局 */
  justify-content: center; /* 水平居中内容 */
}

.control-sliders {
  display: flex;          /* 使用 flexbox 布局 */
  align-items: center;    /* 可选，使滑动条垂直居中 */
  gap: 5px;                    /* 设置两个滑动条和字之间的间距 */
  position:absolute;
  background-color:  rgb(236, 244, 250); /* 设置背景框的颜色 */
  border-radius: 10px; /* 圆角 */
  box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); /* 背景框的阴影效果 */
  width: 1070px; /* 设置与图片相同的宽度 */
  height:50px;
  padding: 20px; /* 增加内边距使背景框更明显 */
  justify-content: center;
  transform: translate(-220px, -160px);

}

.table-container {
  display: flex;
  flex-direction: column; /* 设置为竖直方向 */
  transform: translate(-220px, 790px) ;
}
.col-md-3{
  display: flex;
  flex-direction: column; /* 设置为竖直方向 */
  transform: translate(-455px, 760px) ;
}

  body.dark-theme .control-sliders {
  background-color: rgb(227, 232, 235);
}

.stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px; /* 调整下方间距 */
  padding: 5px 0;   /* 调整内部上下间距 */
}

.stats span {
  line-height: 40px;    /* 增加行高来控制高度 */
  font-size: 16px;   /* 设置字体大小 */
  margin-left: 15px; /* 设置左右间距 */
}


</style>


