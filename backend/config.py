"""
配置文件 - 集中管理API密钥、模型参数、路径等
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# API配置
API_KEY = "sk-G2hDWLMXoX11TuahtNvJvOIzFyDzK0MJEaZCWqmsjPwVhqHp"
API_BASE_URL = "https://api.whatai.cc/v1"

# LLM模型配置
LLM_MODEL = "gpt-4o-mini"  # 对话生成
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 500

# 图像生成配置
IMAGE_MODEL = "nano-banana-2"  # 性价比高的生图模型
IMAGE_SIZE = "512x512"
IMAGE_QUALITY = "standard"

# 对话历史配置
DIALOGUE_HISTORY_WINDOW = 10  # 保留最近10轮对话

# 游戏配置
MAX_TURNS = 20  # 最大对话回合数

# 路径配置
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
CACHE_DIR = BASE_DIR / "cache"
MURALS_DIR = STATIC_DIR / "murals"
GENERATED_IMAGES_DIR = CACHE_DIR / "generated_images"

# 数据文件路径
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.json"
MURAL_TAGS_PATH = DATA_DIR / "mural_tags.json"
PROMPT_LIBRARY_PATH = DATA_DIR / "prompt_library.json"

# 确保目录存在
for directory in [DATA_DIR, STATIC_DIR, CACHE_DIR, MURALS_DIR, GENERATED_IMAGES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
