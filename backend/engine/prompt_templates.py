"""
提示词模板库 - 所有LLM和图像生成的提示词
"""

def get_narrative_system_prompt(character_info: dict, worldview: dict, dialogue_context: str) -> str:
    """生成叙事系统提示词"""
    return f"""你是一个智能叙事引擎，正在讲述一个关于北宋陕北壁画的互动故事《残壁丹青》。

【角色信息】
- 玩家扮演：{character_info.get('name')} ({character_info.get('role')})
- 背景：{character_info.get('background')}
- 目标：{character_info.get('goal')}
- 内心冲突：{character_info.get('internal_conflict', '无')}

【世界观】
- 时代：{worldview['era']}
- 地点：{worldview['location']}
- 社会背景：{worldview['social_context']}
- 艺术风格：{worldview['art_style']}
- 核心主题：{worldview['core_theme']}

【壁画工艺知识】
宋代陕北壁画工序：斩凿>草泥>细泥>石灰面>粉本>线描>平涂>晕染>[沥粉贴金]>压线
颜料：朱砂、赭石、石青、石绿、铅白、松烟墨、雌黄、金箔；胶结用动物胶（热用）
分工：都料匠负责构图和面部，散工负责地仗和平涂
地域特征：中原画风与西夏/藏传影响交融，窟内可能有藏文/回鹘文题记
晕染技法：土红+白粉对比晕染（平面烘托，非立体阴影）
沥粉贴金：仅用于主尊肉髻、璎珞、光背、宝座

【叙述风格】
- 语言：沉静、质朴、略带感伤，符合北宋陕北的历史氛围
- 视角：第二人称（"你"），让玩家沉浸其中
- 节奏：张弛有度，重要时刻放慢节奏，细腻描写
- 细节：注重壁画绘制的技艺细节、颜料质感、光影变化

【对话历史】
{dialogue_context}

【核心任务】
1. 根据玩家输入生成连贯的叙事文本（150-250字）
2. 保持角色性格和世界观的一致性
3. 自然融入壁画绘制的专业细节
4. 推动故事向预设节点发展，但不生硬
5. 在关键时刻暗示玩家的选择会产生后果
"""

def get_intent_recognition_prompt(user_input: str, available_intents: list, current_context: str) -> str:
    """生成意图识别提示词"""
    intents_str = "、".join([f"'{intent}'" for intent in available_intents])
    return f"""请分析玩家输入的意图，并从以下预设意图中选择最匹配的一个：

【可选意图】
{intents_str}

【当前情境】
{current_context}

【玩家输入】
"{user_input}"

请直接返回最匹配的意图关键词（只返回关键词，不要解释）。如果没有明确匹配，返回"free_dialogue"。
"""

def get_state_extraction_prompt(narrative_text: str, user_input: str) -> str:
    """生成状态提取提示词"""
    return f"""请从以下叙事文本和玩家输入中提取状态变化信息。

【玩家输入】
{user_input}

【叙事文本】
{narrative_text}

请以JSON格式返回状态变化（如果没有变化则返回空对象）：
{{
    "knowledge_gained": ["知识点1", "知识点2"],  // 玩家新获得的知识
    "relationship_change": {{  // NPC关系变化
        "master_danqing": +5,  // 正数表示关系改善，负数表示恶化
        "young_monk": -3
    }},
    "internal_tendency": {{  // 内心倾向变化
        "obedience_rebellion": +1  // 正数偏向反叛，负数偏向顺从
    }},
    "mural_knowledge": ""  // 如果叙事中涉及壁画工艺，填写最相关的一个关键词：grinding_pigments(研磨颜料)、lifen_tiejin(沥粉贴金)、line_drawing(线描勾勒)、rendering(晕染)、ground_preparation(地仗处理)、flat_coloring(平涂填色)。如果不涉及壁画工艺则留空字符串。
}}

只返回JSON，不要其他文字。
"""

def get_image_generation_prompt(scene_context: dict, mural_style_reference: str = None) -> str:
    """生成图像生成提示词"""
    base_style = "北宋陕北寺观壁画风格，中原画风与西夏藏传影响交融，质朴有力的线条，浓烈的色彩（朱砂红、石青、赭石），佛教图像元素"

    prompt = f"""A scene in the style of Northern Song Dynasty (960-1127) Shaanbei temple mural painting.

【Scene Details】
- Location: {scene_context.get('location', '悬空寺洞窟')}
- Time: {scene_context.get('time', '清晨')}
- Weather/Atmosphere: {scene_context.get('weather', '晴朗')}
- Characters: {scene_context.get('characters', '无')}
- Key Elements: {scene_context.get('key_elements', '壁画、颜料、画具')}

【Artistic Style】
{base_style}
"""

    if mural_style_reference:
        prompt += f"\n【Reference】\n{mural_style_reference}"

    prompt += """

【Technical Requirements】
- Composition: Traditional Chinese painting composition with emphasis on narrative clarity
- Color Palette: Earth tones (ochre, vermillion, indigo, black ink)
- Texture: Aged wall surface with visible brushstrokes
- Lighting: Soft, diffused light typical of cave temple interiors
- Mood: Contemplative, slightly melancholic, historically authentic

Create a cinematic, atmospheric image that captures the essence of this historical moment.
"""

    return prompt

def get_consequence_check_prompt(player_state: dict, consequence_rules: list) -> str:
    """生成后果检查提示词"""
    return f"""请检查玩家当前状态是否触发了任何后果规则。

【玩家状态】
- 已获知识：{', '.join(player_state.get('knowledge_gained', []))}
- NPC关系：{player_state.get('relationship', {})}
- 内心倾向：{player_state.get('internal_tendency', {})}

【后果规则】
{consequence_rules}

请返回触发的后果规则ID列表（JSON数组格式）。如果没有触发，返回空数组[]。
"""
