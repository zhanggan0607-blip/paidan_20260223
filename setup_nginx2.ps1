$server = "root@8.153.93.123"

Write-Host "Moving nginx config..." -ForegroundColor Yellow
ssh $server "mv /tmp/sstcp_nginx.conf /etc/nginx/sites-available/sstcp"

Write-Host "Creating symlink..." -ForegroundColor Yellow
ssh $server "ln -sf /etc/nginx/sites-available/sstcp /etc/nginx/sites-enabled/sstcp"

Write-Host "Removing default nginx config..." -ForegroundColor Yellow
ssh $server "rm -f /etc/nginx/sites-enabled/default"

Write-Host "Testing nginx config..." -ForegroundColor Yellow
ssh $server "nginx -t"

Write-Host "Starting nginx..." -ForegroundColor Yellow
ssh $server "systemctl start nginx"

Write-Host "Done!" -ForegroundColor Green
