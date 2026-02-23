import { defineStore } from 'pinia'
import api from '../api/client'

export const useGameStore = defineStore('game', {
  state: () => ({
    // 游戏阶段: 'title' | 'character-select' | 'playing' | 'ending'
    stage: 'title',

    // 会话信息
    sessionId: null,
    characterId: null,
    characterName: '',
    characterRole: '',

    // 场景信息
    currentScene: '',
    sceneImageUrl: null,
    fallbackDescription: '',
    narrativeText: '',
    guidancePrompt: '',

    // 游戏状态
    status: {
      turn_count: 0,
      max_turns: 20,
      current_time: '清晨',
      current_location: '悬空寺洞窟内',
      current_weather: '晴朗',
      player_state: {
        knowledge_gained: [],
        relationship: {},
        internal_tendency: {}
      }
    },

    // 选项
    choices: [],

    // 命运事件
    isFateEvent: false,
    fateEventData: null,

    // 结局
    isEnding: false,
    endingData: null,

    // 壁画工艺知识卡片
    knowledgeCards: [],

    // 序章数据
    prologueData: null,

    // 加载状态
    loading: false,
    imageLoading: false,
    error: null,

    // 轮询版本号，用于取消旧轮询
    _pollVersion: 0
  }),

  actions: {
    async loadPrologue() {
      try {
        this.loading = true
        this.prologueData = await api.getPrologue()
      } catch (error) {
        this.error = '加载序章失败'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async startGame(characterId) {
      try {
        this.loading = true
        const response = await api.startGame(characterId)

        this.sessionId = response.session_id
        this.characterId = characterId
        this.characterName = response.character_name
        this.characterRole = response.character_role
        this.currentScene = response.initial_scene
        this.sceneImageUrl = response.initial_image_url
        this.guidancePrompt = response.guidance_prompt
        this.status = response.status

        this.stage = 'playing'
      } catch (error) {
        this.error = '开始游戏失败'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async sendAction(userInput) {
      if (!this.sessionId || !userInput.trim()) return

      // 取消旧的图片轮询
      this._pollVersion++

      try {
        this.loading = true
        this.imageLoading = true
        const response = await api.gameAction(this.sessionId, userInput)

        this.narrativeText = response.narrative_text
        this.status = response.status
        this.choices = response.choices || []
        this.knowledgeCards = response.knowledge_cards || []

        // 检查命运事件
        if (response.is_fate_event) {
          this.isFateEvent = true
          this.fateEventData = response.fate_event_data
        } else {
          this.isFateEvent = false
          this.fateEventData = null
        }

        // 检查结局
        if (response.is_ending) {
          this.isEnding = true
          this.endingData = response.ending_data
          this.stage = 'ending'
        }
      } catch (error) {
        this.error = '行动处理失败'
        console.error(error)
      } finally {
        this.loading = false
      }

      // 异步轮询场景图片（不阻塞UI）
      this._pollSceneImage()
    },

    async _pollSceneImage() {
      if (!this.sessionId) return

      const currentVersion = this._pollVersion
      const maxAttempts = 30
      const interval = 2000

      for (let i = 0; i < maxAttempts; i++) {
        // 如果版本号变了，说明有新的action发出，停止旧轮询
        if (this._pollVersion !== currentVersion) return

        try {
          const result = await api.getSceneImage(this.sessionId)

          if (this._pollVersion !== currentVersion) return

          if (result.status === 'ready') {
            if (result.url) {
              this.sceneImageUrl = result.url
            }
            if (result.fallback_description) {
              this.fallbackDescription = result.fallback_description
            }
            this.imageLoading = false
            return
          }

          if (result.status === 'none') {
            this.imageLoading = false
            return
          }

          // status === 'pending', wait and retry
          await new Promise(resolve => setTimeout(resolve, interval))
        } catch (error) {
          console.error('场景图片轮询失败:', error)
          this.imageLoading = false
          return
        }
      }
      this.imageLoading = false
    },

    async sendFateChoice(choiceKey) {
      if (!this.sessionId) return

      try {
        this.loading = true
        const response = await api.fateChoice(this.sessionId, choiceKey)

        this.narrativeText = response.outcome_text
        if (response.scene_image_url) {
          this.sceneImageUrl = response.scene_image_url
        }
        this.status = response.status

        this.isFateEvent = false
        this.fateEventData = null

        // 命运事件后进入结局
        if (response.next_scene) {
          this.isEnding = true
          this.endingData = response.ending_data || {
            title: '故事结束',
            description: response.outcome_text
          }
          this.stage = 'ending'
        }
      } catch (error) {
        this.error = '命运选择失败'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    resetGame() {
      this.stage = 'title'
      this.sessionId = null
      this.characterId = null
      this.isFateEvent = false
      this.fateEventData = null
      this.isEnding = false
      this.endingData = null
      this.narrativeText = ''
      this.choices = []
      this.knowledgeCards = []
    }
  }
})
