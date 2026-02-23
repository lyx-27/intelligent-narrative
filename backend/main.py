"""
FastAPI主入口 - 《残壁丹青》智能叙事系统后端
"""
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import KNOWLEDGE_BASE_PATH, GENERATED_IMAGES_DIR
from .models.schemas import (
    GameStartRequest, GameStartResponse,
    ActionRequest, ActionResponse,
    FateChoiceRequest, FateChoiceResponse,
    GameStateResponse
)
from .models.game_state import GameState
from .engine import narrative_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="残壁丹青 - 智能叙事系统", version="4.1")

# CORS配置（允许前端开发服务器访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存中的游戏会话存储
sessions: dict[str, GameState] = {}

# 加载知识库
knowledge_base = {}


@app.on_event("startup")
async def startup():
    global knowledge_base
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
        logger.info("知识库加载成功")
    except FileNotFoundError:
        logger.error(f"知识库文件不存在: {KNOWLEDGE_BASE_PATH}")
        raise


@app.get("/api/prologue")
async def get_prologue():
    """获取序章信息和角色选项"""
    return {
        "introduction": knowledge_base["prologue"]["introduction"],
        "worldview": knowledge_base["worldview"],
        "characters": {
            key: {
                "text": opt["text"],
                "role_id": opt["role_id"],
                "detail": knowledge_base["characters"].get(opt["role_id"], {})
            }
            for key, opt in knowledge_base["prologue"]["character_selection"]["options"].items()
        }
    }


@app.post("/api/game/start", response_model=GameStartResponse)
async def start_game(req: GameStartRequest):
    """开始新游戏"""
    if req.character_id not in knowledge_base.get("characters", {}):
        raise HTTPException(status_code=400, detail="无效的角色ID")

    if req.character_id not in knowledge_base.get("story_lines", {}):
        raise HTTPException(status_code=400, detail="该角色暂无故事线")

    # 创建游戏状态
    game_state = GameState(knowledge_base, req.character_id)
    sessions[game_state.session_id] = game_state

    # 获取初始场景
    character_info = game_state.get_character_info()
    first_quest = game_state.get_current_quest()

    initial_scene = first_quest["description"] if first_quest else "故事即将开始……"
    guidance = first_quest.get("guidance_prompt", "你现在想做什么？") if first_quest else "你现在想做什么？"

    # 生成初始场景图
    initial_image_url = None
    if first_quest:
        try:
            from .engine.image_service import generate_scene_image
            image_result = await generate_scene_image(game_state.current_quest_id)
            initial_image_url = image_result.get("url")
        except Exception as e:
            logger.error(f"初始场景图生成失败: {e}")

    logger.info(f"新游戏开始: session={game_state.session_id}, role={req.character_id}")

    return GameStartResponse(
        session_id=game_state.session_id,
        character_name=character_info.get("name", "未知"),
        character_role=character_info.get("role", "未知"),
        initial_scene=initial_scene,
        initial_image_url=initial_image_url,
        guidance_prompt=guidance,
        status=game_state.get_status_dict()
    )


@app.post("/api/game/action", response_model=ActionResponse)
async def game_action(req: ActionRequest):
    """处理玩家行动"""
    game_state = sessions.get(req.session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="会话不存在")

    result = await narrative_engine.process_action(game_state, req.user_input)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return ActionResponse(**result)


@app.post("/api/game/fate-choice", response_model=FateChoiceResponse)
async def fate_choice(req: FateChoiceRequest):
    """处理命运事件选择"""
    game_state = sessions.get(req.session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="会话不存在")

    result = await narrative_engine.process_fate_choice(game_state, req.choice_key)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return FateChoiceResponse(**result)


@app.get("/api/game/state/{session_id}", response_model=GameStateResponse)
async def get_game_state(session_id: str):
    """获取游戏状态"""
    game_state = sessions.get(session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="会话不存在")

    return GameStateResponse(
        session_id=game_state.session_id,
        player_role=game_state.player_role,
        current_quest_id=game_state.current_quest_id,
        turn_count=game_state.turn_count,
        max_turns=game_state.max_turns,
        player_state=game_state.player_state,
        current_time=game_state.current_time,
        current_location=game_state.current_location,
        current_weather=game_state.current_weather
    )


@app.get("/api/game/scene-image/{session_id}")
async def get_scene_image(session_id: str):
    """轮询获取异步生成的场景图片"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    result = narrative_engine.get_scene_image_status(session_id)
    return result


@app.get("/api/images/{image_id}")
async def get_image(image_id: str):
    """获取缓存的场景图片"""
    from .engine.image_service import get_cached_image_path

    path = get_cached_image_path(image_id)
    if not path:
        raise HTTPException(status_code=404, detail="图片不存在")

    return FileResponse(path, media_type="image/png")
