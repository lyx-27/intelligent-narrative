# 《残壁丹青》智能叙事系统 v4.0

基于生成式AI的壁画互动叙事Web应用

## 项目结构

```
intelligent_narrative_demo_v4/
├── backend/              # FastAPI后端
│   ├── main.py          # API入口
│   ├── config.py        # 配置
│   ├── models/          # 数据模型
│   ├── engine/          # 叙事引擎
│   └── data/            # 知识库
├── frontend/            # Vue 3前端
│   ├── src/
│   │   ├── components/  # UI组件
│   │   ├── views/       # 页面视图
│   │   ├── stores/      # Pinia状态管理
│   │   └── api/         # API客户端
│   └── package.json
└── README.md
```

## 技术栈

**后端**
- FastAPI (异步Web框架)
- OpenAI API (LLM + DALL-E 3图像生成)
- Pydantic (数据验证)

**前端**
- Vue 3 (组合式API)
- Vite (构建工具)
- Pinia (状态管理)
- Axios (HTTP客户端)

**AI服务**
- LLM: GPT-4o-mini (叙事生成、意图识别、状态提取)
- 图像: DALL-E 3 (壁画风格场景图生成)

## 快速开始

### 1. 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### powershell运行：
```bash
cd G:\paper\F\intelligent_narrative_demo_v4
python -m uvicorn backend.main:app --reload --port 8000
```


后端将运行在 http://localhost:8000

### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端将运行在 http://localhost:5173

### 3. 访问应用

打开浏览器访问 http://localhost:5173

## API端点

- `GET /api/prologue` - 获取序章和角色信息
- `POST /api/game/start` - 开始新游戏
- `POST /api/game/action` - 玩家行动
- `POST /api/game/fate-choice` - 命运事件选择
- `GET /api/game/state/{session_id}` - 获取游戏状态
- `GET /api/images/{image_id}` - 获取场景图片

## 核心功能

### Phase 1 (MVP) ✅
- [x] FastAPI后端框架
- [x] Vue 3前端框架
- [x] 角色选择
- [x] LLM意图识别
- [x] 对话历史记忆
- [x] 状态追踪
- [x] 命运事件
- [x] 结局系统

### Phase 2 (视觉层) ✅
- [x] 图像生成管线（DALL-E 3）
- [x] 场景图缓存系统
- [x] 壁画风格提示词库（8个场景）
- [x] 打字机效果（30ms/字符）
- [x] 水墨转场动画（0.8秒）
- [x] 降级文字描述显示
- [x] 初始场景图生成

### Phase 3 (内容深度)
- [ ] 扩展故事树 (3角色×12节点)
- [ ] 新增命运事件 (火灾/告密)
- [ ] 后果系统
- [ ] NPC互动
- [ ] 9+结局

### Phase 4 (打磨)
- [ ] 叙事图谱回放
- [ ] 数据日志
- [ ] 性能优化

## 配置

编辑 `backend/config.py` 修改：
- API密钥
- 模型选择
- 对话历史窗口大小
- 最大回合数

## 开发说明

### 添加新任务节点

编辑 `backend/data/knowledge_base.json`，在对应角色的 `quests` 中添加：

```json
"Quest_ID": {
  "description": "场景描述",
  "guidance_prompt": "引导提示",
  "hidden_rules_for_llm": "LLM规则",
  "next_quest_map": {
    "intent_key": "Next_Quest_ID"
  }
}
```

### 添加命运事件

在 `fate_events` 中添加：

```json
"Fate_ID": {
  "title": "事件标题",
  "description": "事件描述",
  "prompt": "选择提示",
  "options": {
    "player_as_apprentice": {
      "text": "选项文本",
      "outcome_description": "结果描述",
      "next_ending": "ending_id"
    }
  }
}
```

## 论文相关

本项目是广电硕士论文《生成式AI驱动下壁画影像的智能叙事研究》的实践案例。

核心创新点：
1. LLM驱动的动态叙事生成
2. 多视角互动叙事结构
3. AI图像生成与壁画风格融合
4. 对话历史记忆机制
5. 状态追踪与后果系统

## License

MIT
