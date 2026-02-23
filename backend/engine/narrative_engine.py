"""
核心叙事引擎 - 管理故事推进、命运事件、后果系统
"""
import asyncio
import json
import logging
from typing import Dict, Optional, Tuple
from ..models.game_state import GameState
from ..config import DATA_DIR
from . import llm_service
from . import image_service
from .prompt_templates import get_narrative_system_prompt

logger = logging.getLogger(__name__)

# 异步图片生成任务存储: session_id → asyncio.Task
_pending_image_tasks: Dict[str, asyncio.Task] = {}
# 已完成的图片结果: session_id → {"url": str|None, "fallback_description": str}
_completed_images: Dict[str, Dict] = {}

# 壁画工艺知识卡片数据
_mural_knowledge = {}

def _load_mural_knowledge():
    """加载壁画工艺知识卡片"""
    global _mural_knowledge
    try:
        with open(DATA_DIR / "mural_knowledge.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            _mural_knowledge = data.get("knowledge_cards", {})
            logger.info(f"已加载壁画知识卡片: {list(_mural_knowledge.keys())}")
    except Exception as e:
        logger.warning(f"壁画知识卡片加载失败: {e}")

_load_mural_knowledge()


async def process_action(game_state: GameState, user_input: str) -> Dict:
    """
    处理玩家行动 - 核心流程：
    1. 获取当前任务
    2. LLM意图识别
    3. 生成叙事文本
    4. 提取状态变化
    5. 推进任务
    6. 检查命运事件/结局
    """
    current_quest = game_state.get_current_quest()
    if not current_quest:
        return {"error": "当前无有效任务"}

    # 检查是否触发命运事件
    if "trigger_fate_event" in current_quest:
        fate_event_id = current_quest["trigger_fate_event"]
        fate_event = game_state.kb["fate_events"].get(fate_event_id)
        if fate_event:
            return await _build_fate_event_response(game_state, fate_event)

    # 检查是否是结局
    if "next_ending" in current_quest:
        ending_id = current_quest["next_ending"]
        ending = game_state.kb["endings"].get(ending_id)
        if ending:
            return await _build_ending_response(game_state, ending, ending_id)

    # 增加回合
    game_state.increment_turn()

    # 检查回合上限
    if game_state.is_game_over():
        return {
            "narrative_text": "时光流转，你在悬空寺的日子已到了尽头。壁画尚未完成，但你的故事已在这残壁之上留下了印记……",
            "is_ending": True,
            "ending_data": {"title": "时光尽头", "description": "你已达到对话上限，故事在此告一段落。"},
            "is_fate_event": False,
            "fate_event_data": None,
            "fallback_description": "",
            "scene_image_url": None,
            "choices": None,
            "status": game_state.get_status_dict()
        }

    # 1. LLM意图识别
    next_quest_map = current_quest.get("next_quest_map", {})
    available_intents = list(next_quest_map.keys())

    intent = "free_dialogue"
    if available_intents:
        intent = await llm_service.recognize_intent(
            user_input=user_input,
            available_intents=available_intents + ["free_dialogue"],
            current_context=current_quest["description"]
        )

    # 2. 生成叙事文本
    character_info = game_state.get_character_info()
    worldview = game_state.kb["worldview"]
    dialogue_context = game_state.get_dialogue_context()

    system_prompt = get_narrative_system_prompt(character_info, worldview, dialogue_context)

    # 注入隐藏规则
    hidden_rules = current_quest.get("hidden_rules_for_llm", "")
    if hidden_rules:
        system_prompt += f"\n\n【当前情节规则】\n{hidden_rules}"

    narrative_text = await llm_service.generate_narrative(
        system_prompt=system_prompt,
        user_input=user_input,
        current_scene=current_quest["description"],
        dialogue_history=game_state.dialogue_history
    )

    # 3. 记录对话历史
    game_state.add_dialogue("user", user_input)
    game_state.add_dialogue("assistant", narrative_text)

    # 4. 提取并更新状态
    state_changes = await llm_service.extract_state_changes(narrative_text, user_input)
    if state_changes:
        game_state.update_state(state_changes)

    # 提取壁画工艺知识卡片
    knowledge_cards = []
    mural_kw = state_changes.get("mural_knowledge", "") if state_changes else ""
    if mural_kw and mural_kw in _mural_knowledge:
        knowledge_cards.append(_mural_knowledge[mural_kw])

    # 5. 推进任务
    quest_advanced = False
    if intent != "free_dialogue" and intent in next_quest_map:
        game_state.advance_quest(next_quest_map[intent])
        quest_advanced = True

    # 6. 检查推进后的新任务是否触发命运事件
    new_quest = game_state.get_current_quest()
    is_fate_event = False
    fate_event_data = None
    is_ending = False
    ending_data = None

    if new_quest and "trigger_fate_event" in new_quest:
        fate_event_id = new_quest["trigger_fate_event"]
        fate_event = game_state.kb["fate_events"].get(fate_event_id)
        if fate_event:
            is_fate_event = True
            fate_event_data = {
                "id": fate_event_id,
                "title": fate_event["title"],
                "description": fate_event["description"],
                "prompt": fate_event["prompt"],
                "options": _get_fate_options(fate_event, game_state.player_role)
            }

    if new_quest and "next_ending" in new_quest:
        ending_id = new_quest["next_ending"]
        ending = game_state.kb["endings"].get(ending_id)
        if ending:
            is_ending = True
            ending_data = {"title": ending["title"], "description": ending["description"]}

    # 构建建议选项
    choices = _generate_choices(new_quest or current_quest)

    # 异步生成场景图片（不阻塞响应）— 基于叙事文本动态生成
    _start_image_task(game_state.session_id, narrative_text)

    # 构建响应
    response = {
        "narrative_text": narrative_text,
        "scene_image_url": None,
        "fallback_description": "",
        "status": game_state.get_status_dict(),
        "choices": choices,
        "is_fate_event": is_fate_event,
        "fate_event_data": fate_event_data,
        "is_ending": is_ending,
        "ending_data": ending_data,
        "knowledge_cards": knowledge_cards if knowledge_cards else None
    }

    # 如果任务推进了，附加新场景描述（用过渡语衔接）
    if quest_advanced and new_quest and not is_fate_event and not is_ending:
        new_desc = new_quest.get("description", "")
        if new_desc:
            response["narrative_text"] = narrative_text + "\n\n……\n\n" + new_desc

    return response


async def process_fate_choice(game_state: GameState, choice_key: str) -> Dict:
    """处理命运事件选择"""
    current_quest = game_state.get_current_quest()
    if not current_quest or "trigger_fate_event" not in current_quest:
        return {"error": "当前无命运事件"}

    fate_event_id = current_quest["trigger_fate_event"]
    fate_event = game_state.kb["fate_events"].get(fate_event_id)
    if not fate_event:
        return {"error": "命运事件数据不存在"}

    # 获取对应角色的选项
    option = fate_event["options"].get(choice_key)
    if not option:
        # 尝试用玩家角色作为key
        option = fate_event["options"].get(game_state.player_role)
    if not option:
        return {"error": "无效的命运选择"}

    # 推进到结局（使用后果系统动态决定）
    next_id = option.get("next_ending")
    if next_id and game_state.player_role == "player_as_apprentice":
        # 学徒线使用后果系统决定结局
        next_id = game_state.determine_ending()
    if next_id:
        game_state.advance_quest(next_id)

    # 记录到对话历史
    game_state.add_dialogue("user", f"[命运选择] {option.get('text', choice_key)}")
    game_state.add_dialogue("assistant", option.get("outcome_description", ""))

    # 生成结局场景图
    scene_image_url = None
    ending_data = None
    if next_id:
        # 获取结局数据
        ending = game_state.kb["endings"].get(next_id)
        if ending:
            ending_data = {"title": ending["title"], "description": ending["description"]}
        try:
            image_result = await image_service.generate_scene_image(next_id)
            scene_image_url = image_result.get("url")
        except Exception as e:
            logger.error(f"结局场景图生成失败: {e}")

    return {
        "outcome_text": option.get("outcome_description", ""),
        "next_scene": next_id or "",
        "scene_image_url": scene_image_url,
        "status": game_state.get_status_dict(),
        "ending_data": ending_data
    }


def _start_image_task(session_id: str, narrative_text: str):
    """启动异步图片生成任务（不阻塞）— 基于叙事文本动态生成"""
    # 取消之前的任务（如果有）
    old_task = _pending_image_tasks.pop(session_id, None)
    if old_task and not old_task.done():
        old_task.cancel()
    # 清除旧结果
    _completed_images.pop(session_id, None)

    async def _generate():
        try:
            # 1. 从叙事文本提取视觉场景描述
            scene_desc = await llm_service.extract_scene_description(narrative_text)
            if not scene_desc:
                scene_desc = "Interior of a Northern Song Dynasty cave temple, dim candlelight, mural painting in progress"

            # 2. 检测文本中出现的角色
            char_names = llm_service.detect_characters_in_text(narrative_text)

            # 3. 获取风格和角色特征
            style_prompt = image_service.get_image_style_prompt()
            char_traits = image_service.get_character_traits_for_names(char_names)

            # 4. 动态生成图片
            result = await image_service.generate_image_from_narrative(scene_desc, style_prompt, char_traits)
            _completed_images[session_id] = {
                "url": result.get("url"),
                "fallback_description": result.get("description", "")
            }
        except Exception as e:
            logger.error(f"异步场景图生成失败: {e}")
            _completed_images[session_id] = {"url": None, "fallback_description": ""}
        finally:
            _pending_image_tasks.pop(session_id, None)

    _pending_image_tasks[session_id] = asyncio.create_task(_generate())


def get_scene_image_status(session_id: str) -> Dict:
    """
    获取场景图片状态（供轮询端点调用）
    返回: {"status": "pending"|"ready"|"none", "url": str|None, "fallback_description": str}
    """
    # 已完成
    if session_id in _completed_images:
        result = _completed_images.pop(session_id)
        return {
            "status": "ready",
            "url": result.get("url"),
            "fallback_description": result.get("fallback_description", "")
        }
    # 进行中
    if session_id in _pending_image_tasks:
        return {"status": "pending", "url": None, "fallback_description": ""}
    # 无任务
    return {"status": "none", "url": None, "fallback_description": ""}


async def _build_fate_event_response(game_state: GameState, fate_event: Dict) -> Dict:
    """构建命运事件响应"""
    # 动态获取fate event id
    current_quest = game_state.get_current_quest()
    fate_event_id = current_quest.get("trigger_fate_event", "") if current_quest else ""

    scene_image_url = None
    try:
        image_result = await image_service.generate_scene_image(fate_event_id)
        scene_image_url = image_result.get("url")
    except Exception as e:
        logger.error(f"命运事件场景图生成失败: {e}")

    return {
        "narrative_text": fate_event["description"],
        "is_fate_event": True,
        "fate_event_data": {
            "id": fate_event_id,
            "title": fate_event["title"],
            "description": fate_event["description"],
            "prompt": fate_event["prompt"],
            "options": _get_fate_options(fate_event, game_state.player_role)
        },
        "is_ending": False,
        "ending_data": None,
        "fallback_description": "",
        "status": game_state.get_status_dict(),
        "choices": None,
        "scene_image_url": scene_image_url
    }


async def _build_ending_response(game_state: GameState, ending: Dict, ending_id: str) -> Dict:
    """构建结局响应"""
    # 为结局生成场景图
    scene_image_url = None
    try:
        image_result = await image_service.generate_scene_image(ending_id)
        scene_image_url = image_result.get("url")
    except Exception as e:
        logger.error(f"结局场景图生成失败: {e}")

    return {
        "narrative_text": ending["description"],
        "is_ending": True,
        "ending_data": {"title": ending["title"], "description": ending["description"]},
        "is_fate_event": False,
        "fate_event_data": None,
        "fallback_description": "",
        "status": game_state.get_status_dict(),
        "choices": None,
        "scene_image_url": scene_image_url
    }


def _get_fate_options(fate_event: Dict, player_role: str) -> list:
    """获取命运事件的选项列表"""
    options = fate_event.get("options", {})
    role_option = options.get(player_role)
    if role_option:
        return [{"key": player_role, "text": role_option["text"]}]
    return []


def _generate_choices(quest: Dict) -> list:
    """根据当前任务生成建议选项"""
    if not quest:
        return []

    next_map = quest.get("next_quest_map", {})
    if not next_map:
        return []

    # 根据意图关键词生成自然语言选项
    intent_to_choice = {
        # 学徒线
        "interact": "走近师傅和乡绅",
        "work": "去准备颜料",
        "continue_listen": "继续偷听",
        "apologize_leave": "道歉离开",
        "reflect": "陷入沉思",
        "look_around": "四处看看",
        "talk": "和了尘聊聊",
        "refuse": "婉拒，继续工作",
        "comfort": "安慰了尘",
        "doubt": "说出你的怀疑",
        "observe": "仔细观察旧壁画",
        "continue": "继续工作",
        "respond": "回应师傅",
        "continue_observe": "继续观察壁画",
        "ask_skill": "请教师傅技艺",
        "ask_meaning": "询问壁画的意义",
        "understand": "我理解了",
        "confused": "我不太明白",
        "imitate": "谨慎模仿师傅",
        "innovate": "加入自己的理解",
        "confront": "质问师傅",
        "keep_secret": "把秘密藏在心里",
        # 画师线
        "dismiss": "强硬回绝乡绅",
        "agree": "敷衍答应乡绅",
        "call_apprentice": "叫徒弟过来帮忙",
        "draft": "开始画底稿",
        "teach": "教导徒弟",
        "insist": "坚持按规矩画",
        "compromise": "妥协，按乡绅要求画",
        "recall": "回忆往事",
        "focus": "专注当下",
        "strict": "严格要求徒弟",
        "lenient": "放手让徒弟发挥",
        "confess": "告诉阿石往事",
        "hide": "继续隐瞒",
        "praise": "夸赞徒弟",
        "deflect": "谦虚回避",
        # 乡绅线
        "demand": "强调你的要求",
        "test": "试探徒弟的才能",
        "inspect": "巡视寺庙",
        "find_abbot": "去找住持",
        "bargain": "趁机压价",
        "appreciate": "表示欣赏",
        "refugees": "注意到流民",
        "mural": "注意到旧壁画",
        "demand_more": "趁机提更多要求",
        "show_concern": "表示关心",
        "give_alms": "施舍一些",
        "ignore": "视而不见",
        "curious": "好奇追问",
        "watch": "回去盯着画师"
    }

    choices = []
    for intent_key in next_map:
        choice_text = intent_to_choice.get(intent_key, intent_key)
        choices.append(choice_text)

    return choices
