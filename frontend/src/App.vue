<template>
  <div class="app-container" @click="tryPlayMusic">
    <audio ref="bgMusic" src="/background-music.mp3" loop preload="auto"></audio>
    <TitleScreen v-if="stage === 'title'" @start="handleStart" />
    <CharacterSelect v-else-if="stage === 'character-select'" @select="handleCharacterSelect" />
    <GameView v-else-if="stage === 'playing'" />
    <EndingScreen v-else-if="stage === 'ending'" @restart="handleRestart" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from './stores/gameStore'
import TitleScreen from './components/TitleScreen.vue'
import CharacterSelect from './components/CharacterSelect.vue'
import GameView from './views/GameView.vue'
import EndingScreen from './components/EndingScreen.vue'

const gameStore = useGameStore()
const stage = computed(() => gameStore.stage)
const bgMusic = ref(null)
const musicStarted = ref(false)

function tryPlayMusic() {
  if (musicStarted.value) return
  const audio = bgMusic.value
  if (audio) {
    audio.volume = 0.3
    audio.play().then(() => {
      musicStarted.value = true
    }).catch(() => {})
  }
}

onMounted(async () => {
  await gameStore.loadPrologue()
  // 尝试自动播放，浏览器可能会阻止，用户点击页面后会自动开始
  tryPlayMusic()
})

function handleStart() {
  gameStore.stage = 'character-select'
}

async function handleCharacterSelect(characterId) {
  await gameStore.startGame(characterId)
}

function handleRestart() {
  gameStore.resetGame()
}
</script>

<style>
.app-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}
</style>
