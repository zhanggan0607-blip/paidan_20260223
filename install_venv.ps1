$server = "root@8.153.93.123"

Write-Host "Installing python3-venv..." -ForegroundColor Yellow
ssh $server "apt install -y python3.12-venv"

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
ssh $server "cd /var/www/sstcp/backend-python && python3 -m venv venv"

Write-Host "Done!" -ForegroundColor Green
