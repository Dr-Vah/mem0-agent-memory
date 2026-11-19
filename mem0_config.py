# -*- coding: utf-8 -*-
"""Mem0 本地配置（路径 A）

使用前：
1. 把下面的 API_KEY 替换成你的第三方 key（OpenAI 兼容接口）
2. 运行 mem0_cli.py 测试（add / search / list / delete）

说明：
- LLM 和 Embedding 走第三方 OpenAI 兼容接口
- 向量库用本地 Qdrant，历史用本地 SQLite，数据都放在本项目的 .mem0 目录下
"""
import os

# 禁用 Mem0 遥测（PostHog 上传超时会导致命令慢退出）
os.environ["MEM0_TELEMETRY"] = "False"

# ===== 在这里填写你的 API KEY =====
API_KEY = "在这里填写你的API_KEY"

# 第三方请求地址（OpenAI 兼容）
BASE_URL = "https://llmapi.paratera.com/v1"

# 模型名
LLM_MODEL = "DeepSeek-V4-Pro-0813"
EMBED_MODEL = "GLM-Embedding-3"

# 本地数据目录（向量库 + 历史库）
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mem0")

CONFIG = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": LLM_MODEL,
            "api_key": API_KEY,
            "openai_base_url": BASE_URL,
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": EMBED_MODEL,
            "api_key": API_KEY,
            "openai_base_url": BASE_URL,
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": os.path.join(DATA_DIR, "qdrant"),
            "embedding_model_dims": 2048,
        },
    },
    "history_db_path": os.path.join(DATA_DIR, "history.db"),
}


def get_memory():
    """返回配置好的 Mem0 Memory 实例"""
    from mem0 import Memory

    return Memory.from_config(CONFIG)
