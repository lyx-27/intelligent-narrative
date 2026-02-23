<template>
  <div class="scene-display">
    <transition name="ink-fade" mode="out-in">
      <div :key="imageKey" class="scene-image" :style="sceneStyle">
        <div class="scene-overlay"></div>
        <div class="location-tag">{{ location }}</div>

        <!-- 图片加载进度指示 -->
        <div v-if="isLoading || imageLoading" class="loading-overlay">
          <div class="loading-content">
            <div class="loading-bar-track">
              <div class="loading-bar-fill"></div>
            </div>
            <p class="loading-text">场景绘制中…</p>
          </div>
        </div>

        <!-- 降级文字描述 -->
        <div v-if="!imageUrl && !isLoading && fallbackDescription" class="fallback-description">
          <p>{{ fallbackDescription }}</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  imageUrl: String,
  location: String,
  fallbackDescription: String,
  imageLoading: Boolean
})

const imageKey = ref(0)
const isLoading = ref(false)
const loadedUrl = ref(null)

// 监听图片变化，用 Image 预加载
watch(() => props.imageUrl, (newUrl) => {
  if (!newUrl) {
    isLoading.value = false
    loadedUrl.value = null
    imageKey.value++
    return
  }

  if (newUrl === loadedUrl.value) return

  isLoading.value = true
  const img = new Image()
  img.onload = () => {
    loadedUrl.value = newUrl
    isLoading.value = false
    imageKey.value++
  }
  img.onerror = () => {
    isLoading.value = false
    loadedUrl.value = null
    imageKey.value++
  }
  img.src = newUrl
}, { immediate: true })

const sceneStyle = computed(() => {
  if (loadedUrl.value) {
    return {
      backgroundImage: `url(${loadedUrl.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {
    background: 'linear-gradient(135deg, #5d4e37 0%, #3e2723 100%)'
  }
})
</script>

<style scoped>
.scene-display {
  flex: 0 0 60%;
  position: relative;
  overflow: hidden;
}

.scene-image {
  width: 100%;
  height: 100%;
  position: relative;
  transition: background 0.5s ease;
}

.scene-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 50%, rgba(0, 0, 0, 0.6) 100%);
}

.location-tag {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.6);
  color: #f5e6d3;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border: 1px solid rgba(245, 230, 211, 0.3);
  z-index: 1;
}

.fallback-description {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #f5e6d3;
  font-size: 1.2rem;
  padding: 2rem;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(245, 230, 211, 0.3);
  max-width: 80%;
  z-index: 1;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  z-index: 2;
}

.loading-content {
  text-align: center;
}

.loading-bar-track {
  width: 200px;
  height: 4px;
  background: rgba(245, 230, 211, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.loading-bar-fill {
  height: 100%;
  width: 30%;
  background: #f5e6d3;
  border-radius: 2px;
  animation: loading-slide 1.5s ease-in-out infinite;
}

@keyframes loading-slide {
  0% { transform: translateX(-100%); width: 30%; }
  50% { width: 50%; }
  100% { transform: translateX(400%); width: 30%; }
}

.loading-text {
  margin-top: 12px;
  color: #f5e6d3;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 水墨晕染转场效果 */
.ink-fade-enter-active,
.ink-fade-leave-active {
  transition: all 0.8s ease;
}

.ink-fade-enter-from {
  opacity: 0;
  filter: blur(10px);
  transform: scale(1.05);
}

.ink-fade-leave-to {
  opacity: 0;
  filter: blur(10px);
  transform: scale(0.95);
}
</style>
