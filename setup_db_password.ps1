$server = "root@8.153.93.123"

Write-Host "Setting PostgreSQL password..." -ForegroundColor Yellow
ssh $server "chmod +x /tmp/set_password.sh && bash /tmp/set_password.sh"

Write-Host "`nRestarting PostgreSQL..." -ForegroundColor Yellow
ssh $server "systemctl restart postgresql"

Write-Host "`nInitializing database..." -ForegroundColor Yellow
ssh $server "cd /var/www/sstcp/backend-python && source venv/bin/activate && alembic upgrade head"

Write-Host "`nRestarting backend service..." -ForegroundColor Yellow
ssh $server "systemctl restart sstcp-backend"

Write-Host "`nDone!" -ForegroundColor Green
