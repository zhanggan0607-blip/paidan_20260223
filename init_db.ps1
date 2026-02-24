$server = "root@8.153.93.123"
$backendDir = "/var/www/sstcp/backend-python"

Write-Host "Initializing database..." -ForegroundColor Yellow
ssh $server "cd $backendDir && source venv/bin/activate && alembic upgrade head"

Write-Host "`nRestarting backend service..." -ForegroundColor Yellow
ssh $server "systemctl restart sstcp-backend"

Write-Host "`nChecking service status..." -ForegroundColor Yellow
ssh $server "systemctl status sstcp-backend --no-pager"

Write-Host "`nDone!" -ForegroundColor Green
