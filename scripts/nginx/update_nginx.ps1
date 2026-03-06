$server = "root@8.153.93.123"

Write-Host "Updating nginx config..." -ForegroundColor Yellow
ssh $server "mv /tmp/sstcp_nginx.conf /etc/nginx/sites-available/sstcp"

Write-Host "Testing nginx config..." -ForegroundColor Yellow
ssh $server "nginx -t"

Write-Host "Reloading nginx..." -ForegroundColor Yellow
ssh $server "systemctl reload nginx"

Write-Host "Done!" -ForegroundColor Green
