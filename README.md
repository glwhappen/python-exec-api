
## 项目简介

这个项目提供了一个基于Flask的API，允许用户在一定限制下安全地执行Python代码。代码执行在一个隔离的环境中进行，API通过限制对危险模块的访问来确保安全性。

## 功能特点

- **安全的执行环境**：API排除了如`os`、`sys`和`subprocess`等危险模块，以防止恶意操作。
- **可定制的执行**：用户可以在代码中传递参数，这些参数将被安全地注入到执行环境中。
- **超时处理**：代码执行限制为60秒，以防止滥用并确保响应及时。
- **内存限制**：内存使用限制为200MB，以进一步确保执行环境的安全性。

## 运行方式

### 先决条件

- Docker
- Docker Compose

### 直接运行

```
version: '3.8'

services:
  flask-app:
    image: glwhappen/backup-mysql:latest
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - TZ=Asia/Shanghai
    volumes:
      - .:/app


```

## 编译运行

### 步骤

1. **克隆代码库**：
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **构建Docker镜像**：
   ```bash
   docker-compose build
   ```

3. **运行Docker容器**：
   ```bash
   docker-compose up
   ```

4. **访问API**：API将会在`http://localhost:5000`启动。你可以使用`curl`或Postman等工具向`/run`发送POST请求。

### 示例请求

```bash
curl -X POST http://localhost:5000/run -H "Content-Type: application/json" -d '{"code": "print(Hello, World!)"}'
```

## 包含的文件

- `app.py`：主Flask应用文件。
- `Dockerfile`：用于构建应用镜像的Docker配置文件。
- `docker-compose.yml`：用于管理多容器Docker应用的Docker Compose文件。
- `requirements.txt`：Flask应用的Python依赖项。

## License

This project is licensed under the MIT License.

## 许可证

本项目采用MIT许可证。