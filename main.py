#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹大小统计工具
扫描目录并按大小排序展示，找出占用空间最大的文件/文件夹
"""

import os
import argparse
from pathlib import Path


def get_dir_size(folder):
    """递归计算目录大小"""
    total = 0
    try:
        for entry in os.scandir(folder):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += get_dir_size(entry.path)
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass
    return total


def get_top_items(folder, top_n=20, depth=1):
    """获取占用空间最大的项目"""
    folder = Path(folder)
    if not folder.is_dir():
        print(f"[错误] 目录不存在: {folder}")
        return []

    items = []
    try:
        for entry in os.scandir(folder):
            try:
                if entry.is_file(follow_symlinks=False):
                    size = entry.stat(follow_symlinks=False).st_size
                    items.append((entry.name, size, "file"))
                elif entry.is_dir(follow_symlinks=False):
                    size = get_dir_size(entry.path)
                    items.append((entry.name, size, "dir"))
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass

    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top_n]


def format_size(size):
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def main():
    parser = argparse.ArgumentParser(description="文件夹大小统计工具")
    parser.add_argument("folder", help="目标文件夹路径")
    parser.add_argument("--top", type=int, default=20, help="显示前 N 项（默认 20）")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"[错误] 目录不存在: {folder}")
        return

    total_size = get_dir_size(folder)
    print(f"目录: {folder}")
    print(f"总大小: {format_size(total_size)}")
    print(f"{'=' * 70}")
    print(f"{'类型':<6} {'大小':>12}  {'名称'}")
    print(f"{'-' * 70}")

    items = get_top_items(folder, top_n=args.top)
    for name, size, typ in items:
        icon = "📁" if typ == "dir" else "📄"
        print(f"{icon:<4} {format_size(size):>12}  {name}")


if __name__ == "__main__":
    main()
