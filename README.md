# AIFriends

AI 角色聊天应用，支持角色创建、语音合成、知识库 RAG 问答。

## 环境要求

- Python >= 3.12
- Node.js >= 22.12
- MySQL 8.0

## Quick Start

### 1. 克隆项目

```bash
git clone https://github.com/czhendan/AIFriends.git
cd AIFriends
```

### 2. 后端配置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt

# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS aifriends CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 API_KEY 等配置
```

`backend/.env` 需要配置以下内容：

```env
MODEL="deepseek-v4-flash"
API_KEY="your-api-key"
API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
WSS_URL="wss://dashscope.aliyuncs.com/api-ws/v1/inference"
VOICE_URL="https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization"
```

### 3. 初始化知识库

```bash
cd backend

# 数据库迁移
python manage.py migrate

# 准备知识库文档（可选，编辑 web/documents/data.txt）
# 然后导入文档到向量库和 BM25 索引
python manage.py shell -c "from web.documents.utils.insert_documents import insert_documents; insert_documents()"
```

### 4. 启动后端

```bash
cd backend
python manage.py runserver
```

后端运行在 `http://127.0.0.1:8000`

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`

## 评估检索效果

```bash
cd backend
python -m web.documents.utils.evaluation.run_evaluation
```

评估管道会自动生成测试集，执行三路检索对比（Vector / BM25 / Hybrid），输出指标报告和 Markdown 详细报告。
