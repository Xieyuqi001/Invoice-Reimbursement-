# 部署指南

本文档介绍如何将发票管理系统部署到本地，并通过内网穿透让外网用户访问。

## 方案一：本地部署 + 内网穿透（推荐）

适合实验室/公司内部使用，无需购买服务器。

### 1. 本地运行服务

```bash
# 进入项目目录
cd Fapiao

# 安装依赖
pip install -r requirements.txt

# 启动服务（监听所有网络接口）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 内网穿透工具

推荐使用以下工具之一：

| 工具 | 优点 | 免费额度 |
|------|------|----------|
| **ngrok** | 简单易用，无需注册 | 1个隧道 |
| **cpolar** | 国内速度快，中文界面 | 1个隧道 |
| **花生壳** | 国内老牌，稳定 | 1个域名 |

### 3. 使用 ngrok（推荐）

#### 3.1 注册并下载

1. 访问 [ngrok官网](https://ngrok.com/) 注册账号
2. 下载对应系统的客户端
3. 解压到任意目录

#### 3.2 配置认证

```bash
# Windows (PowerShell)
./ngrok authtoken 你的auth_token

# Mac/Linux
./ngrok authtoken 你的auth_token
```

#### 3.3 启动穿透

```bash
# 将本地8000端口映射到外网
./ngrok http 8000
```

启动后会显示类似：

```
Session Status                online
Forwarding                    https://xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

#### 3.4 分享网址

将 `https://xxxx-xxxx.ngrok-free.app` 分享给其他用户即可访问。

### 4. 使用 cpolar（国内推荐）

#### 4.1 下载安装

1. 访问 [cpolar官网](https://www.cpolar.com/) 注册账号
2. 下载并安装客户端

#### 4.2 启动穿透

```bash
# 启动Web UI管理界面
cpolar

# 或直接命令行启动
cpolar http 8000
```

访问 cpolar 管理界面查看生成的公网地址。

### 5. 局域网访问

如果只需要局域网内访问，无需内网穿透：

1. 查看本机IP地址：
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. 其他用户通过 `http://你的IP:8000` 访问

---

## 方案二：云服务器部署

如果需要长期稳定运行，建议购买云服务器。

### 1. 服务器要求

- 系统：Ubuntu 20.04+ / CentOS 7+
- 配置：1核1G即可
- 端口：开放 8000 端口

### 2. 部署步骤

```bash
# 1. 安装Python
sudo apt update
sudo apt install python3 python3-pip -y

# 2. 克隆代码
git clone https://github.com/你的用户名/Fapiao.git
cd Fapiao

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 配置OCR密钥
nano app/config.py

# 5. 使用supervisor管理进程
sudo apt install supervisor -y
sudo nano /etc/supervisor/conf.d/fapiao.conf
```

supervisor 配置内容：

```ini
[program:fapiao]
directory=/path/to/Fapiao
command=python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
autostart=true
autorestart=true
stderr_logfile=/var/log/fapiao.err.log
stdout_logfile=/var/log/fapiao.out.log
```

启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fapiao
```

### 3. 配置域名（可选）

使用 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 注意事项

1. **安全性**：
   - 不要将 `app/config.py` 中的API密钥提交到公开仓库
   - 建议设置访问密码或限制IP访问

2. **性能**：
   - 本地部署适合小规模使用（10人以内）
   - 大规模使用建议云服务器部署

3. **稳定性**：
   - 内网穿透工具可能有连接数限制
   - 云服务器部署更稳定

4. **数据备份**：
   - 定期备份 `fapiao.db` 数据库文件
   - 定期备份 `uploads/` 图片目录
