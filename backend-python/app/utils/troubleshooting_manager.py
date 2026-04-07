"""
错误记录管理器模块

功能：
1. 自动记录系统或应用程序中出现的错误信息
2. 确保记录内容不包含重复条目
3. 实时将当前出现的问题与文档中已记录的问题进行对比分析
4. 建立有效的机制杜绝已记录过的问题再次被重复记录

作者：系统自动生成
日期：2026-03-19
"""

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class ErrorRecord:
    """
    错误记录实体类
    
    用于表示单个错误记录的所有属性
    """
    
    def __init__(
        self,
        error_id: str,
        error_code: str,
        category: str,
        title: str,
        error_message: str,
        reason: str,
        solution: str,
        related_files: str = "",
        code_example: str = "",
        created_at: str = "",
        occurrence_count: int = 1,
        last_occurred_at: str = "",
        status: str = "active"
    ):
        self.error_id = error_id
        self.error_code = error_code
        self.category = category
        self.title = title
        self.error_message = error_message
        self.reason = reason
        self.solution = solution
        self.related_files = related_files
        self.code_example = code_example
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.occurrence_count = occurrence_count
        self.last_occurred_at = last_occurred_at or self.created_at
        self.status = status
    
    def to_dict(self) -> dict:
        """
        将错误记录转换为字典格式
        
        Returns:
            dict: 错误记录的字典表示
        """
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "category": self.category,
            "title": self.title,
            "error_message": self.error_message,
            "reason": self.reason,
            "solution": self.solution,
            "related_files": self.related_files,
            "code_example": self.code_example,
            "created_at": self.created_at,
            "occurrence_count": self.occurrence_count,
            "last_occurred_at": self.last_occurred_at,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ErrorRecord':
        """
        从字典创建错误记录实例
        
        Args:
            data: 包含错误记录数据的字典
            
        Returns:
            ErrorRecord: 错误记录实例
        """
        return cls(
            error_id=data.get("error_id", ""),
            error_code=data.get("error_code", ""),
            category=data.get("category", ""),
            title=data.get("title", ""),
            error_message=data.get("error_message", ""),
            reason=data.get("reason", ""),
            solution=data.get("solution", ""),
            related_files=data.get("related_files", ""),
            code_example=data.get("code_example", ""),
            created_at=data.get("created_at", ""),
            occurrence_count=data.get("occurrence_count", 1),
            last_occurred_at=data.get("last_occurred_at", ""),
            status=data.get("status", "active")
        )


