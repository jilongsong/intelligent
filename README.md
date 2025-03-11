# 本地智能对话系统

基于 LangChain 框架实现的本地智能对话系统，支持持续对话并保持对话历史记录。

## 功能特点

- 基于 OpenAI GPT 模型的智能对话
- 保持对话上下文记忆
- RESTful API 接口
- 支持查看对话历史

## 环境要求

- Python 3.8+
- OpenAI API Key

## 部署步骤

1. 克隆代码库：
```bash
git clone <repository_url>
cd intelligent
```

2. 创建并激活虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
复制`.env.example`为`.env`并设置必要的环境变量：
```bash
cp .env.example .env
```

必要的环境变量包括：
```
OPENAI_API_KEY=你的API密钥
```

5. 启动服务：

开发环境：
```bash
# 直接启动
python main.py

# 或使用uvicorn（支持热重载）
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

生产环境：
```bash
# 使用gunicorn（仅支持Linux/Mac）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Windows生产环境
# 使用waitress
waitress-serve --host=0.0.0.0 --port=8000 main:app
```

## 使用方法

1. 启动服务器：
   ```bash
   python main.py
   ```

2. 访问接口：
   - 聊天接口：POST http://localhost:8000/chat
   - 历史记录：GET http://localhost:8000/history

## API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 API 文档。

## 示例请求

```bash
# 发送聊天消息
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "你好"}'

# 获取历史记录
curl "http://localhost:8000/history"
```

## 注意事项

1. 生产环境部署时建议：
   - 使用反向代理（如Nginx）
   - 配置SSL证书
   - 设置适当的安全头部
   - 启用请求限制
   - 配置日志轮转

2. 性能优化：
   - 适当调整工作进程数
   - 配置合适的超时时间
   - 监控服务器资源使用

3. 安全性：
   - 妥善保管API密钥
   - 限制API访问范围
   - 定期更新依赖包
   - 配置防火墙规则

## 维护说明

- 定期检查日志文件
- 监控服务器状态
- 及时更新依赖包
- 备份重要数据
