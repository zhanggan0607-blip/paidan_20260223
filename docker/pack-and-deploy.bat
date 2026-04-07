@echo off
chcp 65001 >nul
echo ==========================================
echo   工程维保系统 - 打包部署脚本
echo ==========================================
echo.

REM 设置服务器信息
set SERVER_HOST=8.153.93.123
set SERVER_USER=root
set SERVER_PASS=Lily421020
set DEPLOY_PATH=/opt/tq-system

REM 检查WinSCP是否可用
where winscp.com >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 WinSCP，请先安装 WinSCP
    echo 下载地址: https://winscp.net/eng/download.php
    pause
    exit /b 1
)

echo [步骤1] 创建临时打包目录...
if exist "deploy-temp" rmdir /s /q deploy-temp
mkdir deploy-temp
mkdir deploy-temp\tq-system

echo [步骤2] 复制项目文件...
REM 复制后端
xcopy /E /I /Q backend-python deploy-temp\tq-system\backend-python >nul

REM 复制前端PC端
xcopy /E /I /Q src deploy-temp\tq-system\src >nul
xcopy /E /I /Q public deploy-temp\tq-system\public >nul
copy package.json deploy-temp\tq-system\ >nul
copy package-lock.json deploy-temp\tq-system\ >nul
copy vite.config.ts deploy-temp\tq-system\ >nul
copy tsconfig.json deploy-temp\tq-system\ >nul
copy tsconfig.node.json deploy-temp\tq-system\ >nul
copy index.html deploy-temp\tq-system\ >nul

REM 复制H5手机端
xcopy /E /I /Q H5 deploy-temp\tq-system\H5 >nul

REM 复制Docker配置
xcopy /E /I /Q docker deploy-temp\tq-system\docker >nul

REM 复制数据库初始化脚本
mkdir deploy-temp\tq-system\docker\init-db
copy docker\init-db\01_init.sql deploy-temp\tq-system\docker\init-db\ >nul

echo [步骤3] 清理不需要的文件...
REM 删除Python缓存
for /d /r deploy-temp\tq-system\backend-python %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r deploy-temp\tq-system\backend-python %%d in (.venv) do @if exist "%%d" rd /s /q "%%d"
del /s /q deploy-temp\tq-system\backend-python\*.pyc >nul 2>&1

REM 删除Node modules
if exist "deploy-temp\tq-system\node_modules" rd /s /q "deploy-temp\tq-system\node_modules"
if exist "deploy-temp\tq-system\H5\node_modules" rd /s /q "deploy-temp\tq-system\H5\node_modules"

echo [步骤4] 创建压缩包...
cd deploy-temp
tar -czvf tq-system.tar.gz tq-system
cd ..

echo [步骤5] 上传到服务器...
echo 正在连接服务器 %SERVER_HOST%...

REM 创建WinSCP脚本
echo option batch abort > upload.scp
echo option confirm off >> upload.scp
echo open sftp://%SERVER_USER%:%SERVER_PASS%@%SERVER_HOST% >> upload.scp
echo mkdir %DEPLOY_PATH% >> upload.scp
echo put deploy-temp\tq-system.tar.gz %DEPLOY_PATH%/ >> upload.scp
echo call cd %DEPLOY_PATH% ^&^& tar -xzvf tq-system.tar.gz >> upload.scp
echo call cd %DEPLOY_PATH%/tq-system/docker ^&^& chmod +x deploy.sh >> upload.scp
echo close >> upload.scp
echo exit >> upload.scp

winscp.com /script=upload.scp
del upload.scp

echo.
echo ==========================================
echo   上传完成！
echo ==========================================
echo.
echo 接下来请SSH登录服务器执行以下命令:
echo.
echo   ssh root@%SERVER_HOST%
echo   cd %DEPLOY_PATH%/tq-system/docker
echo   ./deploy.sh
echo.
echo 或者直接运行:
echo.
echo   ssh root@%SERVER_HOST% "cd %DEPLOY_PATH%/tq-system/docker && ./deploy.sh"
echo.

REM 清理临时文件
echo [清理] 删除临时文件...
rmdir /s /q deploy-temp

echo 完成！
pause
