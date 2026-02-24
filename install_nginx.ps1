$server = "root@8.153.93.123"

Write-Host "Updating apt packages..." -ForegroundColor Yellow
ssh $server "apt update"

Write-Host "Installing nginx..." -ForegroundColor Yellow
ssh $server "apt install -y nginx"

Write-Host "Creating nginx directories..." -ForegroundColor Yellow
ssh $server "mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled"

Write-Host "Uploading nginx config..." -ForegroundColor Yellow
scp "D:\共享文件\SSTCP-paidan260120\sstcp_nginx.conf" $server":/etc/nginx/sites-available/sstcp"

Write-Host "Creating symlink..." -ForegroundColor Yellow
ssh $server "ln -sf /etc/nginx/sites-available/sstcp /etc/nginx/sites-enabled/sstcp"

Write-Host "Removing default nginx config..." -ForegroundColor Yellow
ssh $server "rm -f /etc/nginx/sites-enabled/default"

Write-Host "Testing nginx config..." -ForegroundColor Yellow
ssh $server "nginx -t"

Write-Host "Starting nginx..." -ForegroundColor Yellow
ssh $server "systemctl start nginx"

Write-Host "Enabling nginx..." -ForegroundColor Yellow
ssh $server "systemctl enable nginx"

Write-Host "Done!" -ForegroundColor Green
