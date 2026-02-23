<template>
  <div class="title-screen">
    <div class="title-content">
      <h1 class="game-title">残壁丹青</h1>
      <p class="subtitle">生成式AI驱动的壁画智能叙事</p>
      <div class="intro-text">
        <p>北宋年间，陕北悬空寺</p>
        <p>一幅壁画，三段人生</p>
        <p>在信仰崩塌的时代，寻找存在的意义</p>
      </div>
      <button class="start-button" @click="$emit('start')">
        开始故事
      </button>
    </div>
    <div class="decorative-border"></div>
  </div>
</template>

<script setup>
defineEmits(['start'])
</script>

<style scoped>
.title-screen {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('/front-P1.jpeg') center/cover no-repeat;
  position: relative;
  overflow: hidden;
}

.title-screen::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
}

.title-content {
  text-align: center;
  z-index: 1;
  color: #f5e6d3;
}

.game-title {
  font-size: 4rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.5rem;
}

.subtitle {
  font-size: 1.2rem;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.intro-text {
  margin-bottom: 3rem;
  line-height: 2;
  font-size: 1.1rem;
}

.intro-text p {
  margin: 0.5rem 0;
}

.start-button {
  padding: 1rem 3rem;
  font-size: 1.3rem;
  background: rgba(245, 230, 211, 0.2);
  border: 2px solid #f5e6d3;
  color: #f5e6d3;
  cursor: pointer;
  transition: all 0.3s;
  font-family: inherit;
}

.start-button:hover {
  background: rgba(245, 230, 211, 0.4);
  transform: scale(1.05);
}

.decorative-border {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  border: 3px solid rgba(245, 230, 211, 0.3);
  pointer-events: none;
}
</style>
