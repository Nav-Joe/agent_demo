# 🏠 本地家居 AI Agent 系统

基于 Ollama 本地大模型 + LangChain Agent 架构的智能家居助手，支持天气查询、出行建议、日出日落计算、主动对话提醒。完整 Docker 容器化部署，非 root 安全运行，配置化环境变量管理。

&gt; 纯本地大模型运行（Qwen2.5:3B），零外部 LLM API 依赖，隐私安全。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🌤️ **天气查询** | 基于 Tavily 搜索引擎获取实时天气，RAG 增强回答，防幻觉机制 |
| 🚗 **出行建议** | 综合天气 + 日出日落，给出时段化出行建议 |
| 🌅 **日出日落** | 纯本地天文算法（astral），无需网络 |
| 💬 **主动对话** | Agent 自主判断是否需要主动发起对话，支持时间策略 |
| 🐳 **容器化部署** | Docker 多阶段构建，非 root 运行，健康检查 |

---

## 🏗️ 技术栈

- **大模型**：Ollama + Qwen2.5:3B（本地私有化部署）
- **Agent 框架**：LangChain + 自定义 Intent Router（意图识别路由）
- **搜索增强**：Tavily API（实时信息检索）
- **前端**：Gradio 4.x
- **容器化**：Docker + Docker Compose（多阶段构建）
- **配置管理**：Pydantic Settings + python-dotenv（类型校验、环境变量隔离）
- **结构化日志**：标准 logging 模块，支持 `LOG_LEVEL` 配置

---

## 📁 项目结构
.
├── agents/                 # Agent 模块目录
│   ├── cities.py          # 共享城市坐标与提取逻辑
│   ├── llm.py             # Ollama LLM 工厂（统一 base_url / model）
│   ├── router.py          # 意图识别路由 Agent
│   ├── weather.py         # 天气查询 Agent（Tavily 搜索 + RAG）
│   ├── outing.py          # 出行建议 Agent（多 Agent 协作）
│   ├── suntime.py         # 日出日落 Agent（纯本地计算）
│   └── proactive.py       # 主动对话 Agent（异步策略）
├── main.py                # Gradio 前端 + 主控调度
├── config.py              # 配置中心（Pydantic Settings）
├── logging_config.py      # 结构化日志初始化
├── Dockerfile             # Docker 多阶段构建
├── docker-compose.yml     # 一键编排启动
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略规则（含 .env）
└── requirements.txt       # Python 依赖


---

## 🚀 快速开始（Docker 部署）

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 .env，填入你的 Tavily API Key：
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
Tavily 注册地址：https://tavily.com（每月 1000 次免费额度）

### 2. 确认 Ollama 在宿主机运行
```bash
ollama list
# 如未启动：ollama serve
# 确保已下载模型：ollama pull qwen2.5:3b
```
### 3. 构建并启动容器
```bash
docker-compose up --build -d
```
### 4. 访问服务
浏览器打开 http://localhost:7860

### 5. 查看日志 / 停止
```bash
docker-compose logs -f home-ai   # 查看实时日志
docker-compose down              # 停止服务
```


## 💻 本地运行（非 Docker）
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（同上，创建 .env）

# 3. 确认 Ollama 运行
ollama serve

# 4. 启动
python main.py
```

# 🧠 核心架构说明
## Agent 路由机制
用户输入 → IntentRouter（本地 LLM 意图识别）→ 分发至对应 Agent：
weather → 天气查询
outing → 出行建议
suntime → 日出日落
proactive → 主动对话策略
chat → 基座模型直接回答
## 主动对话策略
ProactiveAgent 基于对话历史 + 沉默时长 + 时间敏感性，通过 ReAct 风格 Prompt 输出 JSON 决策：
```JSON
{
  "should_proactive": true,
  "delay_minutes": 5,
  "topic": "提醒用户带伞",
  "reason": "天气预报显示即将降雨"
}
```
## 防幻觉机制
天气 Agent 在 Tavily 搜索结果中强制验证城市名匹配，若搜索结果不含目标城市，直接拒绝回答，防止模型编造错误天气信息。

## 近期优化
- **Pydantic Settings**：集中管理配置，支持 `OLLAMA_MODEL`、`PROACTIVE_SILENCE_MINUTES`、`LOG_LEVEL` 等
- **LLM 工厂**：统一 Ollama 连接（修复 `OLLAMA_HOST` 此前未生效的问题）
- **共享城市数据**：`agents/cities.py` 消除各 Agent 重复的城市列表
- **闲聊流式输出**：Gradio 前端对 chat 意图启用 token 级流式响应
- **出行并行查询**：天气搜索与日出日落计算并发执行，降低响应延迟
- **意图路由兜底**：非法意图自动回退到 chat，避免路由异常
- **结构化日志**：关键路径（意图识别、搜索失败等）可观测

## 🔒 安全设计
敏感信息隔离：API Key 全部通过 .env 环境变量注入，.env 已加入 .gitignore，永不入 Git
非 root 容器：Docker 内以 appuser 用户运行，最小权限原则
健康检查：容器内置 HTTP 健康探针，异常自动重启