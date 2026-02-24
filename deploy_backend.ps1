$server = "root@8.153.93.123"
$localBackend = "D:\共享文件\SSTCP-paidan260120\backend-python"
$remoteBackend = "/var/www/sstcp/backend-python"

Write-Host "Creating backend directory..." -ForegroundColor Yellow
ssh $server "mkdir -p $remoteBackend"

Write-Host "Uploading backend files..." -ForegroundColor Yellow
scp -r "$localBackend\*" "$server`:$remoteBackend/"

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
ssh $server "cd $remoteBackend && python3 -m venv venv"

Write-Host "Installing dependencies..." -ForegroundColor Yellow
ssh $server "cd $remoteBackend && source venv/bin/activate && pip install -r requirements.txt"

Write-Host "Creating systemd service..." -ForegroundColor Yellow
$serviceContent = @"
[Unit]
Description=SSTCP Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$remoteBackend
Environment="PATH=$remoteBackend/venv/bin"
ExecStart=$remoteBackend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
"@

ssh $server "echo '$serviceContent' > /etc/systemd/system/sstcp-backend.service"

Write-Host "Starting backend service..." -ForegroundColor Yellow
ssh $server "systemctl daemon-reload"
ssh $server "systemctl start sstcp-backend"
ssh $server "systemctl enable sstcp-backend"

Write-Host "Checking service status..." -ForegroundColor Yellow
ssh $server "systemctl status sstcp-backend --no-pager"

Write-Host "Done!" -ForegroundColor Green
