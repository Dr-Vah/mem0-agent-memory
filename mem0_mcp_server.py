# -*- coding: utf-8 -*-
r"""Mem0 记忆服务 MCP Server

把本地 Mem0 记忆能力暴露为 MCP 工具，供 Trae 等 MCP 客户端调用。
工具对 agent 始终可见，agent 遇到涉及用户偏好/个性化推荐/个人背景的任务时会主动调用。

运行方式（stdio）：
    D:\py\NL\python.exe "d:\Trae CN\projects\mem0_mcp_server.py"
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP

mcp = FastMCP("mem0-memory")

_memory = None


def _get_memory():
    """懒加载并缓存 Memory 实例，避免重复初始化与 Qdrant 锁冲突"""
    global _memory
    if _memory is None:
        from mem0_config import get_memory
        _memory = get_memory()
    return _memory


@mcp.tool()
def mem0_search(query: str, user_id: str = "Dr_Vah") -> str:
    """检索用户的长期记忆。当任务涉及用户个人偏好、习惯、口味、背景，或需要个性化推荐（如歌曲、电影、工具）、延续上下文时，应优先调用此工具查询已有记忆。

    Args:
        query: 检索内容，用自然语言描述，如"用户的音乐偏好"
        user_id: 用户标识，默认 Dr_Vah
    """
    m = _get_memory()
    result = m.search(query, filters={"user_id": user_id})
    results = result.get("results", [])
    if not results:
        return "（无匹配记忆）"
    lines = [f"- {r.get('memory')}  (score={r.get('score', 0):.3f})" for r in results]
    return "\n".join(lines)


@mcp.tool()
def mem0_add(content: str, user_id: str = "Dr_Vah") -> str:
    """写入一条长期记忆。仅当用户明确要求记住/记录，或对话中出现明确且重要的新事实、偏好时使用。写入前应先用 mem0_search 确认是否已有相近记忆，避免重复。

    Args:
        content: 要记忆的内容
        user_id: 用户标识，默认 Dr_Vah
    """
    m = _get_memory()
    result = m.add([{"role": "user", "content": content}], user_id=user_id)
    return str(result)


@mcp.tool()
def mem0_list(user_id: str = "Dr_Vah") -> str:
    """列出某用户的全部长期记忆。

    Args:
        user_id: 用户标识，默认 Dr_Vah
    """
    m = _get_memory()
    result = m.get_all(filters={"user_id": user_id}, top_k=100)
    results = result.get("results", [])
    if not results:
        return "（该用户暂无记忆）"
    lines = [f"- [{r.get('id')}] {r.get('memory')}" for r in results]
    return "\n".join(lines)


@mcp.tool()
def mem0_delete(memory_id: str) -> str:
    """按 ID 删除一条记忆。当发现某条记忆内容有误、过时或需要纠正时使用。先用 mem0_list（或 mem0_search）拿到 memory_id，再调用本工具删除。

    Args:
        memory_id: 记忆 ID（形如 UUID，见 mem0_list 输出中括号里的内容）
    """
    m = _get_memory()
    m.delete(memory_id)
    return f"已删除记忆: {memory_id}"


if __name__ == "__main__":
    mcp.run()
