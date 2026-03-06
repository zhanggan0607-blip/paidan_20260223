$server = "root@8.153.93.123"
$backendDir = "/var/www/sstcp/backend-python"

Write-Host "Installing dependencies..." -ForegroundColor Yellow
ssh $server "cd $backendDir && source venv/bin/activate && pip install -r requirements.txt"

Write-Host "Starting backend service..." -ForegroundColor Yellow
ssh $server "systemctl start sstcp-backend"

Write-Host "Checking service status..." -ForegroundColor Yellow
ssh $server "systemctl status sstcp-backend --no-pager"

Write-Host "Done!" -ForegroundColor Green
