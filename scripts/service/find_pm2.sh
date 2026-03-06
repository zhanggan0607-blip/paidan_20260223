#!/bin/bash
echo "=== 查找 Node.js 和 PM2 ==="
which node
which pm2
ls -la /root/.nvm/versions/node/
ls -la ~/.npm-global/bin/ 2>/dev/null || echo "no npm-global"
find /root -name "pm2" 2>/dev/null | head -5
