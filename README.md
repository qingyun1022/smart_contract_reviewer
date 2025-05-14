# 智能合同审查系统

## 项目简介

智能合同审查系统是一个基于人工智能的合同分析工具，旨在帮助法律专业人员和企业快速审查合同文件，识别潜在风险，并提供专业的法律建议。系统利用自然语言处理和机器学习技术，能够自动分析合同条款，识别关键信息，并生成详细的审查报告。

## 主要功能

- **合同上传与管理**：支持PDF、Word和文本格式的合同文件上传和管理
- **智能条款分析**：自动识别和分类合同条款，提取关键信息
- **风险评估**：识别合同中的潜在风险点和不利条款
- **价格条款分析**：专门分析价格相关条款，确保定价合理
- **审查报告生成**：生成专业、详细的合同审查报告
- **预算监控**：跟踪和控制合同审查成本
- **知识库支持**：基于法律知识库提供专业建议

## 技术架构

系统采用现代化的微服务架构，主要组件包括：

- **前端界面**：基于Streamlit构建的用户友好界面
- **合同处理服务**：负责文档解析、文本提取和条款分类
- **法律分析引擎**：基于RAG（检索增强生成）的法律分析系统
- **价格库管理**：维护和更新价格参考数据
- **报告生成服务**：生成专业的审查报告
- **消息队列**：使用RabbitMQ实现组件间的异步通信
- **向量数据库**：使用ChromaDB存储和检索向量化的法律知识

## 安装与运行

### 环境要求

- Python 3.10+
- RabbitMQ
- MySQL

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/qingyun1022/smart_contract_reviewer.git
cd smart_contract_reviewer
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

4. 初始化知识库
```bash
python scripts/init_knowledgebase.py
```

5. 启动应用
```bash
python app/main.py
```

### Docker部署

也可以使用Docker进行部署：

```bash
docker-compose up -d
```

## 使用指南

1. 访问系统首页（默认为http://localhost:8501）
2. 在"上传合同"页面上传合同文件
3. 设置处理优先级并提交
4. 在"分析进度"页面查看处理状态
5. 处理完成后，在"审查报告"页面查看分析结果

## 开发指南

### 项目结构

```
.
├── agents/                # 智能代理组件
├── app/                   # 前端应用
│   ├── components/        # UI组件
│   ├── main_pages/        # 主要页面
│   └── styles/            # 样式文件
├── common/                # 公共工具和配置
├── core_services/         # 核心服务
│   ├── budget_control/    # 预算控制
│   ├── contract_processor/# 合同处理
│   ├── legal_brain/       # 法律分析引擎
│   ├── price_library/     # 价格库
│   └── prompt_engineering/# 提示工程
├── data/                  # 数据文件
│   ├── chroma_db/         # 向量数据库
│   ├── files/             # 文件存储
│   └── knowledge/         # 知识库
├── data_storage/          # 数据存储服务
├── message_broker/        # 消息代理
├── model_services/        # 模型服务
├── scripts/               # 脚本工具
└── tests/                 # 测试代码
```

### 添加新功能

1. 在相应模块中实现功能逻辑
2. 更新前端界面
3. 编写单元测试
4. 提交PR请求

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件

## 联系方式

如有问题或建议，请通过Issues页面提交，或联系项目维护者。