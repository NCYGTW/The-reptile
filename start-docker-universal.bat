@echo off
:: 跨平台 Docker 启动脚本 (适用于 Windows)

echo 正在启动 SSPAI API Docker 服务 (Windows)...

:: 检查 Docker 是否安装并运行
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未安装或未运行
    exit /b 1
)

:: 检查 Docker Compose 版本
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    set COMPOSE_CMD=docker compose
    echo 使用新版本 Docker Compose
) else (
    docker-compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker-compose
        echo 使用旧版本 Docker Compose
    ) else (
        echo 错误: 未找到 Docker Compose
        exit /b 1
    )
)

:: 设置 compose 文件
set COMPOSE_FILES=-f docker-compose.yml -f docker-compose.override.yml

:: 启动服务
echo 正在构建并启动容器...
%COMPOSE_CMD% %COMPOSE_FILES% up -d

if %errorlevel% equ 0 (
    echo 服务启动完成！
    
    :: 检查容器状态
    echo 检查容器状态...
    %COMPOSE_CMD% ps | findstr sspai-api
    
    echo 可以访问 http://localhost:8000/docs 查看 API 文档
) else (
    echo 服务启动失败
    exit /b 1
)