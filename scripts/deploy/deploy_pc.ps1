$server = "root@8.153.93.123"

Write-Host "Creating dist directory..." -ForegroundColor Yellow
ssh $server "mkdir -p /var/www/sstcp/dist"

Write-Host "Uploading PC dist files..." -ForegroundColor Yellow
scp -r "D:\共享文件\SSTCP-paidan260120\dist\*" $server`:/var/www/sstcp/dist/

Write-Host "Uploading nginx config..." -ForegroundColor Yellow
scp "D:\共享文件\SSTCP-paidan260120\sstcp_nginx.conf" $server`:/tmp/sstcp_nginx.conf

Write-Host "Updating nginx config..." -ForegroundColor Yellow
ssh $server "mv /tmp/sstcp_nginx.conf /etc/nginx/sites-available/sstcp"

Write-Host "Testing nginx config..." -ForegroundColor Yellow
ssh $server "nginx -t"

Write-Host "Reloading nginx..." -ForegroundColor Yellow
ssh $server "systemctl reload nginx"

Write-Host "Done!" -ForegroundColor Green
