$server = "root@8.153.93.123"

Write-Host "Checking PostgreSQL status..." -ForegroundColor Yellow
$pgStatus = ssh $server "systemctl status postgresql --no-pager"
Write-Host $pgStatus

Write-Host "`nStarting PostgreSQL..." -ForegroundColor Yellow
ssh $server "systemctl start postgresql"

Write-Host "`nChecking PostgreSQL status again..." -ForegroundColor Yellow
$pgStatus2 = ssh $server "systemctl status postgresql --no-pager"
Write-Host $pgStatus2

Write-Host "`nCreating database..." -ForegroundColor Yellow
ssh $server "su - postgres -c 'psql -c \"CREATE DATABASE tq;\"' 2>&1 || echo 'Database may already exist'"

Write-Host "`nDone!" -ForegroundColor Green
