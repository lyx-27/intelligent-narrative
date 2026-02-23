"""
LLM服务 - 封装所有LLM API调用
"""
import json
import re
import logging
from openai import AsyncOpenAI
from ..config import API_KEY, API_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE_URL)


async def chat_completion(system_prompt: str, user_prompt: str, temperature: float = None, max_tokens: int = None) -> str:
    """通用LLM对话补全"""
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature or LLM_TEMPERATURE,
            max_tokens=max_tokens or LLM_MAX_TOKENS,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        return ""


async def generate_narrative(system_prompt: str, user_input: str, current_scene: str, dialogue_history: list) -> str:
    """生成叙事文本"""
    messages = [{"role": "system", "content": system_prompt}]

    # 注入对话历史
    for msg in dialogue_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 当前用户输入
    user_prompt = f"【当前情景】{current_scene}\n\n【玩家输入】{user_input}\n\n请生成接下来的叙事文本（150-250字），自然推进故事。"
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"叙事生成失败: {e}")
        return "一阵风吹过洞窟，烛火摇曳不定……"


async def recognize_intent(user_input: str, available_intents: list, current_context: str) -> str:
    """LLM意图识别 - 替代关键词匹配"""
    from .prompt_templates import get_intent_recognition_prompt

    prompt = get_intent_recognition_prompt(user_input, available_intents, current_context)

    result = await chat_completion(
        system_prompt="你是一个意图分类器。只返回最匹配的意图关键词，不要解释。",
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=50
    )

    # 清理结果，确保返回有效意图
    result = result.strip().strip("'\"").lower()
    if result in available_intents:
        return result
    return "free_dialogue"


async def extract_state_changes(narrative_text: str, user_input: str) -> dict:
    """从叙事文本中提取状态变化"""
    from .prompt_templates import get_state_extraction_prompt

    prompt = get_state_extraction_prompt(narrative_text, user_input)

    result = await chat_completion(
        system_prompt="你是一个JSON提取器。只返回有效的JSON对象，不要其他文字。",
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=200
    )

    try:
        # 尝试解析JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(result)
    except (json.JSONDecodeError, IndexError):
        logger.warning(f"状态提取JSON解析失败: {result}")
        return {}


async def extract_scene_description(narrative_text: str) -> str:
    """从叙事文本中提取视觉场景描述（英文，供DALL-E使用）"""
    result = await chat_completion(
        system_prompt=(
            "You are a visual scene extractor. Given a Chinese narrative text, "
            "output a concise English visual description (2-3 sentences, under 80 words). "
            "Focus ONLY on visual elements: setting, lighting, character poses, objects, atmosphere. "
            "Do NOT include dialogue, emotions, or plot. Output English only."
        ),
        user_prompt=narrative_text,
        temperature=0.3,
        max_tokens=120
    )
    return result.strip() if result else ""


# 角色关键词映射（同步函数，零延迟）
_CHARACTER_KEYWORDS = {
    "apprentice": ["阿石", "学徒", "徒弟"],
    "master": ["老丹青", "师傅", "画师", "丹青"],
    "donor": ["王乡绅", "乡绅", "施主"],
    "monk": ["了尘", "小沙弥", "沙弥"],
}


def detect_characters_in_text(text: str) -> list:
    """检测叙事文本中出现的角色（关键词匹配，零延迟）"""
    found = []
    for char_key, keywords in _CHARACTER_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                found.append(char_key)
                break
    return found
