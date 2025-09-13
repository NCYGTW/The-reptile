# 部署到阿里云 CentOS 服务器指南

## 前置条件

1. 在阿里云ECS上创建一台CentOS 7/8服务器实例
2. 确保安全组规则允许端口8000的入站访问
3. 通过SSH连接到服务器

## 部署步骤

### 1. 安装 Docker 和 Docker Compose

```bash
# 更新系统包
sudo yum update -y

# 安装必要的工具
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动并启用 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证 Docker 安装
sudo docker --version

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证 Docker Compose 安装
docker-compose --version
```

### 2. 传输项目文件

将项目文件从本地传输到阿里云服务器：

```bash
# 在本地执行以下命令
scp -r /path/to/local/project root@your-server-ip:/opt/sspai-api
```

或者使用Git克隆（如果项目在Git仓库中）：

```bash
# 在服务器上执行
sudo yum install -y git
cd /opt
sudo git clone <your-repo-url> sspai-api
```

### 3. 配置数据库

在阿里云上创建一个MySQL数据库实例，或者在服务器上安装MySQL：

```bash
# 在服务器上安装MySQL（可选）
sudo docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=Tian_1901 -e MYSQL_DATABASE=abcd -d mysql:8.0
```

### 4. 配置数据库连接

编辑 `docker-compose.aliyun.yml` 文件中的 `DATABASE_URL` 环境变量：

```yaml
environment:
  - DATABASE_URL=mysql+pymysql://root:your_password@your_mysql_host:3306/abcd?charset=utf8mb4
```

### 5. 构建和启动服务

```bash
# 进入项目目录
cd /opt/sspai-api

# 构建 Docker 镜像
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml build

# 启动服务
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml up -d

# 检查服务状态
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml ps
```

### 6. 验证部署

1. 检查容器日志：
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml logs -f app
   ```

2. 访问API文档：
   ```
   http://your-server-ip:8000/docs
   ```

3. 测试API接口：
   ```bash
   curl http://your-server-ip:8000/articles
   ```

## 常用管理命令

### 停止服务
```bash
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml down
```

### 查看日志
```bash
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml logs -f app
```

### 重启服务
```bash
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml restart
```

### 更新代码后重新部署
```bash
# 重新构建镜像
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml build --no-cache

# 重启服务
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml up -d
```

## 故障排除

### 1. 数据库连接问题

确保：
- MySQL服务正在运行
- 数据库连接信息正确
- 防火墙允许3306端口通信
- MySQL用户具有远程访问权限

### 2. 容器启动失败

查看详细日志：
```bash
docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml logs app
```

### 3. 端口冲突

修改 `docker-compose.aliyun.yml` 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 将主机端口改为8001
```

## 性能优化建议

1. 根据服务器配置调整资源限制：
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

2. 使用Nginx作为反向代理：
   ```yaml
   # 添加到 docker-compose.aliyun.yml
   nginx:
     image: nginx:alpine
     ports:
       - "80:80"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
     depends_on:
       - app
   ```

3. 配置SSL证书以支持HTTPS访问