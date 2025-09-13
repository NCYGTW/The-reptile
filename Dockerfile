# 多阶段构建：构建阶段
FROM python:3.10-slim as builder

WORKDIR /app

# 更换APT源为阿里云镜像
    RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
            sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 配置pip使用阿里云镜像
    RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 安装Python依赖到本地目录
RUN pip install --user --no-cache-dir -r requirements.txt

# 多阶段构建：运行阶段
 FROM python:3.10-slim 

WORKDIR /app

 # 更换APT源为阿里云镜像
    RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
        sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 配置pip使用阿里云镜像
    RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/


# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制已安装的依赖
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p ./data && chown -R appuser:appuser ./data

# 更改文件所有权
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 确保脚本可执行
RUN chmod +x ./start-docker.py

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PATH=/home/appuser/.local/bin:$PATH

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]