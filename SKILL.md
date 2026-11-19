---
name: mem0-memory
description: 使用本地 Mem0 记忆服务读写长期记忆。当任务涉及用户个人偏好、习惯、口味或背景（如第一人称"我"、个性化推荐、个人情况咨询），或需跨会话延续上下文时，应主动查询已有记忆；写入按需触发、不强制。优先使用 MCP 工具 mem0_search/mem0_add/mem0_list，shell 命令 mem0_cli.py 作为备用。
---

# Mem0 记忆服务

## 描述
本地部署的 Mem0 记忆层，为 AI 提供跨会话的持久记忆能力。底层是 mem0ai（向量检索 + LLM 自动提取事实），优先通过 MCP 工具调用，数据持久化在项目 `.mem0/` 目录。

## 使用场景
### 主动查询（应积极触发 search）
- 用户以"我/我的"表达偏好、习惯、口味、计划、约束（如"推荐几首歌""我喜欢..."）
- 请求个性化推荐或针对性建议（歌曲、电影、工具、方案等）
- 询问或涉及用户个人背景（课程、专业、技术栈、工作方式等）
- 需要基于用户历史做决策、给建议或延续上下文

### 写入（按需触发 add，不强制）
- 用户明确要求"记住/记录"某事
- 对话中出现明确且重要的新事实或偏好，值得长期沉淀

## 关键约束
- 运行环境：Python 解释器固定为 `D:\py\NL\python.exe`（mem0ai 安装在该 conda 环境）
- API key 配置在 `mem0_config.py`；若未填写，所有命令会失败
- 记忆按 `user_id` 隔离；`search` 和 `list` 必须用 `--user-id` 指定
- 工具脚本位于 `d:\Trae CN\projects\` 下：`mem0_cli.py`（命令行）、`mem0_config.py`（配置）
- 当前用户（Dr_Vah）的偏好、事实、约束等，一律以 `--user-id Dr_Vah` 存储；其他实体用各自的 `user_id`

## 指令
### 优先使用 MCP 工具（推荐）
若 MCP server `mem0-memory` 已启用，直接调用工具，无需 shell：
- `mem0_search(query)` — 检索记忆；涉及用户偏好/个性化推荐/个人背景时优先调用
- `mem0_add(content)` — 写入记忆；写入前先 search 确认去重
- `mem0_list()` — 列出全部记忆
- `mem0_delete(memory_id)` — 删除一条记忆；发现错误/过时记忆时，先 list 找 id 再删除
（工具的 user_id 默认 Dr_Vah）

### 备用：shell 命令（MCP 不可用时）
工作目录为 `d:\Trae CN\projects`，调用方式如下：

1. 写入记忆前，先检索是否已有相近/重复记忆：
   `D:\py\NL\python.exe "d:\Trae CN\projects\mem0_cli.py" search --user-id <ID> "<待写入内容>"`
2. 写入时自动整理去重：若检索到相近/分散记忆，先 `delete <旧记忆ID>` 删除旧的，再 `add` 合并后的完整记忆；若无相近记忆，直接 `add`：
   `D:\py\NL\python.exe "d:\Trae CN\projects\mem0_cli.py" add --user-id <ID> "<内容>"`
3. 检索记忆（仅查询）：
   `D:\py\NL\python.exe "d:\Trae CN\projects\mem0_cli.py" search --user-id <ID> "<查询>"`
4. 列出某用户全部记忆：
   `D:\py\NL\python.exe "d:\Trae CN\projects\mem0_cli.py" list --user-id <ID>`
5. 按 ID 删除一条记忆：
   `D:\py\NL\python.exe "d:\Trae CN\projects\mem0_cli.py" delete <记忆ID>`

## 示例
- 用户说"记住我喜欢 Python"
  - 调用：`mem0_cli.py add --user-id alice "用户喜欢 Python"`
  - 输出：`{"results": [{"id": "...", "memory": "User likes Python", "event": "ADD"}]}`
- 查询用户偏好
  - 调用：`mem0_cli.py search --user-id alice "用户喜欢什么编程语言"`
  - 输出：`- User likes Python  (score=0.456)`
