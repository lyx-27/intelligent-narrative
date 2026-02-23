"""
图像生成服务 - 管理AI图像生成管线
基于壁画照片标签 + 风格提示词生成场景图
"""
import json
import hashlib
import logging
from pathlib import Path
import httpx
from openai import AsyncOpenAI
from ..config import (
    API_KEY, API_BASE_URL, IMAGE_MODEL, IMAGE_SIZE, IMAGE_QUALITY,
    GENERATED_IMAGES_DIR, DATA_DIR, BASE_DIR
)

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE_URL)

# 加载提示词库和标签库
_prompt_library = {}
_mural_tags = {}
_local_cache = {}  # prompt_hash → 本地文件名(不含扩展名)
_local_cache_path = GENERATED_IMAGES_DIR / "local_cache.json"

# 外部风格/角色 prompt
_image_style_prompt = ""
_character_traits = {}  # key=角色标识, value=外貌描述


def _load_data():
    """加载提示词库和壁画标签"""
    global _prompt_library, _mural_tags, _local_cache
    try:
        with open(DATA_DIR / "prompt_library.json", "r", encoding="utf-8") as f:
            _prompt_library = json.load(f)
    except Exception as e:
        logger.warning(f"提示词库加载失败: {e}")

    try:
        with open(DATA_DIR / "mural_tags.json", "r", encoding="utf-8") as f:
            _mural_tags = json.load(f)
    except Exception as e:
        logger.warning(f"壁画标签库加载失败: {e}")

    # 加载本地缓存
    try:
        if _local_cache_path.exists():
            with open(_local_cache_path, "r", encoding="utf-8") as f:
                _local_cache = json.load(f)
    except Exception as e:
        logger.warning(f"本地缓存加载失败: {e}")


def _load_external_prompts():
    """加载外部 image style.txt 和 Character traits prompt.txt"""
    global _image_style_prompt, _character_traits
    project_root = BASE_DIR.parent

    # 加载图片风格
    style_path = project_root / "image style.txt"
    try:
        if style_path.exists():
            _image_style_prompt = style_path.read_text(encoding="utf-8").strip()
            logger.info(f"已加载图片风格 prompt ({len(_image_style_prompt)} chars)")
    except Exception as e:
        logger.warning(f"图片风格加载失败: {e}")

    # 加载角色外貌特征
    traits_path = project_root / "Character traits prompt.txt"
    try:
        if traits_path.exists():
            content = traits_path.read_text(encoding="utf-8").strip()
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                # 格式: "key：description" 或 "key: description"
                if "：" in line:
                    key, val = line.split("：", 1)
                elif ":" in line:
                    key, val = line.split(":", 1)
                else:
                    continue
                key = key.strip().lower()
                val = val.strip()
                if key and val:
                    _character_traits[key] = val
            logger.info(f"已加载角色特征: {list(_character_traits.keys())}")
    except Exception as e:
        logger.warning(f"角色特征加载失败: {e}")


def _save_local_cache():
    """保存本地缓存到文件"""
    try:
        with open(_local_cache_path, "w", encoding="utf-8") as f:
            json.dump(_local_cache, f)
    except Exception as e:
        logger.warning(f"本地缓存保存失败: {e}")


# 启动时加载
_load_data()
_load_external_prompts()


def _get_cache_path(prompt: str) -> Path:
    """根据提示词生成缓存文件路径"""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
    return GENERATED_IMAGES_DIR / f"scene_{prompt_hash}.png"


def build_scene_prompt(quest_id: str, variation: str = None) -> str:
    """
    根据任务ID构建完整的图像生成提示词
    流程: quest_id → scene_key → scene_prompt + base_style + quest context
    """
    # 1. 查找任务对应的场景
    mapping = _mural_tags.get("quest_to_scene_mapping", {})
    scene_key = mapping.get(quest_id, "cave_interior")

    # 2. 获取场景提示词
    scene_prompts = _prompt_library.get("scene_prompts", {})
    scene_data = scene_prompts.get(scene_key, {})
    scene_prompt = scene_data.get("base", "")

    # 使用变体（如果指定）
    if variation and "variations" in scene_data:
        scene_prompt = scene_data["variations"].get(variation, scene_prompt)

    # 3. 组合基础风格
    base_style = _prompt_library.get("base_style_prompt", "")

    # 4. 添加质量修饰词
    tech_params = _prompt_library.get("technical_parameters", {})
    quality_mods = ", ".join(tech_params.get("quality_modifiers", []))

    # 5. 加入任务ID作为上下文，确保不同任务生成不同图片
    full_prompt = f"{base_style}\n\nScene: {scene_prompt}\n\nNarrative moment: {quest_id}\n\nQuality: {quality_mods}"

    return full_prompt


def get_scene_key_for_quest(quest_id: str) -> str:
    """获取任务对应的场景key"""
    mapping = _mural_tags.get("quest_to_scene_mapping", {})
    return mapping.get(quest_id, "cave_interior")


def get_scene_fallback_description(scene_key: str) -> str:
    """获取场景的降级文字描述"""
    scenes = _mural_tags.get("scenes", {})
    scene = scenes.get(scene_key, {})
    if scene:
        name = scene.get("name", "未知场景")
        atmosphere = scene.get("atmosphere", "")
        lighting = scene.get("lighting", "")
        return f"{name} — {atmosphere}，{lighting}"
    return "北宋陕北寺庙场景"