class ErrorIdentifier:
    """
    错误唯一标识生成器
    
    通过多种方式生成错误的唯一标识，确保相同错误不会重复记录
    """
    
    @staticmethod
    def generate_error_id(
        error_message: str,
        category: str = "",
        stack_trace: str = "",
        file_path: str = ""
    ) -> str:
        """
        生成错误唯一标识
        
        使用错误信息、类别、堆栈跟踪和文件路径的组合生成唯一标识
        
        Args:
            error_message: 错误信息
            category: 错误类别
            stack_trace: 堆栈跟踪
            file_path: 相关文件路径
            
        Returns:
            str: 32位MD5哈希值作为唯一标识
        """
        content_parts = []
        
        normalized_message = ErrorIdentifier._normalize_message(error_message)
        content_parts.append(normalized_message)
        
        if category:
            content_parts.append(category.lower().strip())
        
        if stack_trace:
            normalized_trace = ErrorIdentifier._extract_key_trace_info(stack_trace)
            content_parts.append(normalized_trace)
        
        if file_path:
            normalized_path = file_path.replace("\\", "/").lower().strip()
            content_parts.append(normalized_path)
        
        content = "|".join(content_parts)
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _normalize_message(message: str) -> str:
        """
        标准化错误信息
        
        移除动态内容（如时间戳、ID、路径等），保留核心错误模式
        
        Args:
            message: 原始错误信息
            
        Returns:
            str: 标准化后的错误信息
        """
        if not message:
            return ""
        
        normalized = message.strip()
        
        patterns_to_remove = [
            (r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?', ''),
            (r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', 'UUID'),
            (r'\b\d+\.\d+\.\d+\.\d+\b', 'IP'),
            (r':\d{4,5}', ':PORT'),
            (r'/[\w/\-\.]+', 'PATH'),
            (r'\\[\w\\\-\.]+', 'PATH'),
            (r'\b\d{10,}\b', 'ID'),
            (r'0x[0-9a-fA-F]+', 'HEX'),
        ]
        
        for pattern, replacement in patterns_to_remove:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.lower().strip()
    
    @staticmethod
    def _extract_key_trace_info(stack_trace: str) -> str:
        """
        从堆栈跟踪中提取关键信息
        
        提取文件名、函数名和行号等关键信息
        
        Args:
            stack_trace: 原始堆栈跟踪
            
        Returns:
            str: 关键信息字符串
        """
        if not stack_trace:
            return ""
        
        key_info = []
        
        file_pattern = r'File "([^"]+)", line (\d+), in (\w+)'
        matches = re.findall(file_pattern, stack_trace)
        
        for match in matches[:3]:
            file_path, line_no, func_name = match
            file_name = os.path.basename(file_path)
            key_info.append(f"{file_name}:{func_name}")
        
        return "|".join(key_info)
    
    @staticmethod
    def generate_error_code(category: str, existing_codes: list) -> str:
        """
        生成错误编码
        
        格式：类别前缀-序号（如 BE-001, FE-002）
        
        Args:
            category: 错误类别
            existing_codes: 已存在的错误编码列表
            
        Returns:
            str: 新的错误编码
        """
        category_prefixes = {
            "后端错误": "BE",
            "前端错误": "FE",
            "部署错误": "DEPLOY",
            "数据库错误": "DB",
            "环境配置错误": "ENV",
            "API错误": "API",
            "业务逻辑错误": "BIZ",
            "权限错误": "AUTH",
            "文件错误": "FILE",
            "网络错误": "NET"
        }
        
        prefix = category_prefixes.get(category, "ERR")
        
        max_num = 0
        for code in existing_codes:
            if code.startswith(prefix + "-"):
                try:
                    num = int(code.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        
        return f"{prefix}-{max_num + 1:03d}"


class DuplicateDetector:
    """
    重复检测器
    
    检测错误是否已经记录，支持多种匹配策略
    """
    
    def __init__(self, existing_records: list):
        """
        初始化重复检测器
        
        Args:
            existing_records: 已存在的错误记录列表
        """
        self.existing_records = existing_records
        self._build_index()
    
    def _build_index(self):
        """
        构建错误索引以加速查询
        """
        self.id_index = {}
        self.message_index = {}
        self.code_index = {}
        
        for record in self.existing_records:
            if isinstance(record, dict):
                record = ErrorRecord.from_dict(record)
            
            if record.error_id:
                self.id_index[record.error_id] = record
            
            if record.error_code:
                self.code_index[record.error_code] = record
            
            normalized_msg = ErrorIdentifier._normalize_message(record.error_message)
            if normalized_msg:
                self.message_index[normalized_msg] = record
    
    def is_duplicate(
        self,
        error_message: str,
        category: str = "",
        stack_trace: str = "",
        file_path: str = "",
        similarity_threshold: float = 0.85
    ) -> tuple:
        """
        检测错误是否重复
        
        Args:
            error_message: 错误信息
            category: 错误类别
            stack_trace: 堆栈跟踪
            file_path: 相关文件路径
            similarity_threshold: 相似度阈值
            
        Returns:
            tuple: (是否重复, 匹配的记录, 匹配类型)
        """
        error_id = ErrorIdentifier.generate_error_id(
            error_message, category, stack_trace, file_path
        )
        
        if error_id in self.id_index:
            return True, self.id_index[error_id], "exact_id"
        
        normalized_msg = ErrorIdentifier._normalize_message(error_message)
        if normalized_msg in self.message_index:
            return True, self.message_index[normalized_msg], "exact_message"
        
        similar_record = self._find_similar_record(
            error_message, category, similarity_threshold
        )
        if similar_record:
            return True, similar_record, "similar"
        
        return False, None, None
    
    def _find_similar_record(
        self,
        error_message: str,
        category: str,
        threshold: float
    ) -> Optional[ErrorRecord]:
        """
        查找相似的错误记录
        
        使用模糊匹配算法查找相似的错误
        
        Args:
            error_message: 错误信息
            category: 错误类别
            threshold: 相似度阈值
            
        Returns:
            Optional[ErrorRecord]: 相似的错误记录，如果没有找到则返回None
        """
        normalized_msg = ErrorIdentifier._normalize_message(error_message)
        
        for record in self.existing_records:
            if isinstance(record, dict):
                record = ErrorRecord.from_dict(record)
            
            if category and record.category != category:
                continue
            
            record_normalized = ErrorIdentifier._normalize_message(record.error_message)
            
            similarity = self._calculate_similarity(normalized_msg, record_normalized)
            
            if similarity >= threshold:
                return record
        
        return None
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度
        
        使用编辑距离算法计算相似度
        
        Args:
            str1: 第一个字符串
            str2: 第二个字符串
            
        Returns:
            float: 相似度（0-1之间）
        """
        if not str1 or not str2:
            return 0.0
        
        if str1 == str2:
            return 1.0
        
        len1, len2 = len(str1), len(str2)
        
        if abs(len1 - len2) > max(len1, len2) * 0.5:
            return 0.0
        
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,
                        dp[i][j-1] + 1,
                        dp[i-1][j-1] + 1
                    )
        
        edit_distance = dp[len1][len2]
        max_len = max(len1, len2)
        
        return 1.0 - (edit_distance / max_len)


class TroubleshootingManager:
    """
    错误记录管理器主类
    
    提供完整的错误记录管理功能，包括记录、查询、更新和导出
    """
    
    def __init__(self, troubleshooting_file: str, cache_file: str = None):
        """
        初始化错误记录管理器
        
        Args:
            troubleshooting_file: TROUBLESHOOTING.md 文件路径
            cache_file: 缓存文件路径（JSON格式），用于存储解析后的错误记录
        """
        self.troubleshooting_file = Path(troubleshooting_file)
        self.cache_file = Path(cache_file) if cache_file else self.troubleshooting_file.with_suffix('.json')
        
        self.records: list[ErrorRecord] = []
        self.detector: Optional[DuplicateDetector] = None
        
        self._load_records()
    
    def _load_records(self):
        """
        加载错误记录
        
        优先从缓存文件加载，如果缓存不存在则从MD文件解析
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [ErrorRecord.from_dict(r) for r in data.get('records', [])]
                logger.info(f"从缓存加载了 {len(self.records)} 条错误记录")
            except Exception as e:
                logger.warning(f"加载缓存文件失败: {e}，将从MD文件解析")
                self._parse_md_file()
        else:
            self._parse_md_file()
        
        self.detector = DuplicateDetector([r.to_dict() for r in self.records])
    
    def _parse_md_file(self):
        """
        解析 TROUBLESHOOTING.md 文件
        
        提取所有已记录的错误信息
        """
        if not self.troubleshooting_file.exists():
            logger.warning(f"TROUBLESHOOTING.md 文件不存在: {self.troubleshooting_file}")
            return
        
        with open(self.troubleshooting_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.records = []
        
        section_pattern = r'### ([A-Z]+-\d+):\s*(.+?)(?=\n)'
        sections = re.split(section_pattern, content)
        
        current_category = ""
        category_pattern = r'## ([\u4e00-\u9fa5]+错误)'
        category_matches = list(re.finditer(category_pattern, content))
        
        for i, match in enumerate(category_matches):
            category = match.group(1)
            start_pos = match.end()
            end_pos = category_matches[i + 1].start() if i + 1 < len(category_matches) else len(content)
            section_content = content[start_pos:end_pos]
            
            error_blocks = re.split(r'---\n', section_content)
            
            for block in error_blocks:
                if not block.strip():
                    continue
                
                record = self._parse_error_block(block, category)
                if record:
                    self.records.append(record)
        
        self._save_cache()
        logger.info(f"从MD文件解析了 {len(self.records)} 条错误记录")
    
    def _parse_error_block(self, block: str, category: str) -> Optional[ErrorRecord]:
        """
        解析单个错误块
        
        Args:
            block: 错误块文本
            category: 错误类别
            
        Returns:
            Optional[ErrorRecord]: 解析后的错误记录，如果解析失败则返回None
        """
        code_match = re.search(r'### ([A-Z]+-\d+)', block)
        title_match = re.search(r'### [A-Z]+-\d+:\s*(.+?)(?=\n)', block)
        
        if not code_match:
            return None
        
        error_code = code_match.group(1)
        title = title_match.group(1).strip() if title_match else ""
        
        error_msg_match = re.search(r'\*\*错误信息：?\*\*\s*```\s*(.+?)\s*```', block, re.DOTALL)
        error_message = error_msg_match.group(1).strip() if error_msg_match else ""
        
        reason_match = re.search(r'\*\*原因：?\*\*\s*(.+?)(?=\n\*\*|\n---|\n###|$)', block, re.DOTALL)
        reason = reason_match.group(1).strip() if reason_match else ""
        
        solution_match = re.search(r'\*\*解决方案：?\*\*\s*(.+?)(?=\n\*\*|\n---|\n###|$)', block, re.DOTALL)
        solution = solution_match.group(1).strip() if solution_match else ""
        
        files_match = re.search(r'\*\*相关文件：?\*\*\s*(.+?)(?=\n)', block)
        related_files = files_match.group(1).strip() if files_match else ""
        
        code_match = re.search(r'\*\*修改示例：?\*\*\s*```[\w]*\s*(.+?)\s*```', block, re.DOTALL)
        code_example = code_match.group(1).strip() if code_match else ""
        
        error_id = ErrorIdentifier.generate_error_id(error_message, category)
        
        return ErrorRecord(
            error_id=error_id,
            error_code=error_code,
            category=category,
            title=title,
            error_message=error_message,
            reason=reason,
            solution=solution,
            related_files=related_files,
            code_example=code_example
        )
    
    def _save_cache(self):
        """
        保存错误记录到缓存文件
        """
        try:
            data = {
                "version": "1.0",
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "records": [r.to_dict() for r in self.records]
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"缓存已保存到 {self.cache_file}")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def record_error(
        self,
        error_message: str,
        category: str,
        reason: str,
        solution: str,
        title: str = "",
        related_files: str = "",
        code_example: str = "",
        stack_trace: str = "",
        file_path: str = "",
        auto_update_md: bool = True
    ) -> dict:
        """
        记录新的错误
        
        自动检测重复并记录新错误
        
        Args:
            error_message: 错误信息
            category: 错误类别
            reason: 错误原因
            solution: 解决方案
            title: 错误标题
            related_files: 相关文件
            code_example: 代码示例
            stack_trace: 堆栈跟踪
            file_path: 相关文件路径
            auto_update_md: 是否自动更新MD文件
            
        Returns:
            dict: 包含操作结果和错误记录的字典
        """
        is_duplicate, matched_record, match_type = self.detector.is_duplicate(
            error_message, category, stack_trace, file_path
        )
        
        if is_duplicate:
            matched_record.occurrence_count += 1
            matched_record.last_occurred_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self._save_cache()
            
            logger.info(f"检测到重复错误 [{match_type}]: {matched_record.error_code}")
            
            return {
                "success": True,
                "is_duplicate": True,
                "match_type": match_type,
                "record": matched_record.to_dict(),
                "message": f"错误已存在（{matched_record.error_code}），已更新出现次数"
            }
        
        error_id = ErrorIdentifier.generate_error_id(
            error_message, category, stack_trace, file_path
        )
        
        existing_codes = [r.error_code for r in self.records]
        error_code = ErrorIdentifier.generate_error_code(category, existing_codes)
        
        if not title:
            title = self._generate_title(error_message)
        
        new_record = ErrorRecord(
            error_id=error_id,
            error_code=error_code,
            category=category,
            title=title,
            error_message=error_message,
            reason=reason,
            solution=solution,
            related_files=related_files,
            code_example=code_example
        )
        
        self.records.append(new_record)
        
        self.detector = DuplicateDetector([r.to_dict() for r in self.records])
        
        self._save_cache()
        
        if auto_update_md:
            self._update_md_file(new_record)
        
        logger.info(f"新错误已记录: {error_code}")
        
        return {
            "success": True,
            "is_duplicate": False,
            "record": new_record.to_dict(),
            "message": f"新错误已记录（{error_code}）"
        }
    
    def _generate_title(self, error_message: str) -> str:
        """
        根据错误信息生成标题
        
        Args:
            error_message: 错误信息
            
        Returns:
            str: 生成的标题
        """
        first_line = error_message.split('\n')[0]
        
        if len(first_line) > 50:
            return first_line[:47] + "..."
        
        return first_line
    
    def _update_md_file(self, new_record: ErrorRecord):
        """
        更新 TROUBLESHOOTING.md 文件
        
        将新错误记录追加到对应类别下
        
        Args:
            new_record: 新的错误记录
        """
        try:
            with open(self.troubleshooting_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            error_section = self._format_error_section(new_record)
            
            category_pattern = f'## {new_record.category}'
            category_match = re.search(category_pattern, content)
            
            if category_match:
                next_category_pattern = r'\n## ([\u4e00-\u9fa5]+错误)'
                next_match = re.search(next_category_pattern, content[category_match.end():])
                
                if next_match:
                    insert_pos = category_match.end() + next_match.start()
                    content = content[:insert_pos] + error_section + "\n---\n" + content[insert_pos:]
                else:
                    dev_section_pattern = r'\n## 开发规范'
                    dev_match = re.search(dev_section_pattern, content)
                    
                    if dev_match:
                        content = content[:dev_match.start()] + error_section + "\n---\n" + content[dev_match.start():]
                    else:
                        content += "\n" + error_section + "\n---\n"
            else:
                dev_section_pattern = r'\n## 开发规范'
                dev_match = re.search(dev_section_pattern, content)
                
                if dev_match:
                    new_category_section = f"\n## {new_record.category}\n\n{error_section}\n---\n"
                    content = content[:dev_match.start()] + new_category_section + content[dev_match.start():]
                else:
                    content += f"\n## {new_record.category}\n\n{error_section}\n---\n"
            
            self._update_changelog(content)
            
            with open(self.troubleshooting_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"TROUBLESHOOTING.md 已更新: {new_record.error_code}")
            
        except Exception as e:
            logger.error(f"更新MD文件失败: {e}")
    
    def _format_error_section(self, record: ErrorRecord) -> str:
        """
        格式化错误记录为Markdown格式
        
        Args:
            record: 错误记录
            
        Returns:
            str: Markdown格式的错误记录
        """
        section = f"\n### {record.error_code}: {record.title}\n\n"
        
        section += f"**错误信息：**\n```\n{record.error_message}\n```\n\n"
        
        section += f"**原因：** {record.reason}\n\n"
        
        section += f"**解决方案：**\n{record.solution}\n"
        
        if record.related_files:
            section += f"\n**相关文件：** {record.related_files}\n"
        
        if record.code_example:
            section += f"\n**修改示例：**\n```python\n{record.code_example}\n```\n"
        
        return section
    
    def _update_changelog(self, content: str) -> str:
        """
        更新变更日志
        
        Args:
            content: 文档内容
            
        Returns:
            str: 更新后的文档内容
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        changelog_pattern = r'(\| 日期 +\| 更新内容 +\|\n\|[-| ]+\|[-| ]+\|\n)'
        changelog_match = re.search(changelog_pattern, content)
        
        if changelog_match:
            new_entry = f"| {today} | 新增错误记录 |\n"
            content = content[:changelog_match.end()] + new_entry + content[changelog_match.end():]
        
        return content
    
    def check_before_operation(self, error_message: str, category: str = "") -> dict:
        """
        操作前检查
        
        在用户进行相关操作时，实时将当前出现的问题与文档中已记录的问题进行对比分析
        
        Args:
            error_message: 错误信息
            category: 错误类别
            
        Returns:
            dict: 检查结果，包含是否已记录、相关记录等信息
        """
        is_duplicate, matched_record, match_type = self.detector.is_duplicate(
            error_message, category
        )
        
        result = {
            "has_record": is_duplicate,
            "match_type": match_type,
            "suggestion": ""
        }
        
        if is_duplicate and matched_record:
            result["record"] = matched_record.to_dict()
            result["suggestion"] = f"此问题已有记录（{matched_record.error_code}），请参考解决方案：\n{matched_record.solution}"
        else:
            result["suggestion"] = "此问题尚未记录，建议记录错误信息以便后续参考。"
        
        return result
    
    def search_records(
        self,
        keyword: str = "",
        category: str = "",
        error_code: str = ""
    ) -> list:
        """
        搜索错误记录
        
        Args:
            keyword: 关键词
            category: 错误类别
            error_code: 错误编码
            
        Returns:
            list: 匹配的错误记录列表
        """
        results = []
        
        for record in self.records:
            if error_code and record.error_code != error_code:
                continue
            
            if category and record.category != category:
                continue
            
            if keyword:
                keyword_lower = keyword.lower()
                if (keyword_lower not in record.title.lower() and
                    keyword_lower not in record.error_message.lower() and
                    keyword_lower not in record.reason.lower() and
                    keyword_lower not in record.solution.lower()):
                    continue
            
            results.append(record.to_dict())
        
        return results
    
    def get_statistics(self) -> dict:
        """
        获取错误统计信息
        
        Returns:
            dict: 统计信息
        """
        stats = {
            "total_count": len(self.records),
            "by_category": {},
            "recent_errors": [],
            "frequent_errors": []
        }
        
        for record in self.records:
            category = record.category
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        sorted_by_occurrence = sorted(
            self.records,
            key=lambda r: r.occurrence_count,
            reverse=True
        )
        stats["frequent_errors"] = [
            {
                "error_code": r.error_code,
                "title": r.title,
                "occurrence_count": r.occurrence_count
            }
            for r in sorted_by_occurrence[:5]
        ]
        
        sorted_by_date = sorted(
            self.records,
            key=lambda r: r.last_occurred_at,
            reverse=True
        )
        stats["recent_errors"] = [
            {
                "error_code": r.error_code,
                "title": r.title,
                "last_occurred_at": r.last_occurred_at
            }
            for r in sorted_by_date[:5]
        ]
        
        return stats


_manager_instance: Optional[TroubleshootingManager] = None


def get_troubleshooting_manager() -> TroubleshootingManager:
    """
    获取错误记录管理器单例
    
    Returns:
        TroubleshootingManager: 错误记录管理器实例
    """
    global _manager_instance
    
    if _manager_instance is None:
        project_root = Path(__file__).parent.parent.parent.parent
        troubleshooting_file = project_root / "TROUBLESHOOTING.md"
        cache_file = project_root / "troubleshooting_cache.json"
        
        _manager_instance = TroubleshootingManager(
            str(troubleshooting_file),
            str(cache_file)
        )
    
    return _manager_instance
