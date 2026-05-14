$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PROJECT_ROOT = "D:\SSTCP_XIANGMU\paidan"
$SERVER_IP = "${env:DEPLOY_SERVER_IP}"
if (-not $SERVER_IP) { throw "请设置环境变量 DEPLOY_SERVER_IP (服务器IP地址)" }
$SERVER_USER = if ($env:DEPLOY_SERVER_USER) { $env:DEPLOY_SERVER_USER } else { "root" }
$DEPLOY_PATH = "/opt/sstcp"
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
$VERSION = "v2.2.0"
$LOG_FILE = "$PROJECT_ROOT\deploy-log-$TIMESTAMP.txt"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$time] [$Level] $Message"
    Write-Host $line
    Add-Content -Path $LOG_FILE -Value $line -Encoding UTF8
}

function Test-DockerRunning {
    try {
        $null = docker info 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Docker not running" }
        Write-Log "Docker is running"
        return $true
    } catch {
        Write-Log "Docker is NOT running! Please start Docker Desktop." "ERROR"
        return $false
    }
}

function Test-SSHAvailable {
    try {
        $result = ssh -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" "echo ok" 2>&1
        if ($result -match "ok") {
            Write-Log "SSH connection to $SERVER_IP verified"
            return $true
        } else {
            Write-Log "SSH connection failed. Please ensure SSH key is configured or password is available." "WARN"
            Write-Log "You may need to run: ssh $SERVER_USER@$SERVER_IP first to accept the host key" "WARN"
            return $false
        }
    } catch {
        Write-Log "SSH test error: $_" "WARN"
        return $false
    }
}

function Invoke-SSHCommand {
    param([string]$Command)
    $fullCmd = "ssh $SERVER_USER@$SERVER_IP `"$Command`""
    Write-Log "SSH> $Command"
    $result = @()
    $tempFile = [System.IO.Path]::GetTempFileName()
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "cmd.exe"
        $psi.Arguments = "/c $fullCmd"
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.CreateNoWindow = $true
        $process = [System.Diagnostics.Process]::Start($psi)
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        if ($stdout) {
            foreach ($line in $stdout -split "`n") {
                $trimmed = $line.Trim()
                if ($trimmed) {
                    $result += $trimmed
                    Write-Log "  $trimmed"
                }
            }
        }
        if ($stderr) {
            foreach ($line in $stderr -split "`n") {
                $trimmed = $line.Trim()
                if ($trimmed) {
                    $result += $trimmed
                    Write-Log "  $trimmed"
                }
            }
        }
    } catch {
        Write-Log "  SSH command error: $_" "WARN"
    }
    return $result
}

function Build-BackendImage {
    Write-Log "========== Building Backend Image =========="
    Push-Location "$PROJECT_ROOT\backend-python"
    try {
        docker build --no-cache -t "sstcp-backend:$VERSION" -t "sstcp-backend:latest" -f Dockerfile .
        if ($LASTEXITCODE -ne 0) { throw "Backend build failed" }
        Write-Log "Backend image built successfully: sstcp-backend:$VERSION"
    } finally {
        Pop-Location
    }
}

function Build-PCFrontendImage {
    Write-Log "========== Building PC Frontend Image =========="
    Push-Location $PROJECT_ROOT
    try {
        docker build --no-cache -t "sstcp-frontend-pc:$VERSION" -t "sstcp-frontend-pc:latest" -f Dockerfile .
        if ($LASTEXITCODE -ne 0) { throw "PC Frontend build failed" }
        Write-Log "PC Frontend image built successfully: sstcp-frontend-pc:$VERSION"
    } finally {
        Pop-Location
    }
}

function Build-H5FrontendImage {
    Write-Log "========== Building H5 Frontend Image =========="
    Push-Location $PROJECT_ROOT
    try {
        docker build --no-cache -t "sstcp-frontend-h5:$VERSION" -t "sstcp-frontend-h5:latest" -f H5\Dockerfile .
        if ($LASTEXITCODE -ne 0) { throw "H5 Frontend build failed" }
        Write-Log "H5 Frontend image built successfully: sstcp-frontend-h5:$VERSION"
    } finally {
        Pop-Location
    }
}

