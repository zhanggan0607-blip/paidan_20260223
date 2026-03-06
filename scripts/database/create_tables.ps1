$server = "root@8.153.93.123"
$backendDir = "/var/www/sstcp/backend-python"

Write-Host "Creating database tables..." -ForegroundColor Yellow
ssh $server "cd $backendDir && source venv/bin/activate && python -c \"from app.database import engine; from app.models import Base; Base.metadata.create_all(engine)\""

Write-Host "`nRestarting backend service..." -ForegroundColor Yellow
ssh $server "systemctl restart sstcp-backend"

Write-Host "`nChecking service status..." -ForegroundColor Yellow
ssh $server "systemctl status sstcp-backend --no-pager"

Write-Host "`nDone!" -ForegroundColor Green
