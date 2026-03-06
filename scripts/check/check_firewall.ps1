$server = "root@8.153.93.123"

Write-Host "Checking firewall status..." -ForegroundColor Yellow
ssh $server "ufw status"

Write-Host "`nChecking if port 80 is open..." -ForegroundColor Yellow
ssh $server "netstat -tlnp | grep :80"

Write-Host "`nChecking nginx status..." -ForegroundColor Yellow
ssh $server "systemctl status nginx --no-pager"

Write-Host "Done!" -ForegroundColor Green
