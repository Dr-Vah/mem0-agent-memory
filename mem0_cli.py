# -*- coding: utf-8 -*-
"""Mem0 通用命令行工具

提供记忆的写入、检索、列出、删除能力，基于本地 Mem0（配置见 mem0_config.py）。

用法：
    python mem0_cli.py add --user-id <用户ID> "<记忆内容>"
    python mem0_cli.py search --user-id <用户ID> "<查询内容>"
    python mem0_cli.py list --user-id <用户ID>
    python mem0_cli.py delete <记忆ID>

示例：
    python mem0_cli.py add --user-id alice "用户喜欢用 Python 写代码"
    python mem0_cli.py search --user-id alice "用户喜欢什么语言"
    python mem0_cli.py list --user-id alice
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mem0_config import get_memory, API_KEY

_PLACEHOLDER = "在这里填写你的API_KEY"


def _check_key():
    if not API_KEY or API_KEY == _PLACEHOLDER:
        print("[!] 请先在 mem0_config.py 中填写 API_KEY", file=sys.stderr)
        sys.exit(1)


def cmd_add(args):
    m = get_memory()
    result = m.add(
        [{"role": "user", "content": args.content}],
        user_id=args.user_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_search(args):
    m = get_memory()
    result = m.search(args.query, filters={"user_id": args.user_id})
    results = result.get("results", [])
    if not results:
        print("（无匹配记忆）")
        return
    for r in results:
        score = r.get("score", 0)
        print(f"- {r.get('memory')}  (score={score:.3f})")


def cmd_list(args):
    m = get_memory()
    result = m.get_all(filters={"user_id": args.user_id}, top_k=args.top_k)
    results = result.get("results", [])
    if not results:
        print("（该用户暂无记忆）")
        return
    for r in results:
        print(f"- [{r.get('id')}] {r.get('memory')}")


def cmd_delete(args):
    m = get_memory()
    m.delete(args.memory_id)
    print(f"已删除记忆: {args.memory_id}")


def main():
    parser = argparse.ArgumentParser(
        prog="mem0_cli",
        description="Mem0 记忆命令行工具（本地持久记忆）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="写入一条记忆")
    p_add.add_argument("--user-id", required=True, help="用户/会话标识")
    p_add.add_argument("content", help="要记忆的内容")
    p_add.set_defaults(func=cmd_add)

    p_search = sub.add_parser("search", help="检索记忆")
    p_search.add_argument("--user-id", required=True, help="用户/会话标识")
    p_search.add_argument("query", help="查询内容")
    p_search.set_defaults(func=cmd_search)

    p_list = sub.add_parser("list", help="列出某用户的全部记忆")
    p_list.add_argument("--user-id", required=True, help="用户/会话标识")
    p_list.add_argument("--top-k", type=int, default=100, help="最多返回条数（默认100）")
    p_list.set_defaults(func=cmd_list)

    p_del = sub.add_parser("delete", help="按 ID 删除一条记忆")
    p_del.add_argument("memory_id", help="记忆 ID（见 list 输出）")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    _check_key()
    args.func(args)


if __name__ == "__main__":
    main()
