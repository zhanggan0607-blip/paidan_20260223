#!/bin/bash
echo "=== 检查工单状态 ==="
sudo -u postgres psql -d sstcp_maintenance -c "SELECT status, COUNT(*) FROM periodic_inspection GROUP BY status;"
echo ""
sudo -u postgres psql -d sstcp_maintenance -c "SELECT status, COUNT(*) FROM temporary_repair GROUP BY status;"
echo ""
sudo -u postgres psql -d sstcp_maintenance -c "SELECT status, COUNT(*) FROM spot_work GROUP BY status;"
