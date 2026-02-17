import subprocess
import sys

hosts_content = """
# SSTCP系统优化 - 确保localhost优先解析到IPv4
127.0.0.1    localhost
"""

try:
    result = subprocess.run(
        ['powershell', '-Command', f'''
        $content = @'
{hosts_content}
'@
        Add-Content -Path "$env:SystemRoot\\System32\\drivers\\etc\\hosts" -Value $content -Force
        Write-Host "hosts文件已修改"
        '''],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")
except Exception as e:
    print(f"执行失败: {e}")
    print("请手动以管理员身份运行以下命令:")
    print('echo "127.0.0.1    localhost" >> C:\\Windows\\System32\\drivers\\etc\\hosts')
