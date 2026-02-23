"""
游戏状态管理 - 升级版GameState类
"""
from typing import List, Dict, Optional
import uuid
from datetime import datetime

class GameState:
    """游戏状态类 - 管理单个游戏会话的所有状态"""

    def __init__(self, kb: Dict, player_role: str):
        self.session_id = str(uuid.uuid4())
        self.kb = kb
        self.player_role = player_role
        self.current_quest_id = kb["story_lines"][player_role]["start_quest"]

        # 玩家状态
        self.player_state = {
            "knowledge_gained": [],  # 已获得的知识
            "internal_tendency": {"obedience_rebellion": 0},  # 内心倾向（顺从-反叛）
            "relationship": {  # NPC关系值
                "master_danqing": 50,
                "young_monk": 50,
                "patron_wang": 50
            }
        }

        # 游戏进度
        self.turn_count = 0
        self.max_turns = 20

        # 场景状态
        self.current_time = "清晨"
        self.current_location = "悬空寺洞窟内"
        self.current_weather = "晴朗"

        # 对话历史（滑动窗口）
        self.dialogue_history: List[Dict[str, str]] = []
        self.max_history_length = 10

        # 故事历史（完整记录）
        self.story_history: List[Dict] = []
        self.quest_history: List[str] = [self.current_quest_id]  # 追踪路径

        # 创建时间
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

    def add_dialogue(self, role: str, content: str):
        """添加对话到历史记录"""
        self.dialogue_history.append({
            "role": role,
            "content": content
        })
        # 保持滑动窗口大小
        if len(self.dialogue_history) > self.max_history_length:
            self.dialogue_history = self.dialogue_history[-self.max_history_length:]
        self.last_updated = datetime.now()

    def get_dialogue_context(self) -> str:
        """获取对话历史的文本表示"""
        if not self.dialogue_history:
            return "（无对话历史）"

        context = []
        for msg in self.dialogue_history:
            if msg["role"] == "user":
                context.append(f"玩家：{msg['content']}")
            elif msg["role"] == "assistant":
                context.append(f"叙事：{msg['content']}")
        return "\n".join(context)

    def update_state(self, updates: Dict):
        """更新玩家状态"""
        if "knowledge_gained" in updates:
            for knowledge in updates["knowledge_gained"]:
                if knowledge not in self.player_state["knowledge_gained"]:
                    self.player_state["knowledge_gained"].append(knowledge)

        if "relationship_change" in updates:
            for npc, change in updates["relationship_change"].items():
                current = self.player_state["relationship"].get(npc, 50)
                self.player_state["relationship"][npc] = max(0, min(100, current + change))

        if "internal_tendency" in updates:
            for key, change in updates["internal_tendency"].items():
                current = self.player_state["internal_tendency"].get(key, 0)
                self.player_state["internal_tendency"][key] = current + change

        self.last_updated = datetime.now()

    def get_current_quest(self) -> Optional[Dict]:
        """获取当前任务数据"""
        if not self.player_role or not self.current_quest_id:
            return None
        return self.kb["story_lines"][self.player_role]["quests"].get(self.current_quest_id)

    def get_character_info(self, role_id: str = None) -> Dict:
        """获取角色信息"""
        if role_id is None:
            role_id = self.player_role
        return self.kb["characters"].get(role_id, {})

    def advance_quest(self, next_quest_id: str):
        """推进到下一个任务"""
        self.current_quest_id = next_quest_id
        self.quest_history.append(next_quest_id)
        self.last_updated = datetime.now()

    def determine_ending(self) -> str:
        """根据玩家路径和状态决定结局"""
        tendency = self.player_state["internal_tendency"].get("obedience_rebellion", 0)
        history = self.quest_history

        if self.player_role == "player_as_apprentice":
            # 大胆创新路径 → 觉醒结局
            if "Apprentice_Bold_Choice" in history or "Apprentice_Confront_Master" in history:
                return "ending_apprentice_awakening"
            # 保守模仿路径 → 传承结局
            if "Apprentice_Safe_Choice" in history or "Apprentice_Keep_Secret" in history:
                return "ending_apprentice_tradition"
            # 倾向反叛 → 觉醒
            if tendency > 2:
                return "ending_apprentice_awakening"
            # 倾向顺从 → 传承
            if tendency < -2:
                return "ending_apprentice_tradition"
            # 默认 → 迷茫
            return "ending_apprentice"

        elif self.player_role == "player_as_master":
            return "ending_master"

        elif self.player_role == "player_as_patron":
            return "ending_patron"

        return "ending_apprentice"

    def increment_turn(self):
        """增加回合计数"""
        self.turn_count += 1
        self.last_updated = datetime.now()

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.turn_count >= self.max_turns

    def get_status_dict(self) -> Dict:
        """获取状态字典（用于API响应）"""
        return {
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "current_time": self.current_time,
            "current_location": self.current_location,
            "current_weather": self.current_weather,
            "player_state": self.player_state,
            "current_quest_id": self.current_quest_id
        }

    def to_dict(self) -> Dict:
        """序列化为字典（用于持久化）"""
        return {
            "session_id": self.session_id,
            "player_role": self.player_role,
            "current_quest_id": self.current_quest_id,
            "player_state": self.player_state,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "current_time": self.current_time,
            "current_location": self.current_location,
            "current_weather": self.current_weather,
            "dialogue_history": self.dialogue_history,
            "story_history": self.story_history,
            "quest_history": self.quest_history,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
