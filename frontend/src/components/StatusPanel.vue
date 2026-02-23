<template>
  <div class="status-panel">
    <div class="status-item">
      <span class="status-label">时辰</span>
      <span class="status-value">{{ status.current_time }}</span>
    </div>
    <div class="status-item">
      <span class="status-label">地点</span>
      <span class="status-value">{{ status.current_location }}</span>
    </div>
    <div class="status-item">
      <span class="status-label">天气</span>
      <span class="status-value">{{ status.current_weather }}</span>
    </div>
    <div class="status-item">
      <span class="status-label">回合</span>
      <span class="status-value">{{ status.turn_count }}/{{ status.max_turns }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  status: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.status-panel {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: rgba(0, 0, 0, 0.7);
  padding: 0.8rem 1rem;
  border-bottom: 2px solid #8b7355;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-label {
  color: #a89f91;
  font-size: 0.9rem;
}

.status-value {
  color: #f5e6d3;
  font-size: 1rem;
  font-weight: bold;
}
</style>
