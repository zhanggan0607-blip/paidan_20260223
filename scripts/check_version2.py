import paramiko
import os
import re

SERVER_IP = os.environ.get('SERVER_IP', '')
SERVER_PASSWORD = os.environ.get('SERVER_PASSWORD', '')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
known_hosts = os.path.expanduser('~/.ssh/known_hosts')
if os.path.exists(known_hosts):
    ssh.load_host_keys(known_hosts)
ssh.connect(SERVER_IP, username='root', password=SERVER_PASSWORD, timeout=15)

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8')

print('=== PC端: 搜索Layout组件定义 ===')
pc_js = run_cmd('docker exec sstcp-frontend-pc sh -c "cat /usr/share/nginx/html/assets/js/index-CCPmbE8q.js"')

search_terms = ['name:"Layout"', '2.0.7', '2.0.3', '__APP_VERSION__']
for term in search_terms:
    idx = pc_js.find(term)
    if idx >= 0:
        context = pc_js[max(0,idx-100):idx+100]
        print(f'  "{term}" found at {idx}: ...{context}...')
    else:
        print(f'  "{term}" NOT found')

print('\n=== 搜索版本号字符串 ===')
version_matches = list(re.finditer(r'"(\d+\.\d+\.\d+)"', pc_js))
for m in version_matches:
    start = max(0, m.start()-50)
    end = min(len(pc_js), m.end()+50)
    print(f'  版本号 "{m.group(1)}" at {m.start()}: ...{pc_js[start:end]}...')

print('\n=== H5端: 搜索版本号字符串 ===')
h5_js = run_cmd('docker exec sstcp-frontend-h5 sh -c "cat /usr/share/nginx/html/assets/js/index-BnR2rLu3.js"')

version_matches_h5 = list(re.finditer(r'"(\d+\.\d+\.\d+)"', h5_js))
for m in version_matches_h5:
    start = max(0, m.start()-50)
    end = min(len(h5_js), m.end()+50)
    print(f'  版本号 "{m.group(1)}" at {m.start()}: ...{h5_js[start:end]}...')

ssh.close()
