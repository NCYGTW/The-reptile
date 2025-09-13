#!/bin/bash
# 阿里云 CentOS 部署脚本

echo "开始部署 SSPAI API 到阿里云 CentOS 服务器..."

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then
  echo "请以 root 权限运行此脚本"
  exit 1
fi

# 更新系统包
echo "更新系统包..."
yum update -y

# 安装必要的工具
echo "安装必要的工具..."
yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
echo "添加 Docker 仓库..."
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
echo "安装 Docker..."
yum install -y docker-ce docker-ce-cli containerd.io

# 启动并启用 Docker 服务
echo "启动 Docker 服务..."
systemctl start docker
systemctl enable docker

# 安装 Docker Compose
echo "安装 Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 创建项目目录
echo "创建项目目录..."
mkdir -p /opt/sspai-api
cd /opt/sspai-api

# 下载项目文件（这里假设您会手动上传文件）
echo "请确保项目文件已上传到 /opt/sspai-api 目录"

# 构建 Docker 镜像
echo "构建 Docker 镜像..."
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml build

# 启动服务
echo "启动服务..."
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml up -d

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml ps

echo "部署完成！请根据需要修改 docker-compose.aliyun.yml 中的数据库连接信息"
echo "然后重新启动服务：docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml up -d"