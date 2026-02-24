#!/bin/bash
sudo -u postgres psql -d sstcp_maintenance -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO sstcp_user;"
sudo -u postgres psql -d sstcp_maintenance -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO sstcp_user;"
echo "授权完成"
echo "验证表结构:"
sudo -u postgres psql -d sstcp_maintenance -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name LIMIT 30;"
echo "验证用户数据:"
sudo -u postgres psql -d sstcp_maintenance -c "SELECT id, username, role FROM users LIMIT 5;"
