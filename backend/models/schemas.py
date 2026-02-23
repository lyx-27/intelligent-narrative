"""
Pydantic数据模型 - 定义API请求和响应的数据结构
"""
from pydantic import BaseModel
from typing import List, Dict, Optional

class GameStartRequest(BaseModel):
    """游戏开始请求"""
    character_id: str  # "player_as_apprentice" / "player_as_master" / "player_as_patron"

class GameStartResponse(BaseModel):
    """游戏开始响应"""
    session_id: str
    character_name: str
    character_role: str
    initial_scene: str
    initial_image_url: Optional[str] = None
    guidance_prompt: str
    status: Dict

class ActionRequest(BaseModel):
    """玩家行动请求"""
    session_id: str
    user_input: str

class ActionResponse(BaseModel):
    """玩家行动响应"""
    narrative_text: str
    scene_image_url: Optional[str] = None
    fallback_description: str = ""
    status: Dict
    choices: Optional[List[str]] = None  # 建议选项
    is_fate_event: bool = False
    fate_event_data: Optional[Dict] = None
    is_ending: bool = False
    ending_data: Optional[Dict] = None
    knowledge_cards: Optional[List[Dict]] = None

class FateChoiceRequest(BaseModel):
    """命运事件选择请求"""
    session_id: str
    choice_key: str  # 选项标识

class FateChoiceResponse(BaseModel):
    """命运事件选择响应"""
    outcome_text: str
    next_scene: str
    scene_image_url: Optional[str] = None
    status: Dict
    ending_data: Optional[Dict] = None

class GameStateResponse(BaseModel):
    """游戏状态响应"""
    session_id: str
    player_role: str
    current_quest_id: str
    turn_count: int
    max_turns: int
    player_state: Dict
    current_time: str
    current_location: str
    current_weather: str
