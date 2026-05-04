$TaskName = "SSTCP-Docker-Deploy"
$ScriptPath = "D:\SSTCP_XIANGMU\paidan\scripts\deploy-docker-all.ps1"
$TriggerTime = "22:00"

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task: $TaskName"
}

$today = Get-Date
$scheduleDate = Get-Date -Year $today.Year -Month $today.Month -Day $today.Day -Hour 22 -Minute 0 -Second 0

if ($scheduleDate -le $today) {
    Write-Host "ERROR: 22:00 has already passed today! Please set a future time." -ForegroundColor Red
    exit 1
}

$trigger = New-ScheduledTaskTrigger -Once -At $scheduleDate
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Trigger $trigger -Action $action -Settings $settings -Principal $principal -Description "SSTCP Docker Build & Deploy - Scheduled for $scheduleDate" | Out-Null

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Scheduled Task Created Successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Task Name:    $TaskName" -ForegroundColor Yellow
Write-Host "  Script:       $ScriptPath" -ForegroundColor Yellow
Write-Host "  Scheduled At: $scheduleDate" -ForegroundColor Yellow
Write-Host "  Time Limit:   3 hours" -ForegroundColor Yellow
Write-Host ""
Write-Host "  The task will:" -ForegroundColor White
Write-Host "    1. Build all Docker images (backend + PC + H5)" -ForegroundColor White
Write-Host "    2. Save images as tar and transfer to server" -ForegroundColor White
Write-Host "    3. Deploy on server (8.153.95.31)" -ForegroundColor White
Write-Host "    4. Run health checks" -ForegroundColor White
Write-Host "    5. Auto-fix issues if found" -ForegroundColor White
Write-Host "    6. Rollback if auto-fix fails" -ForegroundColor White
Write-Host ""
Write-Host "  To check task status:" -ForegroundColor White
Write-Host "    Get-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Gray
Write-Host ""
Write-Host "  To run manually now:" -ForegroundColor White
Write-Host "    powershell -File `"$ScriptPath`"" -ForegroundColor Gray
Write-Host ""
Write-Host "  To cancel the scheduled task:" -ForegroundColor White
Write-Host "    Unregister-ScheduledTask -TaskName `"$TaskName`" -Confirm:`$false" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
