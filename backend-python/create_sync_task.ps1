# Create Windows Scheduled Task - Database Auto Sync
# Run as Administrator

$TaskName = "SSTCP-Database-Sync"
$TaskDescription = "Auto sync server database to local every 5 minutes"
$ScriptPath = "D:\共享文件\SSTCP-paidan260120\backend-python\sync_task.bat"

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task exists, updating..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create trigger - run every 5 minutes
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)

# Create action
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory "D:\共享文件\SSTCP-paidan260120\backend-python"

# Create settings
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register task
Register-ScheduledTask -TaskName $TaskName -Description $TaskDescription -Trigger $Trigger -Action $Action -Settings $Settings -RunLevel Highest

Write-Host ""
Write-Host "============================================"
Write-Host "Task created successfully!"
Write-Host "Task Name: $TaskName"
Write-Host "Interval: Every 5 minutes"
Write-Host "Script Path: $ScriptPath"
Write-Host "============================================"
