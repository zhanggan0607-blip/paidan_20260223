#!/bin/bash
echo "=== 验证H5部署 ==="
echo "检查dist目录文件数量:"
ls -la /var/www/sstcp/H5/dist/ | wc -l
echo ""
echo "检查index.html:"
head -5 /var/www/sstcp/H5/dist/index.html
echo ""
echo "测试H5访问:"
curl -s -o /dev/null -w "%{http_code}" http://localhost/h5/