async def generate_scene_image(quest_id: str, variation: str = None) -> dict:
    """
    为指定任务生成场景图片
    返回: {"url": str|None, "source": "generated"|"cached"|"fallback", "description": str}
    """
    scene_key = get_scene_key_for_quest(quest_id)
    prompt = build_scene_prompt(quest_id, variation)
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
    local_filename = f"scene_{prompt_hash}"
    local_path = GENERATED_IMAGES_DIR / f"{local_filename}.png"

    # 检查本地缓存：文件存在则直接返回本地API路径
    if prompt_hash in _local_cache and local_path.exists():
        logger.info(f"使用本地缓存: {local_filename} (quest={quest_id})")
        return {
            "url": f"/api/images/{local_filename}",
            "source": "cached",
            "description": ""
        }

    # 尝试生成
    try:
        logger.info(f"生成场景图片: quest={quest_id}, scene={scene_key}")
        response = await client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt[:4000],
            size=IMAGE_SIZE,
            quality=IMAGE_QUALITY,
            n=1
        )

        image_url = response.data[0].url
        logger.info(f"图片生成成功: {image_url[:80]}")

        # 下载图片到本地
        try:
            async with httpx.AsyncClient() as http:
                img_resp = await http.get(image_url, timeout=30, follow_redirects=True)
            if img_resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(img_resp.content)
                _local_cache[prompt_hash] = local_filename
                _save_local_cache()
                logger.info(f"图片已下载到本地: {local_filename}")
                return {
                    "url": f"/api/images/{local_filename}",
                    "source": "generated",
                    "description": ""
                }
            else:
                logger.warning(f"图片下载失败, HTTP {img_resp.status_code}")
        except Exception as e:
            logger.error(f"图片下载异常: {e}")

    except Exception as e:
        logger.error(f"图像生成失败 (quest={quest_id}): {e}")

    # 降级：返回文字描述
    fallback_desc = get_scene_fallback_description(scene_key)
    return {
        "url": None,
        "source": "fallback",
        "description": fallback_desc
    }


def get_cached_image_path(image_id: str) -> Path | None:
    """获取缓存图片的文件路径"""
    path = GENERATED_IMAGES_DIR / f"{image_id}.png"
    if path.exists():
        return path
    return None


def get_image_style_prompt() -> str:
    """获取写实风格基础 prompt"""
    return _image_style_prompt


def get_character_traits_for_names(names: list) -> str:
    """根据角色标识列表拼接角色外貌描述"""
    parts = []
    for name in names:
        key = name.strip().lower()
        if key in _character_traits:
            parts.append(_character_traits[key])
    return "; ".join(parts)


async def generate_image_from_narrative(scene_description: str, style_prompt: str, character_traits: str) -> dict:
    """
    基于叙事文本动态生成图片
    prompt 结构: [image style] + Scene: [场景描述] + Characters: [角色特征] + Quality: [质量修饰]
    返回: {"url": str|None, "source": str, "description": str}
    """
    # 组装 prompt
    tech_params = _prompt_library.get("technical_parameters", {})
    quality_mods = ", ".join(tech_params.get("quality_modifiers", []))

    parts = []
    if style_prompt:
        parts.append(style_prompt)
    parts.append(f"Scene: {scene_description}")
    if character_traits:
        parts.append(f"Characters: {character_traits}")
    if quality_mods:
        parts.append(f"Quality: {quality_mods}")

    prompt = "\n\n".join(parts)
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
    local_filename = f"scene_{prompt_hash}"
    local_path = GENERATED_IMAGES_DIR / f"{local_filename}.png"

    # 检查本地缓存
    if prompt_hash in _local_cache and local_path.exists():
        logger.info(f"动态图片使用本地缓存: {local_filename}")
        return {
            "url": f"/api/images/{local_filename}",
            "source": "cached",
            "description": ""
        }

    # 生成图片
    try:
        logger.info(f"动态生成场景图片: {scene_description[:60]}...")
        response = await client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt[:4000],
            size=IMAGE_SIZE,
            quality=IMAGE_QUALITY,
            n=1
        )

        image_url = response.data[0].url
        logger.info(f"动态图片生成成功: {image_url[:80]}")

        # 下载到本地
        try:
            async with httpx.AsyncClient() as http:
                img_resp = await http.get(image_url, timeout=30, follow_redirects=True)
            if img_resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(img_resp.content)
                _local_cache[prompt_hash] = local_filename
                _save_local_cache()
                logger.info(f"动态图片已下载到本地: {local_filename}")
                return {
                    "url": f"/api/images/{local_filename}",
                    "source": "generated",
                    "description": ""
                }
            else:
                logger.warning(f"动态图片下载失败, HTTP {img_resp.status_code}")
        except Exception as e:
            logger.error(f"动态图片下载异常: {e}")

    except Exception as e:
        logger.error(f"动态图像生成失败: {e}")

    # 降级
    return {
        "url": None,
        "source": "fallback",
        "description": "北宋陕北寺庙场景"
    }
