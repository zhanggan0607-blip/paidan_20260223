$server = "root@8.153.93.123"

Write-Host "Checking if backend service is running..." -ForegroundColor Yellow
$serviceStatus = ssh $server "systemctl status sstcp-backend"
Write-Host $serviceStatus

Write-Host "`nChecking what's listening on port 8080..." -ForegroundColor Yellow
$portStatus = ssh $server "netstat -tlnp | grep 8080"
Write-Host $portStatus

Write-Host "`nChecking backend directory..." -ForegroundColor Yellow
$backendDir = ssh $server "ls -la /var/www/sstcp/backend-python/"
Write-Host $backendDir
