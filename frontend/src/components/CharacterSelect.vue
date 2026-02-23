<template>
  <div class="character-select">
    <div class="select-content">
      <h2 class="select-title">选择你的身份</h2>
      <p class="select-prompt" v-if="prologueData">
        {{ prologueData.introduction }}
      </p>

      <div class="character-options">
        <div
          v-for="(char, key) in characters"
          :key="key"
          class="character-card"
          @click="selectCharacter(char.role_id)"
        >
          <h3 class="character-name">{{ char.detail.name }}</h3>
          <p class="character-role">{{ char.detail.role }}</p>
          <p class="character-desc">{{ char.detail.background }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/gameStore'

const emit = defineEmits(['select'])
const gameStore = useGameStore()

const prologueData = computed(() => gameStore.prologueData)
const characters = computed(() => prologueData.value?.characters || {})

function selectCharacter(roleId) {
  emit('select', roleId)
}
</script>

<style scoped>
.character-select {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('/front-P2.jpeg') center/cover no-repeat;
  position: relative;
  padding: 2rem;
  overflow-y: auto;
}

.character-select::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.select-content {
  max-width: 1200px;
  width: 100%;
  position: relative;
  z-index: 1;
}

.select-title {
  text-align: center;
  font-size: 2.5rem;
  color: #f5e6d3;
  margin-bottom: 2rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
}

.select-prompt {
  text-align: center;
  font-size: 1.1rem;
  line-height: 1.8;
  color: #f0e0cc;
  margin-bottom: 3rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}

.character-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.character-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  padding: 2rem;
  border: 2px solid #8b7355;
  cursor: pointer;
  transition: all 0.3s;
}

.character-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.95);
}

.character-name {
  font-size: 1.8rem;
  color: #3e2723;
  margin-bottom: 0.5rem;
}

.character-role {
  font-size: 1.1rem;
  color: #6d4c41;
  margin-bottom: 1rem;
}

.character-desc {
  font-size: 1rem;
  line-height: 1.6;
  color: #5d4e37;
}
</style>
