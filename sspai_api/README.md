# SSPAI API Server

这是一个基于 FastAPI 的数据服务，用于爬取少数派网站的文章和评论数据，并提供 API 接口进行访问。

## 功能特性

- 自动定时爬取少数派网站的文章和评论数据
- 提供 RESTful API 接口访问数据
- 支持手动触发爬取指定页数的文章
- 使用 Docker 进行容器化部署

## 技术栈

- FastAPI: 高性能 Python Web 框架
- SQLModel: SQLAlchemy + Pydantic 的数据库 ORM
- MySQL: 数据存储
- Docker: 容器化部署
- BeautifulSoup4: 网页解析
- APScheduler: 任务调度

## Docker 部署

### 镜像构建

项目提供了优化的多阶段 Dockerfile，可以构建轻量级的生产镜像：

```bash
# 构建生产镜像
docker build -t sspai-api:latest .

# 构建开发镜像
docker build -t sspai-api-dev:latest -f Dockerfile.dev .
```

### 使用 Docker Compose 部署

项目提供了多个 docker-compose 配置文件，用于不同环境的部署：

#### 跨平台启动脚本

项目提供了跨平台的启动脚本，可以在 Windows （部署在本机）和 Linux 系统（部署在阿里云服务器）上使用：

1. **Windows 系统**:
   ```cmd
   start-docker-universal.bat
   ```

2. **Linux/macOS 系统**:
   ```bash
   ./start-docker-universal.sh
   ```

3. **使用 Python 脚本**:
   ```bash
   python start-docker.py
   ```

#### 手动部署

1. **构建镜像**:
   ```bash
   docker-compose build
   ```

2. **启动服务**:
   ```bash
   # 开发环境 (本地)
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   
   # 生产环境 (服务器)
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   
   # 阿里云环境
   docker-compose -f docker-compose.yml -f docker-compose.aliyun.yml up -d
   ```

3. **停止服务**:
   ```bash
   docker-compose down
   ```

### 环境配置

项目使用不同的 docker-compose 文件来管理不同环境的配置：

- `docker-compose.yml`: 基础配置
- `docker-compose.dev.yml`: 开发环境配置，支持热重载
- `docker-compose.prod.yml`: 生产环境配置，包含资源限制
- `docker-compose.aliyun.yml`: 阿里云环境配置
- `docker-compose.override.yml`: Windows 本地开发环境配置

### 数据持久化

项目使用 Docker 卷来持久化数据：

- `sspai-mysql-data`: MySQL 数据库存储
- `sspai-app-data`: 应用数据存储
- `sspai-app-logs`: 应用日志存储

### 网络配置

所有服务都在 `sspai-network` 网络中运行，确保服务间安全通信。

## API 接口

服务启动后，可以通过以下接口访问数据：

- `POST /crawl/{pages}`: 手动爬取指定页数的文章
- `GET /articles`: 获取文章列表
- `GET /articles/{article_id}`: 获取指定文章
- `GET /comments`: 获取评论列表
- `GET /articles/{article_id}/comments`: 获取指定文章的评论

API 文档可以通过 `http://localhost:8000/docs` 访问。

## 数据库配置

项目默认连接到 MySQL 数据库，可以通过以下环境变量进行配置：

- `DATABASE_URL`: 数据库连接字符串

在不同环境中，数据库连接配置可能不同：
- Windows 本地开发环境: 使用 SQLite 数据库
- Linux 生产环境: 使用 MySQL 容器或外部数据库

## 定时任务

服务启动后会自动启动定时任务，每小时爬取一次数据。首次启动时也会立即爬取一次。

## 停止服务

使用以下命令停止服务：

```bash
# Windows
stop-docker-universal.bat

# Linux/macOS
./stop-docker-universal.sh
```

或者使用 Docker Compose:

```bash
docker-compose down
```