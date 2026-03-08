#!/usr/bin/env python
"""
详细对比本地和服务器文件的具体差异
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import difflib

try:
    import paramiko
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
    import paramiko

BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend-python"

SERVER_CONFIG = {
    "host": "8.153.93.123",
    "port": 22,
    "username": "root",
    "password": "Lily421020",
    "project_dir": "/opt/sstcp"
}

def get_file_diff(local_path, server_content, filename):
    """生成文件差异对比"""
    if not local_path.exists():
        return f"本地文件不存在: {local_path}"
    
    local_content = local_path.read_text(encoding='utf-8')
    local_lines = local_content.splitlines(keepends=True)
    server_lines = server_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        server_lines,
        local_lines,
        fromfile=f"服务器/{filename}",
        tofile=f"本地/{filename}",
        lineterm=""
    )
    
    return ''.join(diff)

def main():
    print("=" * 70)
    print("详细对比本地和服务器文件差异")
    print("=" * 70)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            SERVER_CONFIG["host"],
            port=SERVER_CONFIG["port"],
            username=SERVER_CONFIG["username"],
            password=SERVER_CONFIG["password"],
            timeout=10
        )
        print(f"✓ 已连接服务器: {SERVER_CONFIG['host']}\n")
        
        files_to_compare = [
            ("backend-python/app/config.py", BACKEND_DIR / "app" / "config.py"),
            ("backend-python/app/main.py", BACKEND_DIR / "app" / "main.py"),
            ("backend-python/.env", BACKEND_DIR / ".env"),
        ]
        
        all_diffs = {}
        
        for server_rel, local_path in files_to_compare:
            print(f"\n{'='*70}")
            print(f"对比文件: {server_rel}")
            print(f"{'='*70}")
            
            server_path = f"{SERVER_CONFIG['project_dir']}/{server_rel}"
            stdin, stdout, stderr = ssh.exec_command(f"cat {server_path} 2>/dev/null", timeout=30)
            server_content = stdout.read().decode('utf-8')
            
            if not local_path.exists():
                print(f"⚠️ 本地文件不存在")
                continue
            
            local_content = local_path.read_text(encoding='utf-8')
            
            local_lines = len(local_content.split('\n'))
            server_lines = len(server_content.split('\n'))
            
            print(f"本地: {local_lines} 行")
            print(f"服务器: {server_lines} 行")
            
            if local_content == server_content:
                print("✓ 文件内容一致")
                continue
            
            print("⚠️ 文件内容有差异\n")
            
            diff = get_file_diff(local_path, server_content, server_rel)
            all_diffs[server_rel] = diff
            
            diff_lines = diff.split('\n')
            if len(diff_lines) > 100:
                print("差异内容（前50行）:")
                print(''.join(diff_lines[:50]))
                print(f"\n... 还有 {len(diff_lines) - 50} 行差异 ...")
            else:
                print("差异内容:")
                print(diff)
        
        ssh.close()
        
        report_path = BASE_DIR / "scripts" / "check" / f"file_content_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("文件内容差异报告\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n\n")
            
            for filename, diff in all_diffs.items():
                f.write(f"\n{'='*70}\n")
                f.write(f"文件: {filename}\n")
                f.write(f"{'='*70}\n")
                f.write(diff)
                f.write("\n")
        
        print(f"\n\n{'='*70}")
        print("差异报告已保存")
        print(f"{'='*70}")
        print(f"路径: {report_path}")
        
        if all_diffs:
            print(f"\n⚠️ 发现 {len(all_diffs)} 个文件存在差异")
            print("\n建议操作:")
            print("1. 检查本地文件是否为最新版本")
            print("2. 如果本地是最新版本，执行部署同步到服务器:")
            print("   - 方式1: 手动复制文件到服务器")
            print("   - 方式2: 运行部署脚本重新部署")
        else:
            print("\n✓ 所有文件内容一致")
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
