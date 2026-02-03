# utils/dir_tree.py
"""
项目目录树生成器
用法：
1. 直接运行：python utils/dir_tree.py
2. 在代码中导入：from utils.dir_tree import print_project_tree
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Optional


class DirectoryTree:
    """生成项目目录树的类"""

    # 默认忽略的目录和文件
    DEFAULT_IGNORE = {
        '.git', '.idea', '.vscode', '__pycache__', '.pytest_cache',
        'node_modules', 'venv', 'env', '.env', '.venv',
        '.gitignore', '.env.local', '.env.*.local',
        '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
        '*.log', '*.sqlite', '*.db', '.DS_Store',
        'Thumbs.db', 'desktop.ini', '.coverage', 'htmlcov',
        'dist', 'build', '*.egg-info', '.mypy_cache',
        '.hypothesis', '.tox', '.nox', '.benchmarks',
    }

    def __init__(
            self,
            root_dir: str = ".",
            max_depth: int = 7,
            ignore_patterns: Optional[Set[str]] = None,
            show_hidden: bool = False,
            show_files: bool = True,
            show_size: bool = False,
    ):
        """
        初始化目录树生成器

        Args:
            root_dir: 根目录路径
            max_depth: 最大深度
            ignore_patterns: 要忽略的模式集合
            show_hidden: 是否显示隐藏文件/目录
            show_files: 是否显示文件
            show_size: 是否显示文件大小
        """
        self.root_path = Path(root_dir).resolve()
        self.max_depth = max_depth
        self.show_hidden = show_hidden
        self.show_files = show_files
        self.show_size = show_size

        # 合并默认忽略模式和自定义忽略模式
        self.ignore_patterns = set(self.DEFAULT_IGNORE)
        if ignore_patterns:
            self.ignore_patterns.update(ignore_patterns)

        # 输出统计信息
        self.dir_count = 0
        self.file_count = 0

        # 用于构建树状结构的符号
        self.BRANCH = "├── "
        self.LAST_BRANCH = "└── "
        self.VERTICAL = "│   "
        self.INDENT = "    "

    def _should_ignore(self, name: str, is_dir: bool) -> bool:
        """判断是否应该忽略该条目"""
        # 隐藏文件处理
        if not self.show_hidden and name.startswith('.'):
            return True

        # 检查是否在忽略模式中
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                # 通配符模式，如 *.pyc
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True

        return False

    def _get_size_str(self, size_bytes: int) -> str:
        """将字节数转换为可读的字符串"""
        if size_bytes < 1024:
            return f"({size_bytes} B)"
        elif size_bytes < 1024 * 1024:
            return f"({size_bytes / 1024:.1f} KB)"
        else:
            return f"({size_bytes / (1024 * 1024):.1f} MB)"

    def _walk_directory(
            self,
            directory: Path,
            prefix: str = "",
            depth: int = 0,
            is_last: bool = True
    ) -> List[str]:
        """递归遍历目录，生成树状结构行"""
        if depth > self.max_depth:
            return []

        lines = []
        current_dir_name = directory.name if depth > 0 else str(directory)

        # 当前目录的行
        if depth == 0:
            lines.append(f"{current_dir_name}/")
        else:
            connector = self.LAST_BRANCH if is_last else self.BRANCH
            lines.append(f"{prefix}{connector}{current_dir_name}/")

        # 获取目录内容并排序
        try:
            items = list(directory.iterdir())

            # 过滤忽略的项目
            filtered_items = []
            for item in items:
                if self._should_ignore(item.name, item.is_dir()):
                    continue
                filtered_items.append(item)

            # 排序：目录在前，文件在后，都按字母顺序
            filtered_items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            # 统计
            self.dir_count += sum(1 for item in filtered_items if item.is_dir())
            self.file_count += sum(1 for item in filtered_items if not item.is_dir())

            # 递归处理每个项目
            for i, item in enumerate(filtered_items):
                is_last_item = (i == len(filtered_items) - 1)

                # 构建新的前缀
                if depth == 0:
                    new_prefix = ""
                else:
                    new_prefix = prefix + (self.INDENT if is_last else self.VERTICAL)

                if item.is_dir():
                    # 处理子目录
                    sub_lines = self._walk_directory(
                        item, new_prefix, depth + 1, is_last_item
                    )
                    lines.extend(sub_lines)
                elif self.show_files:
                    # 处理文件
                    connector = self.LAST_BRANCH if is_last_item else self.BRANCH
                    size_str = ""
                    if self.show_size:
                        try:
                            size = item.stat().st_size
                            size_str = " " + self._get_size_str(size)
                        except:
                            size_str = " (?)"
                    lines.append(f"{new_prefix}{connector}{item.name}{size_str}")

        except PermissionError:
            lines.append(f"{prefix}{self.INDENT}[权限不足]")
        except Exception as e:
            lines.append(f"{prefix}{self.INDENT}[错误: {str(e)}]")

        return lines

    def generate(self) -> str:
        """生成目录树字符串"""
        if not self.root_path.exists():
            return f"错误: 目录不存在 - {self.root_path}"

        if not self.root_path.is_dir():
            return f"错误: 不是目录 - {self.root_path}"

        # 重置统计
        self.dir_count = 0
        self.file_count = 0

        # 生成树状结构
        tree_lines = self._walk_directory(self.root_path)

        # 添加统计信息
        if tree_lines:
            tree_lines.append("")
            tree_lines.append(f"统计: {self.dir_count} 个目录, {self.file_count} 个文件")
            tree_lines.append(f"根目录: {self.root_path}")

        return "\n".join(tree_lines)

    def print_tree(self) -> None:
        """打印目录树"""
        tree_str = self.generate()
        print(tree_str)

    def save_to_file(self, filepath: str) -> None:
        """将目录树保存到文件"""
        tree_str = self.generate()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(tree_str)
        print(f"目录树已保存到: {filepath}")


def print_project_tree(
        root_dir: str = ".",
        max_depth: int = 7,
        ignore_patterns: Optional[List[str]] = None,
        show_hidden: bool = False,
        show_files: bool = True,
        show_size: bool = False,
        save_to: Optional[str] = None,
) -> None:
    """
    打印项目目录树的便捷函数

    Args:
        root_dir: 根目录，默认为当前目录
        max_depth: 最大显示深度
        ignore_patterns: 要忽略的文件/目录模式列表
        show_hidden: 是否显示隐藏文件
        show_files: 是否显示文件
        show_size: 是否显示文件大小
        save_to: 保存到的文件路径（可选）
    """
    ignore_set = set(ignore_patterns) if ignore_patterns else None

    tree = DirectoryTree(
        root_dir=root_dir,
        max_depth=max_depth,
        ignore_patterns=ignore_set,
        show_hidden=show_hidden,
        show_files=show_files,
        show_size=show_size,
    )

    if save_to:
        tree.save_to_file(save_to)
    else:
        tree.print_tree()


def get_project_root() -> Path:
    """自动检测项目根目录（包含 .git 或 pyproject.toml 的目录）"""
    current = Path.cwd()

    # 向上查找包含特定文件的目录
    for parent in [current] + list(current.parents):
        if (parent / '.git').exists() or (parent / 'pyproject.toml').exists():
            return parent

    return current


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="生成项目目录树")
    parser.add_argument("root_dir", nargs="?", default=".", help="根目录路径")
    parser.add_argument("-d", "--depth", type=int, default=7, help="最大深度")
    parser.add_argument("-a", "--all", action="store_true", help="显示隐藏文件")
    parser.add_argument("-f", "--files", action="store_true", help="显示文件")
    parser.add_argument("-s", "--size", action="store_true", help="显示文件大小")
    parser.add_argument("-o", "--output", help="输出到文件")
    parser.add_argument("--find-root", action="store_true", help="自动查找项目根目录")
    parser.add_argument("--no-files", action="store_true", help="不显示文件")
    parser.add_argument("--ignore", nargs="+", help="额外的忽略模式")

    args = parser.parse_args()

    # 确定根目录
    if args.find_root:
        root_dir = str(get_project_root())
        print(f"检测到项目根目录: {root_dir}")
    else:
        root_dir = args.root_dir

    # 确定是否显示文件
    show_files = not args.no_files
    if args.files:
        show_files = True

    # 调用函数
    print_project_tree(
        root_dir=root_dir,
        max_depth=args.depth,
        ignore_patterns=args.ignore,
        show_hidden=args.all,
        show_files=show_files,
        show_size=args.size,
        save_to=args.output,
    )