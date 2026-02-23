<template>
  <div class="ending-screen">
    <div class="ending-content">
      <h2 class="ending-title">{{ endingData?.title || '故事结束' }}</h2>
      <p class="ending-description">{{ endingData?.description || '感谢游玩' }}</p>

      <div class="ending-actions">
        <button class="restart-btn" @click="$emit('restart')">
          重新开始
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/gameStore'

defineEmits(['restart'])

const gameStore = useGameStore()
const endingData = computed(() => gameStore.endingData)
</script>

<style scoped>
.ending-screen {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3e2723 0%, #1c1410 100%);
}

.ending-content {
  max-width: 800px;
  padding: 3rem;
  text-align: center;
  color: #f5e6d3;
}

.ending-title {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #d4c5b0;
}

.ending-description {
  font-size: 1.2rem;
  line-height: 1.8;
  margin-bottom: 3rem;
}

.ending-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.restart-btn {
  padding: 1rem 3rem;
  background: rgba(139, 115, 85, 0.3);
  border: 2px solid #8b7355;
  color: #f5e6d3;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
  font-family: inherit;
}

.restart-btn:hover {
  background: rgba(139, 115, 85, 0.5);
  transform: scale(1.05);
}
</style>
