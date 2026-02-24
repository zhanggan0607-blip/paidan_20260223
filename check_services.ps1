$server = "root@8.153.93.123"

Write-Host "Checking Nginx status..." -ForegroundColor Yellow
ssh $server "systemctl status nginx --no-pager"

Write-Host "`nChecking Backend status..." -ForegroundColor Yellow
ssh $server "systemctl status sstcp-backend --no-pager"

Write-Host "`nChecking PostgreSQL status..." -ForegroundColor Yellow
ssh $server "systemctl status postgresql --no-pager"

Write-Host "`nChecking ports..." -ForegroundColor Yellow
ssh $server "netstat -tlnp | grep -E '80|8080|5432'"

Write-Host "Done!" -ForegroundColor Green
