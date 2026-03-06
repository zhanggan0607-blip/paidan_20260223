$server = "root@8.153.93.123"

Write-Host "Creating database and user..." -ForegroundColor Yellow
ssh $server "chmod +x /tmp/create_db.sh && bash /tmp/create_db.sh"

Write-Host "`nDone!" -ForegroundColor Green
