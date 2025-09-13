#!/bin/bash
# 跨平台 Docker 停止脚本 (适用于 Linux 和 Windows WSL)

echo "正在停止 SSPAI API Docker 服务..."

# 检查操作系统类型
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows 系统 (Git Bash)
    PLATFORM="windows"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.override.yml"
    echo "检测到 Windows 系统"
else
    # Linux 或其他类 Unix 系统
    PLATFORM="linux"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
    echo "检测到 Linux 系统"
fi

# 检查 Docker 是否运行
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到 Docker 命令"
    exit 1
fi

# 检查 Docker Compose 版本
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "使用新版本 Docker Compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "使用旧版本 Docker Compose"
else
    echo "错误: 未找到 Docker Compose"
    exit 1
fi

# 停止服务
echo "正在停止容器..."
$COMPOSE_CMD $COMPOSE_FILES down

if [ $? -eq 0 ]; then
    echo "服务已停止"
else
    echo "停止服务失败"
    exit 1
fi