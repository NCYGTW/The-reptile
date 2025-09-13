#!/bin/bash
# 跨平台 Docker 启动脚本 (适用于 Linux 和 Windows WSL)

echo "正在启动 SSPAI API Docker 服务..."

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

# 启动服务
echo "正在构建并启动容器..."
$COMPOSE_CMD $COMPOSE_FILES up -d

if [ $? -eq 0 ]; then
    echo "服务启动完成！"
    
    # 检查容器状态
    echo "检查容器状态..."
    $COMPOSE_CMD ps | grep sspai-api
    
    # 显示访问地址
    if [ "$PLATFORM" = "windows" ]; then
        echo "可以访问 http://localhost:8000/docs 查看 API 文档"
    else
        IP=$(hostname -I | awk '{print $1}')
        echo "可以访问 http://$IP:8000/docs 查看 API 文档"
    fi
else
    echo "服务启动失败"
    exit 1
fi