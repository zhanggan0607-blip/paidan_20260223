$server = "root@8.153.93.123"

Write-Host "Installing PostgreSQL..." -ForegroundColor Yellow
ssh $server "apt install -y postgresql postgresql-contrib"

Write-Host "`nStarting PostgreSQL..." -ForegroundColor Yellow
ssh $server "systemctl start postgresql"
ssh $server "systemctl enable postgresql"

Write-Host "`nChecking PostgreSQL status..." -ForegroundColor Yellow
$pgStatus = ssh $server "systemctl status postgresql --no-pager"
Write-Host $pgStatus

Write-Host "`nCreating database and user..." -ForegroundColor Yellow
ssh $server "su - postgres -c \"psql -c \\\"CREATE USER postgres WITH PASSWORD '123456';\\\"\""
ssh $server "su - postgres -c \"psql -c \\\"CREATE DATABASE tq OWNER postgres;\\\"\""

Write-Host "`nDone!" -ForegroundColor Green
