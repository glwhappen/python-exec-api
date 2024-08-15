# 使用官方 Python 镜像作为基础镜像
FROM registry.cn-beijing.aliyuncs.com/dockerhub_happen/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制并安装依赖包
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple some-package

# 复制当前目录中的内容到容器的工作目录中
COPY . /app

# 暴露 Flask 的默认端口
EXPOSE 5000

# 运行 Flask 应用
CMD ["python", "app.py"]
