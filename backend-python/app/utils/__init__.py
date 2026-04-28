"""
工具模块索引
统一导出所有工具函数和类
"""
from urllib.parse import quote


def get_inline_content_disposition(filename: str) -> str:
    ascii_filename = filename.encode("ascii", "replace").decode("ascii")
    encoded_filename = quote(filename)
    return f"inline; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"


__all__ = ["get_inline_content_disposition"]
