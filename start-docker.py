#!/usr/bin/env python3
"""
跨平台 Docker 启动脚本
支持 Windows 和 Linux 系统
"""

import os
import sys
import platform
import subprocess
import argparse


def detect_platform():
    """检测当前操作系统平台"""
    return platform.system().lower()


def run_command(command, shell=False):
    """运行系统命令"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return None


def check_docker():
    """检查 Docker 是否已安装并运行"""
    try:
        result = subprocess.run(["docker", "version"], 
                              capture_output=True, text=True, check=True)
        print("Docker 检查通过")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: Docker 未安装或未运行")
        return False


def check_docker_compose():
    """检查 Docker Compose 是否可用"""
    try:
        # 尝试新版本的 docker compose 命令
        result = subprocess.run(["docker", "compose", "version"], 
                              capture_output=True, text=True, check=True)
        print("Docker Compose (新版本) 检查通过")
        return "new"
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # 尝试旧版本的 docker-compose 命令
            result = subprocess.run(["docker-compose", "version"], 
                                  capture_output=True, text=True, check=True)
            print("Docker Compose (旧版本) 检查通过")
            return "old"
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("错误: Docker Compose 未安装")
            return None


def start_services(platform_type, compose_version, env="dev"):
    """启动 Docker 服务"""
    print(f"正在启动 SSPAI API Docker 服务 ({platform_type})...")
    
    # 根据环境选择配置文件
    if env == "prod":
        compose_files = ["docker-compose.yml", "docker-compose.prod.yml"]
        print("使用生产环境配置")
    else:
        if platform_type == "windows":
            compose_files = ["docker-compose.yml", "docker-compose.override.yml"]
            print("使用 Windows 开发环境配置")
        else:
            compose_files = ["docker-compose.yml", "docker-compose.prod.yml"]
            print("使用 Linux 开发环境配置")
    
    # 构建 docker-compose 命令
    if compose_version == "new":
        cmd = ["docker", "compose"]
    else:
        cmd = ["docker-compose"]
    
    # 添加配置文件参数
    for file in compose_files:
        cmd.extend(["-f", file])
    
    # 添加启动命令
    cmd.extend(["up", "-d"])
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行启动命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("服务启动完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"启动服务失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def check_container_status():
    """检查容器状态"""
    print("检查容器状态...")
    
    try:
        # 尝试新版本命令
        result = subprocess.run(
            ["docker", "ps"], 
            capture_output=True, 
            text=True, 
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # 尝试旧版本命令
            result = subprocess.run(
                ["docker-compose", "ps"], 
                capture_output=True, 
                text=True, 
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("无法检查容器状态")
            return
    
    if "sspai-api" in result.stdout:
        print("容器运行状态正常")
    else:
        print("未找到正在运行的 sspai-api 容器")


def get_service_url(platform_type):
    """获取服务访问地址"""
    if platform_type == "windows":
        return "http://localhost:8000/docs"
    else:
        try:
            # 获取本机IP地址
            result = subprocess.run(
                ["hostname", "-I"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            ip = result.stdout.strip().split()[0]
            return f"http://{ip}:8000/docs"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "http://localhost:8000/docs"


def main():
    parser = argparse.ArgumentParser(description="跨平台 Docker 启动脚本")
    parser.add_argument(
        "--env", 
        choices=["dev", "prod"], 
        default="dev", 
        help="环境类型 (dev=开发环境, prod=生产环境)"
    )
    args = parser.parse_args()
    
    # 检查 Docker 和 Docker Compose
    if not check_docker():
        sys.exit(1)
    
    compose_version = check_docker_compose()
    if not compose_version:
        sys.exit(1)
    
    # 检测平台
    current_platform = detect_platform()
    if current_platform not in ["windows", "linux"]:
        print(f"警告: 不支持的操作系统 {current_platform}，将尝试以 Linux 模式运行")
        current_platform = "linux"
    
    # 启动服务
    if start_services(current_platform, compose_version, args.env):
        # 检查容器状态
        check_container_status()
        
        # 显示访问地址
        url = get_service_url(current_platform)
        print(f"服务启动完成！可以访问 {url} 查看 API 文档")


if __name__ == "__main__":
    main()