function Save-ImagesToTar {
    Write-Log "========== Saving Docker Images to Tar Files =========="
    $tarDir = "$PROJECT_ROOT\deploy-tars"
    if (-not (Test-Path $tarDir)) { New-Item -ItemType Directory -Path $tarDir | Out-Null }

    Write-Log "Saving backend image..."
    docker save -o "$tarDir\sstcp-backend.tar" "sstcp-backend:$VERSION"
    if ($LASTEXITCODE -ne 0) { throw "Failed to save backend image" }

    Write-Log "Saving PC frontend image..."
    docker save -o "$tarDir\sstcp-frontend-pc.tar" "sstcp-frontend-pc:$VERSION"
    if ($LASTEXITCODE -ne 0) { throw "Failed to save PC frontend image" }

    Write-Log "Saving H5 frontend image..."
    docker save -o "$tarDir\sstcp-frontend-h5.tar" "sstcp-frontend-h5:$VERSION"
    if ($LASTEXITCODE -ne 0) { throw "Failed to save H5 frontend image" }

    $totalSize = (Get-ChildItem $tarDir -Filter "*.tar" | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Log "All images saved. Total size: $([math]::Round($totalSize, 2)) MB"
}

function Send-DeployPackage {
    Write-Log "========== Transferring Files to Server =========="

    Write-Log "Creating deploy directory on server..."
    Invoke-SSHCommand "mkdir -p $DEPLOY_PATH/deploy-staging"

    Write-Log "Transferring backend image tar..."
    scp "$PROJECT_ROOT\deploy-tars\sstcp-backend.tar" "${SERVER_USER}@${SERVER_IP}:${DEPLOY_PATH}/deploy-staging/"
    if ($LASTEXITCODE -ne 0) { throw "Failed to transfer backend image" }

    Write-Log "Transferring PC frontend image tar..."
    scp "$PROJECT_ROOT\deploy-tars\sstcp-frontend-pc.tar" "${SERVER_USER}@${SERVER_IP}:${DEPLOY_PATH}/deploy-staging/"
    if ($LASTEXITCODE -ne 0) { throw "Failed to transfer PC frontend image" }

    Write-Log "Transferring H5 frontend image tar..."
    scp "$PROJECT_ROOT\deploy-tars\sstcp-frontend-h5.tar" "${SERVER_USER}@${SERVER_IP}:${DEPLOY_PATH}/deploy-staging/"
    if ($LASTEXITCODE -ne 0) { throw "Failed to transfer H5 frontend image" }

    Write-Log "Transferring nginx config..."
    scp "$PROJECT_ROOT\docker\nginx.conf" "${SERVER_USER}@${SERVER_IP}:${DEPLOY_PATH}/nginx.conf"
    if ($LASTEXITCODE -ne 0) { throw "Failed to transfer nginx.conf" }

    Write-Log "Transferring docker-compose file..."
    scp "$PROJECT_ROOT\docker\docker-compose-server.yml" "${SERVER_USER}@${SERVER_IP}:${DEPLOY_PATH}/docker-compose.yml"
    if ($LASTEXITCODE -ne 0) { throw "Failed to transfer docker-compose.yml" }

    Write-Log "All files transferred successfully"
}

function Deploy-OnServer {
    Write-Log "========== Deploying on Server =========="

    Write-Log "Loading Docker images on server..."
    Invoke-SSHCommand "docker load -i $DEPLOY_PATH/deploy-staging/sstcp-backend.tar"
    Invoke-SSHCommand "docker load -i $DEPLOY_PATH/deploy-staging/sstcp-frontend-pc.tar"
    Invoke-SSHCommand "docker load -i $DEPLOY_PATH/deploy-staging/sstcp-frontend-h5.tar"

    Write-Log "Updating docker-compose.yml with new version..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && sed -i 's/sstcp-backend:v[0-9.]*/sstcp-backend:$VERSION/g' docker-compose.yml"
    Invoke-SSHCommand "cd $DEPLOY_PATH && sed -i 's/sstcp-frontend-pc:v[0-9.]*/sstcp-frontend-pc:$VERSION/g' docker-compose.yml"
    Invoke-SSHCommand "cd $DEPLOY_PATH && sed -i 's/sstcp-frontend-h5:v[0-9.]*/sstcp-frontend-h5:$VERSION/g' docker-compose.yml"

    Write-Log "Ensuring DATABASE_URL points to Alibaba Cloud RDS..."
    $dbUrl = "${env:DATABASE_URL}"
    if (-not $dbUrl) {
        Write-Log "ERROR: DATABASE_URL environment variable is not set. Please set it before deploying."
        exit 1
    }
    Invoke-SSHCommand "cd $DEPLOY_PATH && sed -i 's|DATABASE_URL=.*|DATABASE_URL=$dbUrl|g' docker-compose.yml"

    Write-Log "Backing up current docker-compose.yml..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && cp docker-compose.yml docker-compose.yml.bak.$TIMESTAMP"

    Write-Log "Stopping old containers..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose down --remove-orphans"

    Write-Log "Running database migrations on RDS..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose run --rm -e DATABASE_URL='$dbUrl' backend alembic upgrade head"

    Write-Log "Starting new containers..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose up -d"

    Write-Log "Cleaning up staging files..."
    Invoke-SSHCommand "rm -rf $DEPLOY_PATH/deploy-staging"

    Write-Log "Cleaning up old Docker resources..."
    Invoke-SSHCommand "docker system prune -f"

    Write-Log "Removing old version images..."
    Invoke-SSHCommand "docker images | grep sstcp | grep -v '${VERSION}' | awk '{print `$3}' | xargs -r docker rmi -f 2>/dev/null || true"

    Write-Log "Server deployment commands executed"
}

function Wait-ForServices {
    Write-Log "========== Waiting for Services to Start =========="
    $maxWait = 120
    $waited = 0
    $interval = 10

    while ($waited -lt $maxWait) {
        Write-Log "Waiting for services... ($waited/$maxWait seconds)"
        Start-Sleep -Seconds $interval
        $waited += $interval

        $healthResult = Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose ps --format json" 2>&1
        $allHealthy = $true

        $services = @("sstcp-backend", "sstcp-frontend-pc", "sstcp-frontend-h5", "sstcp-nginx")
        foreach ($svc in $services) {
            $status = Invoke-SSHCommand "docker inspect --format='{{.State.Health.Status}}' $svc 2>/dev/null || echo 'not_found'"
            $statusStr = $status | Out-String
            if ($statusStr -notmatch "healthy") {
                Write-Log "  $svc status: $statusStr (not healthy yet)"
                $allHealthy = $false
            } else {
                Write-Log "  $svc status: healthy"
            }
        }

        if ($allHealthy) {
            Write-Log "All services are healthy!"
            return $true
        }
    }

    Write-Log "Timed out waiting for services to become healthy" "WARN"
    return $false
}

function Test-Deployment {
    Write-Log "========== Verifying Deployment =========="
    $issues = @()

    Write-Log "Checking backend health endpoint..."
    $healthCheck = Invoke-SSHCommand "curl -sf http://localhost:8000/api/v1/health 2>&1 || echo 'HEALTH_CHECK_FAILED'"
    $healthStr = $healthCheck | Out-String
    if ($healthStr -match "HEALTH_CHECK_FAILED" -or ($healthStr -notmatch "healthy" -and $healthStr -notmatch "200")) {
        Write-Log "Backend health check FAILED" "ERROR"
        $issues += "backend_health_failed"
    } else {
        Write-Log "Backend health check PASSED"
    }

    Write-Log "Checking PC frontend..."
    $pcCheck = Invoke-SSHCommand "curl -sf http://localhost:8081/ -o /dev/null -w '%{http_code}' 2>&1 || echo 'PC_CHECK_FAILED'"
    $pcStr = $pcCheck | Out-String
    if ($pcStr -match "PC_CHECK_FAILED" -or $pcStr -notmatch "200") {
        Write-Log "PC frontend check FAILED" "ERROR"
        $issues += "pc_frontend_failed"
    } else {
        Write-Log "PC frontend check PASSED"
    }

    Write-Log "Checking H5 frontend..."
    $h5Check = Invoke-SSHCommand "curl -sf http://localhost:8082/ -o /dev/null -w '%{http_code}' 2>&1 || echo 'H5_CHECK_FAILED'"
    $h5Str = $h5Check | Out-String
    if ($h5Str -match "H5_CHECK_FAILED" -or $h5Str -notmatch "200") {
        Write-Log "H5 frontend check FAILED" "ERROR"
        $issues += "h5_frontend_failed"
    } else {
        Write-Log "H5 frontend check PASSED"
    }

    Write-Log "Checking nginx reverse proxy..."
    $nginxCheck = Invoke-SSHCommand "curl -sf http://localhost/api/v1/health -o /dev/null -w '%{http_code}' -L 2>&1 || echo 'NGINX_CHECK_FAILED'"
    $nginxStr = $nginxCheck | Out-String
    if ($nginxStr -match "NGINX_CHECK_FAILED" -or ($nginxStr -notmatch "200" -and $nginxStr -notmatch "301")) {
        Write-Log "Nginx reverse proxy check FAILED" "ERROR"
        $issues += "nginx_proxy_failed"
    } else {
        Write-Log "Nginx reverse proxy check PASSED"
    }

    Write-Log "Checking database connectivity to Alibaba Cloud RDS..."
    $dbPassword = "${env:DB_PASSWORD}"
    $dbHost = "${env:DB_HOST}"
    if (-not $dbPassword -or -not $dbHost) {
        Write-Log "DB connectivity check skipped (DB_PASSWORD/DB_HOST not set)" "WARN"
    } else {
        $dbCheck = Invoke-SSHCommand "PGPASSWORD='$dbPassword' psql -h $dbHost -U postgres -d tq -c 'SELECT 1;' 2>&1 || echo 'DB_CHECK_FAILED'"
        $dbStr = $dbCheck | Out-String
        if ($dbStr -match "1 row" -or $dbStr -match "DB_OK") {
            Write-Log "Database connectivity check PASSED (RDS tq)"
        } else {
            Write-Log "Database connectivity check FAILED" "ERROR"
            $issues += "db_connection_failed"
        }
    }

    Write-Log "Checking container resource usage..."
    $null = Invoke-SSHCommand "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"

    if ($issues.Count -eq 0) {
        Write-Log "All verification checks PASSED!"
    } else {
        Write-Log "Verification found $($issues.Count) issue(s): $($issues -join ', ')" "ERROR"
    }

    return $issues
}

function Invoke-AutoFix {
    param([string[]]$Issues)

    Write-Log "========== Auto-Fix Starting =========="
    $fixSuccess = $true

    foreach ($issue in $Issues) {
        Write-Log "Attempting to fix: $issue"

        switch ($issue) {
            "backend_health_failed" {
                Write-Log "Fix: Restarting backend container..."
                Invoke-SSHCommand "docker restart sstcp-backend"
                Start-Sleep -Seconds 30

                $recheck = Invoke-SSHCommand "curl -sf http://localhost:8000/api/v1/health 2>&1 || echo 'STILL_FAILED'"
                if ($recheck | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                    Write-Log "Fix: Checking backend logs for errors..."
                    Invoke-SSHCommand "docker logs sstcp-backend --tail 50"
                    Write-Log "Fix: Attempting full container recreation..."
                    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose up -d --force-recreate backend"
                    Start-Sleep -Seconds 40

                    $recheck2 = Invoke-SSHCommand "curl -sf http://localhost:8000/api/v1/health 2>&1 || echo 'STILL_FAILED'"
                    if ($recheck2 | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                        Write-Log "Auto-fix FAILED for backend_health_failed" "ERROR"
                        $fixSuccess = $false
                    } else {
                        Write-Log "Auto-fix SUCCEEDED for backend_health_failed"
                    }
                } else {
                    Write-Log "Auto-fix SUCCEEDED for backend_health_failed (restart helped)"
                }
            }

            "pc_frontend_failed" {
                Write-Log "Fix: Restarting PC frontend container..."
                Invoke-SSHCommand "docker restart sstcp-frontend-pc"
                Start-Sleep -Seconds 15

                $recheck = Invoke-SSHCommand "curl -sf http://localhost:8081/ -o /dev/null -w '%{http_code}' 2>&1 || echo 'STILL_FAILED'"
                if ($recheck | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                    Write-Log "Fix: Recreating PC frontend container..."
                    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose up -d --force-recreate frontend-pc"
                    Start-Sleep -Seconds 15

                    $recheck2 = Invoke-SSHCommand "curl -sf http://localhost:8081/ -o /dev/null -w '%{http_code}' 2>&1 || echo 'STILL_FAILED'"
                    if ($recheck2 | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                        Write-Log "Auto-fix FAILED for pc_frontend_failed" "ERROR"
                        $fixSuccess = $false
                    } else {
                        Write-Log "Auto-fix SUCCEEDED for pc_frontend_failed"
                    }
                } else {
                    Write-Log "Auto-fix SUCCEEDED for pc_frontend_failed"
                }
            }

            "h5_frontend_failed" {
                Write-Log "Fix: Restarting H5 frontend container..."
                Invoke-SSHCommand "docker restart sstcp-frontend-h5"
                Start-Sleep -Seconds 15

                $recheck = Invoke-SSHCommand "curl -sf http://localhost:8082/ -o /dev/null -w '%{http_code}' 2>&1 || echo 'STILL_FAILED'"
                if ($recheck | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                    Write-Log "Fix: Recreating H5 frontend container..."
                    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose up -d --force-recreate frontend-h5"
                    Start-Sleep -Seconds 15

                    $recheck2 = Invoke-SSHCommand "curl -sf http://localhost:8082/ -o /dev/null -w '%{http_code}' 2>&1 || echo 'STILL_FAILED'"
                    if ($recheck2 | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                        Write-Log "Auto-fix FAILED for h5_frontend_failed" "ERROR"
                        $fixSuccess = $false
                    } else {
                        Write-Log "Auto-fix SUCCEEDED for h5_frontend_failed"
                    }
                } else {
                    Write-Log "Auto-fix SUCCEEDED for h5_frontend_failed"
                }
            }

            "nginx_proxy_failed" {
                Write-Log "Fix: Restarting nginx container..."
                Invoke-SSHCommand "docker restart sstcp-nginx"
                Start-Sleep -Seconds 15

                Write-Log "Fix: Checking nginx config..."
                Invoke-SSHCommand "docker exec sstcp-nginx nginx -t"

                $recheck = Invoke-SSHCommand "curl -sf http://localhost/api/v1/health -o /dev/null -w '%{http_code}' 2>&1 || echo 'STILL_FAILED'"
                if ($recheck | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                    Write-Log "Fix: Recreating nginx container..."
                    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose up -d --force-recreate nginx"
                    Start-Sleep -Seconds 15

                    $recheck2 = Invoke-SSHCommand "curl -sf http://localhost/api/v1/health -o /dev/null -w '%{http_code}' 2>&1 || echo 'STILL_FAILED'"
                    if ($recheck2 | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                        Write-Log "Auto-fix FAILED for nginx_proxy_failed" "ERROR"
                        $fixSuccess = $false
                    } else {
                        Write-Log "Auto-fix SUCCEEDED for nginx_proxy_failed"
                    }
                } else {
                    Write-Log "Auto-fix SUCCEEDED for nginx_proxy_failed"
                }
            }

            "db_connection_failed" {
                Write-Log "Fix: Checking if PostgreSQL is running on host..."
                Invoke-SSHCommand "systemctl status postgresql || service postgresql status"
                Invoke-SSHCommand "docker exec sstcp-backend python -c `"from app.database import engine; from sqlalchemy import text; import asyncio; async def check(): async with engine.connect() as conn: r = await conn.execute(text('SELECT 1')); print('DB_OK:', r.scalar()); asyncio.run(check())`" 2>&1"

                Start-Sleep -Seconds 10
                Invoke-SSHCommand "docker restart sstcp-backend"
                Start-Sleep -Seconds 30

                $recheck = Invoke-SSHCommand "curl -sf http://localhost:8000/api/v1/health 2>&1 || echo 'STILL_FAILED'"
                if ($recheck | Out-String | Select-String -Pattern "STILL_FAILED" -Quiet) {
                    Write-Log "Auto-fix FAILED for db_connection_failed" "ERROR"
                    $fixSuccess = $false
                } else {
                    Write-Log "Auto-fix SUCCEEDED for db_connection_failed"
                }
            }

            default {
                Write-Log "No auto-fix available for: $issue" "WARN"
                $fixSuccess = $false
            }
        }
    }

    return $fixSuccess
}

function Invoke-Rollback {
    Write-Log "========== Rolling Back Deployment =========="

    Write-Log "Restoring previous docker-compose.yml..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && ls -t docker-compose.yml.bak.* | head -1 | xargs -I {} cp {} docker-compose.yml"

    Write-Log "Stopping current containers..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose down --remove-orphans"

    Write-Log "Starting previous version..."
    Invoke-SSHCommand "cd $DEPLOY_PATH && docker compose up -d"

    Start-Sleep -Seconds 40

    Write-Log "Checking rollback health..."
    $healthCheck = Invoke-SSHCommand "curl -sf http://localhost:8000/api/v1/health 2>&1 || echo 'ROLLBACK_HEALTH_FAILED'"
    if ($healthCheck | Out-String | Select-String -Pattern "ROLLBACK_HEALTH_FAILED" -Quiet) {
        Write-Log "Rollback health check FAILED! Manual intervention required!" "ERROR"
    } else {
        Write-Log "Rollback completed successfully"
    }
}

function Send-DeployReport {
    param([string]$Status, [string[]]$Issues = @(), [bool]$FixResult = $false)

    Write-Log "========== Deployment Report =========="
    Write-Log "Version: $VERSION"
    Write-Log "Timestamp: $TIMESTAMP"
    Write-Log "Server: $SERVER_IP"
    Write-Log "Overall Status: $Status"

    if ($Issues.Count -gt 0) {
        Write-Log "Issues Found: $($Issues -join ', ')"
        Write-Log "Auto-Fix Result: $(if ($FixResult) { 'SUCCESS' } else { 'FAILED' })"
    }

    Write-Log "Access URLs:"
    Write-Log "  PC Frontend: http://$SERVER_IP"
    Write-Log "  H5 Frontend: http://$SERVER_IP/h5/"
    Write-Log "  API Docs: http://$SERVER_IP/api/docs"
    Write-Log "  Health Check: http://$SERVER_IP/api/v1/health"
    Write-Log "==========================================="

    $reportPath = "$PROJECT_ROOT\deploy-report-$TIMESTAMP.txt"
    Copy-Item $LOG_FILE $reportPath
    Write-Log "Report saved to: $reportPath"
}

function Main {
    Write-Log "============================================"
    Write-Log "  SSTCP Docker Build & Deploy Pipeline"
    Write-Log "  Version: $VERSION"
    Write-Log "  Scheduled Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Log "============================================"

    if (-not (Test-DockerRunning)) {
        Send-DeployReport "FAILED" @("docker_not_running")
        exit 1
    }

    try {
        Build-BackendImage
    } catch {
        Write-Log "Backend build failed: $_" "ERROR"
        Send-DeployReport "FAILED" @("backend_build_failed")
        exit 1
    }

    try {
        Build-PCFrontendImage
    } catch {
        Write-Log "PC Frontend build failed: $_" "ERROR"
        Send-DeployReport "FAILED" @("pc_frontend_build_failed")
        exit 1
    }

    try {
        Build-H5FrontendImage
    } catch {
        Write-Log "H5 Frontend build failed: $_" "ERROR"
        Send-DeployReport "FAILED" @("h5_frontend_build_failed")
        exit 1
    }

    try {
        Save-ImagesToTar
    } catch {
        Write-Log "Save images failed: $_" "ERROR"
        Send-DeployReport "FAILED" @("save_images_failed")
        exit 1
    }

    try {
        Send-DeployPackage
    } catch {
        Write-Log "Transfer to server failed: $_" "ERROR"
        Send-DeployReport "FAILED" @("transfer_failed")
        exit 1
    }

    try {
        Deploy-OnServer
    } catch {
        Write-Log "Server deployment failed: $_" "ERROR"
        Write-Log "Attempting rollback..."
        Invoke-Rollback
        Send-DeployReport "FAILED_AND_ROLLED_BACK" @("deploy_failed")
        exit 1
    }

    $healthy = Wait-ForServices
    if (-not $healthy) {
        Write-Log "Services did not become healthy in time" "WARN"
    }

    $issues = Test-Deployment

    if ($issues.Count -eq 0) {
        Write-Log "DEPLOYMENT SUCCESSFUL! All services are running correctly."
        Send-DeployReport "SUCCESS"
    } else {
        Write-Log "Deployment has $($issues.Count) issue(s), starting auto-fix..." "WARN"
        $fixResult = Invoke-AutoFix -Issues $issues

        if ($fixResult) {
            Write-Log "Auto-fix succeeded! Re-verifying..."
            Start-Sleep -Seconds 20
            $recheckIssues = Test-Deployment
            if ($recheckIssues.Count -eq 0) {
                Write-Log "DEPLOYMENT SUCCESSFUL after auto-fix!"
                Send-DeployReport "SUCCESS_AFTER_AUTOFIX" $issues $true
            } else {
                Write-Log "Auto-fix passed but re-verification found new issues. Rolling back..." "ERROR"
                Invoke-Rollback
                Send-DeployReport "ROLLED_BACK_AFTER_AUTOFIX" $issues $false
            }
        } else {
            Write-Log "Auto-fix failed. Rolling back to previous version..." "ERROR"
            Invoke-Rollback
            Send-DeployReport "FAILED_AND_ROLLED_BACK" $issues $false
        }
    }

    Write-Log "Cleaning up local tar files..."
    Remove-Item "$PROJECT_ROOT\deploy-tars\*.tar" -Force -ErrorAction SilentlyContinue
}

Main
