<template>
  <div v-if="cards && cards.length" class="knowledge-cards">
    <div
      v-for="(card, index) in cards"
      :key="index"
      class="knowledge-card"
      :class="{ expanded: expandedIndex === index }"
      @click="toggle(index)"
    >
      <div class="card-header">
        <span class="card-icon">{{ card.icon }}</span>
        <span class="card-title">{{ card.title }}</span>
        <span class="card-toggle">{{ expandedIndex === index ? '▲' : '▼' }}</span>
      </div>
      <div v-if="expandedIndex === index" class="card-content">
        {{ card.content }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  cards: {
    type: Array,
    default: () => []
  }
})

const expandedIndex = ref(-1)

function toggle(index) {
  expandedIndex.value = expandedIndex.value === index ? -1 : index
}
</script>

<style scoped>
.knowledge-cards {
  padding: 0 12px;
  margin-bottom: 8px;
}

.knowledge-card {
  background: linear-gradient(135deg, #f5e6d3, #ede0d0);
  border: 1px solid #c4a882;
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.knowledge-card:hover {
  border-color: #8b7355;
}

.knowledge-card.expanded {
  border-color: #8b7355;
  box-shadow: 0 2px 8px rgba(139, 115, 85, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  gap: 8px;
}

.card-icon {
  font-size: 16px;
}

.card-title {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #5a4632;
}

.card-toggle {
  font-size: 10px;
  color: #8b7355;
}

.card-content {
  padding: 0 12px 10px;
  font-size: 12px;
  line-height: 1.7;
  color: #6b5842;
  border-top: 1px dashed #c4a882;
  margin: 0 8px;
  padding-top: 8px;
}
</style>
