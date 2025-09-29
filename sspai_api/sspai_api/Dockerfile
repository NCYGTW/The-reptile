#构建阶段
FROM python:3.10 AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /build

ARG DEBIAN_CODENAME
RUN test -n "$DEBIAN_CODENAME" || DEBIAN_CODENAME="$(. /etc/os-release; echo $VERSION_CODENAME)"; \
    echo "deb http://mirrors.aliyun.com/debian/ ${DEBIAN_CODENAME} main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security/ ${DEBIAN_CODENAME}-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# 配置 pip 
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#运行阶段
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# 同步源
ARG DEBIAN_CODENAME
RUN test -n "$DEBIAN_CODENAME" || DEBIAN_CODENAME="$(. /etc/os-release; echo $VERSION_CODENAME)"; \
    echo "deb http://mirrors.aliyun.com/debian/ ${DEBIAN_CODENAME} main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security/ ${DEBIAN_CODENAME}-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# 非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser appuser

#复制代码
COPY --chown=appuser:appuser ./app ./app

RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app /opt/venv

USER appuser
#暴露端口
EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]