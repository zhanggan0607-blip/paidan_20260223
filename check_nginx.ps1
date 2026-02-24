$server = "root@8.153.93.123"

Write-Host "Checking Nginx status..." -ForegroundColor Yellow
$nginxStatus = ssh $server "systemctl status nginx"
Write-Host $nginxStatus

Write-Host "`nChecking Nginx config..." -ForegroundColor Yellow
$nginxConfig = ssh $server "cat /etc/nginx/sites-enabled/sstcp"
Write-Host $nginxConfig

Write-Host "`nChecking if H5 files exist..." -ForegroundColor Yellow
$h5Files = ssh $server "ls -la /var/www/sstcp/H5/dist/"
Write-Host $h5Files
