$localPath = "D:\共享文件\SSTCP-paidan260120\H5\dist"
$remotePath = "/var/www/sstcp/H5/dist"
$server = "root@8.153.93.123"

Write-Host "Starting upload..." -ForegroundColor Green

Set-Location $localPath
scp -r . $server`:$remotePath/

Write-Host "Upload complete!" -ForegroundColor Green
Write-Host "Visit: http://8.153.93.123/h5/" -ForegroundColor Cyan
