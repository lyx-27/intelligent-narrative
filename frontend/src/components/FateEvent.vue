<template>
  <div class="fate-event-overlay">
    <div class="fate-content">
      <h2 class="fate-title">{{ fateData.title }}</h2>
      <p class="fate-description">{{ fateData.description }}</p>
      <p class="fate-prompt">{{ fateData.prompt }}</p>

      <div class="fate-options">
        <button
          v-for="option in fateData.options"
          :key="option.key"
          class="fate-option-btn"
          @click="$emit('choice', option.key)"
        >
          {{ option.text }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  fateData: {
    type: Object,
    required: true
  }
})

defineEmits(['choice'])
</script>

<style scoped>
.fate-event-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fate-content {
  max-width: 700px;
  padding: 3rem;
  background: linear-gradient(135deg, #8b0000 0%, #4a0000 100%);
  border: 3px solid #ff6b6b;
  color: #f5e6d3;
  text-align: center;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.fate-title {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: #ff6b6b;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.fate-description {
  font-size: 1.2rem;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.fate-prompt {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  color: #ffcccc;
}

.fate-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fate-option-btn {
  padding: 1rem 2rem;
  background: rgba(255, 107, 107, 0.2);
  border: 2px solid #ff6b6b;
  color: #f5e6d3;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
  font-family: inherit;
}

.fate-option-btn:hover {
  background: rgba(255, 107, 107, 0.4);
  transform: scale(1.05);
}
</style>
