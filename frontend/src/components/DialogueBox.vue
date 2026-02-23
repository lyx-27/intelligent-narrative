<template>
  <div class="dialogue-box">
    <div class="narrative-text" ref="narrativeRef">
      <p v-html="formattedText"></p>
    </div>

    <div class="input-area">
      <div class="guidance">{{ guidancePrompt }}</div>

      <div class="choices" v-if="choices && choices.length > 0">
        <button
          v-for="(choice, index) in choices"
          :key="index"
          class="choice-btn"
          @click="selectChoice(choice)"
        >
          {{ choice }}
        </button>
      </div>

      <div class="user-input">
        <input
          v-model="userInput"
          type="text"
          placeholder="输入你的行动..."
          @keyup.enter="submitInput"
          :disabled="loading || isTyping"
        />
        <button @click="submitInput" :disabled="loading || !userInput.trim() || isTyping">
          {{ loading ? '思考中...' : isTyping ? '叙述中...' : '确定' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  narrativeText: String,
  guidancePrompt: String,
  choices: Array,
  loading: Boolean
})

const emit = defineEmits(['submit'])

const userInput = ref('')
const displayedText = ref('')
const isTyping = ref(false)
const narrativeRef = ref(null)

// 打字机效果
const typewriterSpeed = 30 // 毫秒/字符

function scrollToBottom() {
  nextTick(() => {
    if (narrativeRef.value) {
      narrativeRef.value.scrollTop = narrativeRef.value.scrollHeight
    }
  })
}

watch(() => props.narrativeText, (newText) => {
  if (!newText) return

  isTyping.value = true
  displayedText.value = ''

  let index = 0
  const interval = setInterval(() => {
    if (index < newText.length) {
      displayedText.value += newText[index]
      index++
      scrollToBottom()
    } else {
      clearInterval(interval)
      isTyping.value = false
    }
  }, typewriterSpeed)
}, { immediate: true })

const formattedText = computed(() => {
  return displayedText.value?.replace(/\n/g, '<br>') || ''
})

function selectChoice(choice) {
  userInput.value = choice
}

function submitInput() {
  if (userInput.value.trim() && !props.loading && !isTyping.value) {
    emit('submit', userInput.value)
    userInput.value = ''
  }
}
</script>

<style scoped>
.dialogue-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  background: rgba(245, 230, 211, 0.95);
  border-top: 3px solid #8b7355;
}

.narrative-text {
  flex: 1;
  min-height: 0;
  padding: 2rem;
  overflow-y: auto;
  font-size: 1.1rem;
  line-height: 1.8;
  color: #3e2723;
}

.input-area {
  padding: 1.5rem;
  background: rgba(212, 197, 176, 0.5);
  border-top: 1px solid #8b7355;
}

.guidance {
  margin-bottom: 1rem;
  color: #5d4e37;
  font-size: 0.95rem;
}

.choices {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.choice-btn {
  padding: 0.5rem 1rem;
  background: rgba(139, 115, 85, 0.2);
  border: 1px solid #8b7355;
  color: #3e2723;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.choice-btn:hover {
  background: rgba(139, 115, 85, 0.4);
}

.user-input {
  display: flex;
  gap: 0.5rem;
}

.user-input input {
  flex: 1;
  padding: 0.8rem;
  border: 2px solid #8b7355;
  background: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  font-family: inherit;
  color: #3e2723;
}

.user-input input:focus {
  outline: none;
  border-color: #5d4e37;
}

.user-input button {
  padding: 0.8rem 2rem;
  background: #8b7355;
  border: none;
  color: #f5e6d3;
  cursor: pointer;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
}

.user-input button:hover:not(:disabled) {
  background: #6d4c41;
}

.user-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
