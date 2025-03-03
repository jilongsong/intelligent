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

## 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 创建 `.env` 文件并设置 OpenAI API Key：
   ```
   OPENAI_API_KEY=你的API密钥
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
