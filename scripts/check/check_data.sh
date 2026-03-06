#!/bin/bash
echo "=== 检查工单 #153 状态 ==="
sudo -u postgres psql -d sstcp_maintenance -c "SELECT id, work_id, status, plan_end_date FROM spot_work WHERE id = 153;"
echo ""
echo "=== 检查已审批工单的日期 ==="
sudo -u postgres psql -d sstcp_maintenance -c "SELECT id, inspection_id, status, plan_end_date FROM periodic_inspection WHERE status = '已审批';"
sudo -u postgres psql -d sstcp_maintenance -c "SELECT id, repair_id, status, plan_end_date FROM temporary_repair WHERE status = '已审批';"
sudo -u postgres psql -d sstcp_maintenance -c "SELECT id, work_id, status, plan_end_date FROM spot_work WHERE status = '已审批';"
