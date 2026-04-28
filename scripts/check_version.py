import paramiko
import sys

SERVER_IP = '8.153.95.31'
SERVER_PASSWORD = os.environ.get('SERVER_PASSWORD', '')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_IP, username='root', password=SERVER_PASSWORD, timeout=15)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8')

print('=== PC端版本号检查 ===')
pc_js = run_cmd('docker exec sstcp-frontend-pc sh -c "cat /usr/share/nginx/html/assets/js/index-CCPmbE8q.js"')
idx = pc_js.find('appVersion')
if idx >= 0:
    context = pc_js[max(0,idx-300):idx+50]
    print(f'找到appVersion上下文: ...{context}...')
else:
    print('未找到appVersion')

idx2 = pc_js.find('"2.0.7"')
idx3 = pc_js.find('"2.0.3"')
print(f'"2.0.7" 出现位置: {idx2}')
print(f'"2.0.3" 出现位置: {idx3}')

if idx3 >= 0:
    context3 = pc_js[max(0,idx3-100):idx3+50]
    print(f'2.0.3上下文: ...{context3}...')

print('\n=== H5端版本号检查 ===')
h5_files = run_cmd('docker exec sstcp-frontend-h5 sh -c "ls /usr/share/nginx/html/assets/js/ | grep index | grep -v .gz$"').strip()
print(f'H5 index文件: {h5_files}')

if h5_files:
    h5_js = run_cmd(f'docker exec sstcp-frontend-h5 sh -c "cat /usr/share/nginx/html/assets/js/{h5_files}"')
    idx_h5 = h5_js.find('appVersion')
    if idx_h5 >= 0:
        context_h5 = h5_js[max(0,idx_h5-300):idx_h5+50]
        print(f'找到appVersion上下文: ...{context_h5}...')
    idx_h5_207 = h5_js.find('"2.0.7"')
    idx_h5_203 = h5_js.find('"2.0.3"')
    print(f'"2.0.7" 出现位置: {idx_h5_207}')
    print(f'"2.0.3" 出现位置: {idx_h5_203}')

ssh.close()
