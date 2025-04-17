<template>
  <div class="c-slider-wrapper">
    <!-- 置信度滑动条 -->
    <div class="slider-container">
      <label for="confSlider" class="slider-label">CONF:</label>
      <div class="slider-wrapper">
        <input type="range" id="confSlider" min="0" max="1" step="0.01" value="0.5" class="c-slider">
        <span id="confValue" class="slider-value">0.5</span>
      </div>
    </div>

    <!-- IOU阈值滑动条 -->
    <div class="slider-container">
      <label for="iouSlider" class="slider-label">IOU:</label>
      <div class="slider-wrapper">
        <input type="range" id="iouSlider" min="0" max="1" step="0.01" value="0.5" class="c-slider">
        <span id="iouValue" class="slider-value">0.5</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sliderbar_1',
  data() {
    return {};
  },
  mounted() {
    const confSlider = document.getElementById("confSlider");
    const iouSlider = document.getElementById("iouSlider");
    const confValue = document.getElementById("confValue");
    const iouValue = document.getElementById("iouValue");

    // 获取主题并更新背景颜色
    const updateSliderBackground = (slider) => {
      const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
      const isDarkTheme = document.body.classList.contains('dark-theme');
      const backgroundColor = isDarkTheme ? 'rgb(48, 82, 119)' : '#3d96f3'; // 更新暗黑模式背景色
      slider.style.background = `linear-gradient(to right, ${backgroundColor} ${value - 0.5}%, #d3d3d3 ${value - 0.5}%)`;
    };

    const updateSliderValue = (slider, valueElement) => {
      const value = parseFloat(slider.value).toFixed(2);
      valueElement.innerText = value;
      // 计算并设置数字标注位置
      const percentage = (slider.value - slider.min) / (slider.max - slider.min);
      const offset = percentage * slider.offsetWidth;
      valueElement.style.left = `${offset - valueElement.offsetWidth / 2}px`;
    };

    const handleSliderChange = () => {
      updateSliderValue(confSlider, confValue);
      updateSliderValue(iouSlider, iouValue);
      updateSliderBackground(confSlider);
      updateSliderBackground(iouSlider);
        // 触发事件，将 conf 和 iou 值传递给父组件
      this.$emit('update-values', {
        conf: parseFloat(confSlider.value),
        iou: parseFloat(iouSlider.value)
      });
      this.sendConfIouToBackend(parseFloat(confSlider.value), parseFloat(iouSlider.value));
    };

    // 监听主题变化
    const themeObserver = new MutationObserver(() => {
      updateSliderBackground(confSlider);
      updateSliderBackground(iouSlider);
    });

    themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    confSlider.addEventListener("input", handleSliderChange);
    iouSlider.addEventListener("input", handleSliderChange);

    // 初始化背景样式和位置
    updateSliderBackground(confSlider);
    updateSliderBackground(iouSlider);
    updateSliderValue(confSlider, confValue);
    updateSliderValue(iouSlider, iouValue);
  },
  methods: {
    sendConfIouToBackend(conf, iou) {
      let formData = new FormData();
      formData.append("conf", conf);
      formData.append("iou", iou);

      fetch("http://127.0.0.1:8000/set_conf_iou/", {
        method: "POST",
        body: formData,
        mode: "cors",
        credentials: "include",
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("配置更新成功:", data);
        })
        .catch((error) => {
          console.error("配置更新失败:", error);
        });
    },
  },
};
</script>

<style scoped lang="scss">
.c-slider-wrapper {
  display: flex;
  align-items: center;
  background-color:  rgb(236, 244, 250);
}

  body.dark-theme .c-slider-wrapper {
  background-color: rgb(227, 232, 235);
}

.slider-container {
  position: relative;
  display: flex;
  margin-right: 300px;  /* 增加两个滑动条之间的间距 */
}

.slider-container:last-child {
  margin-right: 0;  /* 最后的滑动条不增加右边的间距 */
}

.slider-label {
  font-size: 15px;
  color: #666;
}

.slider-wrapper {
  position: relative;
  width: 200px;
}

.c-slider {
  flex-grow: 1;
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 15px;
  background: #ebeef5;
  border-radius: 6px;
  outline: none;
  transition: background 0.3s ease;
  body.dark-theme & {
    background: #2a3d52;  /* Dark background for slider */
  }
}

.slider-value {
  position: absolute;
  top: -22px;
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}

.c-slider:hover {
  background: #cbe9f6;
  body.dark-theme & {
    background: #3b5d76;  /* Darker hover background */
  }
}

.c-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid #3d96f3;
  cursor: pointer;
  transition: background 0.3s ease;
  body.dark-theme & {
    background: #cadeed;  /* Darker thumb */
    border: 1px solid #043e7d;  /* Light border for thumb in dark theme */
  }
}

.c-slider::-webkit-slider-thumb:hover {
  background: #cbe9f6;
  body.dark-theme & {
    background: #4f7f94;
  }
}

.c-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3d96f3;
  cursor: pointer;
}

.c-slider::-moz-range-thumb:hover {
  background: #2b79b0;

}
</style>
