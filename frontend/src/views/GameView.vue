<template>
  <div class="game-view">
    <!-- 场景显示区 -->
    <SceneDisplay
      :imageUrl="sceneImageUrl"
      :location="status.current_location"
      :fallbackDescription="fallbackDescription"
      :imageLoading="imageLoading"
    />

    <!-- 状态栏 -->
    <StatusPanel :status="status" />

    <!-- 命运事件覆盖层 -->
    <FateEvent
      v-if="isFateEvent"
      :fateData="fateEventData"
      @choice="handleFateChoice"
    />

    <!-- 对话框 + 知识卡片 -->
    <template v-else>
      <!-- 壁画工艺知识卡片 -->
      <KnowledgeCard :cards="knowledgeCards" />

      <!-- 对话框 -->
      <DialogueBox
        :narrativeText="displayText"
        :guidancePrompt="guidancePrompt"
        :choices="choices"
        :loading="loading"
        @submit="handleUserInput"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/gameStore'
import SceneDisplay from '../components/SceneDisplay.vue'
import StatusPanel from '../components/StatusPanel.vue'
import DialogueBox from '../components/DialogueBox.vue'
import FateEvent from '../components/FateEvent.vue'
import KnowledgeCard from '../components/KnowledgeCard.vue'

const gameStore = useGameStore()

const sceneImageUrl = computed(() => gameStore.sceneImageUrl)
const imageLoading = computed(() => gameStore.imageLoading)
const status = computed(() => gameStore.status)
const isFateEvent = computed(() => gameStore.isFateEvent)
const fateEventData = computed(() => gameStore.fateEventData)
const loading = computed(() => gameStore.loading)
const choices = computed(() => gameStore.choices)
const guidancePrompt = computed(() => gameStore.guidancePrompt)
const fallbackDescription = computed(() => gameStore.fallbackDescription)
const knowledgeCards = computed(() => gameStore.knowledgeCards)

const displayText = computed(() => {
  if (gameStore.narrativeText) {
    return gameStore.narrativeText
  }
  return gameStore.currentScene
})

async function handleUserInput(input) {
  await gameStore.sendAction(input)
}

async function handleFateChoice(choiceKey) {
  await gameStore.sendFateChoice(choiceKey)
}
</script>

<style scoped>
.game-view {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  background: #2c2416;
}
</style>
