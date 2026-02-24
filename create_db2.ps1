$server = "root@8.153.93.123"

Write-Host "Creating database and user..." -ForegroundColor Yellow
ssh $server "su - postgres -c psql -c 'CREATE USER postgres WITH PASSWORD 123456;'"
ssh $server "su - postgres -c psql -c 'CREATE DATABASE tq OWNER postgres;'"

Write-Host "`nDone!" -ForegroundColor Green
