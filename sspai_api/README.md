# SSPAI API Server

**SSPAI API Server** 是一个基于 FastAPI 框架构建的高性能数据采集与 API 服务系统，专门用于爬取少数派（sspai.com）网站的文章内容和评论数据，并通过 RESTful API 接口提供结构化数据访问。

## 架构设计

本项目采用微服务架构，包含以下几个核心组件：

- **app/main.py**: FastAPI 应用入口，负责路由定义、依赖注入、应用生命周期管理
- **app/models.py**: SQLModel 数据模型定义，包含 Article 和 BestComment 表结构
- **app/crawler.py**: HTTP 请求与数据爬取模块，封装少数派 API 调用逻辑
- **app/database.py**: 数据库操作层，包含 DatabaseHandler 类和会话管理
- **app/processor.py**: 数据处理与清洗模块，负责内容解析和存储逻辑

## 技术栈

### 核心框架
- **FastAPI 0.95.2**: 高性能的 ASGI web 框架，支持异步处理和 API 文档生成
- **SQLModel 0.0.8**: SQL 数据库 ORM，结合了 SQLAlchemy 的强大功能和 Pydantic 的数据验证能力
- **Pydantic 1.10**: 数据验证和设置管理库

### 数据处理
- **BeautifulSoup4 4.12.2**
- **LXML 6.0.1**
### 数据库
- **MySQL 8.0.39**: 数据存储ENGINE
- **PyMySQL 1.0.3**: Python的 MySQL 客户端驱动
- **SQLAlchemy**: SQL 工具包和 ORM 框架底层支持

### HTTP 客户端
- **Requests 2.31.0**: HTTP 库，用于与少数派 API 交互

### 任务调度
- **APScheduler 3.10.1**: 高级 Python 任务调度框架，实现定时爬取功能

### Web 服务器
- **Uvicorn 0.22.0**: 高性能 ASGI 服务器，基于 uvloop 和 httptools

## 功能特性

### 数据采集
- **自动化爬取**: 通过 `SSPAICrawler` 类实现对少数派 API 的定时数据采集
- **内容清洗**: 使用 BeautifulSoup4 清理文章内容中的 HTML 标签，存储原始文本内容
- **评论选择**: 在 `DataProcessor` 中实现基于回复数和时间戳的评论选择算法

### API 端点
- `POST /crawl/{pages}`: 手动触发爬取指定页数（每页20篇文章）的任务
- `GET /articles?skip=0&limit=100`: 获取分页文章列表，默认支持分页查询
- `GET /articles/{article_id}`: 查询单篇文章详情
- `GET /comments?skip=0&limit=100`: 获取评论列表
- `GET /articles/{article_id}/comments`: 获取特定文章的所有评论

### 任务自动化
- **定时任务**: 使用 APScheduler 配置每小时执行一次的数据爬取任务
- **启动任务**: 应用启动时自动执行一次完整的数据爬取流程

## 数据模型(位于`app/models.py`)

### Article 模型 
```python
class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # 数据库主键
    article_id: int = Field(index=True, unique=True)  # 文章ID
    article_title: Optional[str] = Field(default=None, max_length=255)  # 文章标题
    article_text: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))  # 文章内容
    article_likes: int  # 点赞数
    article_time: Optional[str]  # 发布时间
    article_author: Optional[str] = Field(default=None, max_length=100)  # 作者名
```

### BestComment 模型 (`app/models.py`)
```python
class BestComment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # 数据库主键
    comment_id: int  # 评论ID
    article_id: int = Field(index=True)  # 关联的文章ID
    best_comment: Optional[str] = Field(default=None, sa_column=Column(LONGTEXT))  # 评论内容
    comment_author: Optional[str] = Field(default=None, max_length=100)  # 评论作者
    comment_time: Optional[str]  # 评论时间
```

## 配置部署

### Docker 化部署

项目使用多阶段 Dockerfile 构建优化镜像，以减小镜像体积：

#### 构建阶段
1. **Builder 阶段**: 安装编译依赖（gcc, libpq-dev）和 Python 包
2. **Runtime 阶段**: 创建精简的运行环境，复制虚拟环境

#### 依赖管理
- **requirements.txt**: 定义所有 Python 依赖项
- 使用阿里云镜像源加速包安装
- 虚拟环境隔离依赖（`/opt/venv`）

#### 容器编排 (位于`docker-compose.yml`)
- **app 服务**: FastAPI 应用容器，暴露 8000 端口
- **mysql 服务**: MySQL 数据库容器，配置健康检查
- **数据卷**: `sspai-mysql-data`, `sspai-app-data`, `sspai-app-logs`
- **网络**: `sspai-network` 隔离服务通信

### 环境配置

#### 数据库连接
```bash
DATABASE_URL="mysql+pymysql://root:Tian_1901@mysql:3306/abcd?charset=utf8mb4"
```

## 错误处理机制

- **重复数据**: 在 `DatabaseHandler.insert_article()` 和 `insert_comment()` 中实现重复数据检测
- **异常捕获**: 在数据采集、处理、存储各环节添加异常捕获
- **日志记录**: 使用 Python logging 模块记录应用运行状态和错误信息


## 部署命令行

### 构建镜像
```bash
docker build -t sspai-api:latest .
```

### 启动和停止服务
```bash
docker-compose -f docker-compose.yml up -d

docker-compose down
```

