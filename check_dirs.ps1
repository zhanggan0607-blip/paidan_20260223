$server = "root@8.153.93.123"

Write-Host "Checking /var/www/sstcp directory..." -ForegroundColor Yellow
$sstcpDir = ssh $server "ls -la /var/www/sstcp/"
Write-Host $sstcpDir

Write-Host "`nChecking home directory..." -ForegroundColor Yellow
$homeDir = ssh $server "ls -la ~"
Write-Host $homeDir
