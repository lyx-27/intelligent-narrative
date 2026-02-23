import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
client.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
client.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 获取序章
  getPrologue() {
    return client.get('/prologue')
  },

  // 开始游戏
  startGame(characterId) {
    return client.post('/game/start', { character_id: characterId })
  },

  // 玩家行动
  gameAction(sessionId, userInput) {
    return client.post('/game/action', {
      session_id: sessionId,
      user_input: userInput
    })
  },

  // 命运事件选择
  fateChoice(sessionId, choiceKey) {
    return client.post('/game/fate-choice', {
      session_id: sessionId,
      choice_key: choiceKey
    })
  },

  // 获取游戏状态
  getGameState(sessionId) {
    return client.get(`/game/state/${sessionId}`)
  },

  // 轮询获取场景图片
  getSceneImage(sessionId) {
    return client.get(`/game/scene-image/${sessionId}`)
  }
}
