# Mem0 记忆服务 —— 部署与复现说明

本说明介绍如何在本地部署 Mem0（AI 记忆层），让 AI 具备跨会话的持久记忆能力，并通过**命令行工具**、**MCP 工具**、**全局技能**三种方式调用。

---

## 1. 这是什么

Mem0 是一个开源记忆层，为 AI 提供"记住用户偏好、事实、习惯，跨会话不遗忘"的能力。它本身不做对话，而是：

- **写入**：把对话中值得记住的事实/偏好，用 LLM 自动提炼、向量化后存进本地向量库
- **检索**：用自然语言检索已有记忆，供 AI 在回答时参考

本项目完成的事（已全部落地并验证）：

1. 本地部署 Mem0（第三方 OpenAI 兼容 API + 本地 Qdrant 向量库 + 本地 SQLite 历史库）
2. 封装了**命令行工具** `mem0_cli.py`（增/查/列/删）
3. 封装了 **MCP 工具**（`mem0_search` / `mem0_add` / `mem0_list` / `mem0_delete`），让 AI 能主动调用
4. 写了**全局技能** `SKILL.md`，告诉 AI 何时该查/写记忆

---

## 2. 环境依赖

| 项 | 要求 |
| --- | --- |
| 操作系统 | Windows（PowerShell） |
| Python | 3.12（建议用 conda 环境） |
| 第三方 API | 需提供 **OpenAI 兼容** 接口，且**同时具备 LLM（对话）和 Embedding（向量）两个接口** |
| Python 包 | `mem0ai`、`fastmcp`（及其依赖） |

> 第三方 API 的两个接口缺一不可：LLM 用于提炼事实，Embedding 用于向量检索。很多服务只有对话接口，没有 Embedding，这类服务**不能直接用**。

---

## 3. 文件清单

| 文件 | 作用 |
| --- | --- |
| `mem0_config.py` | 配置文件：API key、模型名、请求地址、存储路径 |
| `mem0_cli.py` | 命令行工具：add / search / list / delete |
| `mem0_mcp_server.py` | MCP server：暴露 mem0_search / mem0_add / mem0_list / mem0_delete |
| `SKILL.md` | 全局技能说明（告诉 AI 何时调用记忆） |

---

## 4. 部署步骤

### 4.1 创建并激活 conda 环境

```powershell
# 示例：创建一个名为 NL 的环境（名字可自定义）
conda create -n NL python=3.12 -y
conda activate NL
```

> 后续所有命令里的 `python` 都指这个环境里的解释器。若没有激活环境，就用它的**完整路径**，例如 `D:\py\NL\python.exe`。

### 4.2 安装依赖

```powershell
pip install mem0ai fastmcp
```

### 4.3 填写配置

打开 `mem0_config.py`，修改这几项：

```python
API_KEY   = "你的key"            # 必填，你的第三方 key
BASE_URL  = "https://你的地址/v1"  # 你的第三方请求地址
LLM_MODEL = "你的对话模型名"       # 例如 deepseek-chat
EMBED_MODEL = "你的embedding模型名" # 例如 text-embedding-3-small
```

**重点：`embedding_model_dims` 要改成你 embedding 模型的向量维度。**

```python
"vector_store": {
    "provider": "qdrant",
    "config": {
        "path": os.path.join(DATA_DIR, "qdrant"),
        "embedding_model_dims": 2048,   # ← GLM-Embedding-3 是 2048；换模型要改
    },
},
```

- 常见的 OpenAI 系 embedding 是 **1536**（text-embedding-3-small）或 **3072**（text-embedding-3-large）
- 本项目用的 GLM-Embedding-3 是 **2048**
- 不确定维度时，可以先用一句代码测：`len(openai_client.embeddings.create(model=..., input="hi").data[0].embedding)`

### 4.4 验证（命令行）

```powershell
# 写入一条记忆
python mem0_cli.py add --user-id alice "用户喜欢用 Python 写代码"

# 检索
python mem0_cli.py search --user-id alice "用户喜欢什么语言"

# 列出全部
python mem0_cli.py list --user-id alice
```

写入后能看到 `"event": "ADD"` 的结果，检索能返回对应记忆，即说明配置成功。

---

## 5. 配置 MCP（让 AI 主动调用）

以 Trae 为例，在 **MCP Servers 设置界面**，粘贴以下 JSON（把 `python` 路径换成你自己的）：

```json
{
  "mcpServers": {
    "mem0-memory": {
      "command": "D:\\py\\NL\\python.exe",
      "args": [
        "d:\\Trae CN\\projects\\mem0_mcp_server.py"
      ]
    }
  }
}
```

- `command`：你的 conda 环境 Python 解释器完整路径
- `args`：`mem0_mcp_server.py` 的绝对路径

保存并重启后，MCP 列表应出现 `mem0-memory`，含四个工具：`mem0_search` / `mem0_add` / `mem0_list` / `mem0_delete`。

> MCP 工具对 AI 是"始终可见"的，AI 遇到涉及用户偏好、个性化推荐、个人背景的任务时会主动调用——这比技能按需加载更可靠。

---

## 6. 安装全局技能（可选）

把 `SKILL.md` 放到全局技能目录，AI 就能按需加载它作为补充说明，以 Trae 为例：

```
%userprofile%\.trae-cn\skills\mem0-memory\SKILL.md
```

（Windows 下 `%userprofile%` 即 `C:\Users\你的用户名`，需手动创建 `mem0-memory` 子文件夹。）

---

## 7. 关键注意事项

1. **embedding 维度必须匹配**：`embedding_model_dims` 写错会导致写入/检索报维度错误。
2. **第三方 API 要有 Embedding 接口**：没有就换服务，或 LLM 用第三方 + Embedding 用本地 Ollama。
3. **记忆按 user_id 隔离**：查/写都要指定 `--user-id`（CLI）或 `user_id`（MCP，默认 `Dr_Vah`，可改）。
4. **遥测已默认禁用**：`mem0_config.py` 里已设 `MEM0_TELEMETRY=False`，避免命令被 PostHog 超时拖慢，不要删掉这行。
5. **数据存本地**：向量库和历史库都在脚本同目录的 `.mem0/` 文件夹里，删除该文件夹即清空记忆。

---

## 8. 常见问题

**Q：add 返回 `{"results": []}`？**
A：通常是"该内容已存在"（去重）或 embedding 维度不匹配。先用 `list` 确认是否已存在，再核对 `embedding_model_dims`。

**Q：search/list 报 `use filters={'user_id': ...}`？**
A：mem0 新版把 `user_id` 参数改成了 `filters={"user_id": ...}`，本项目的脚本已经按新写法写好了，直接用它即可。

**Q：运行报 `Storage folder ... already accessed by another instance`？**
A：有另一个进程正在用同一个 `.mem0` 目录（比如上一个命令还没退出）。关掉占用进程再跑即可。这是 Qdrant 本地模式的限制，不支持并发访问。
