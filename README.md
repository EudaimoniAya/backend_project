# 一、项目介绍
一个后端实验项目，用于探索从简陋原型优化至成熟架构项目的方法论。  
该后端场景为电商网站，在传统后端的基础上新加入了AI功能，架构设计上尽量保证项目的可扩展性
# 二、模块介绍
**传统后端架构：**
* 运维：日志与监控、配置管理
* 模型层：包含两种数据模型，用于操作数据库的ORM模型（models）和数据验证的Pydantic模型（schemas）  
  但是两种模型因为作用位置不同，物理上不会放在一起，ORM模型单独作为`models`模块内容，Pydantic模型作为`schemas`模块下内容。
* 核心层：包含像数据库引擎创建、会话工厂创建等基础设施代码
* 仓储层：根据业务需求操作数据库
* 服务层：实现业务需求，向路由层提供服务
* 路由层：调用服务层功能，完成HTTP请求、响应报文处理，暴露端口提供服务  

**AI应用架构：**
* 运维：日志与监控、配置管理、成本追踪
* 数据仓储层：向量存储知识库、上下文存储
* 工具执行层：LLM客户端、工具执行器、外部API集成
* 智能体层：角色定义、工具注册表
* 编排层：任务分解器、工作流引擎、智能体调度器
* 表现层：API端点  
将两种架构相结合：运维层合并，并将AI应用作为传统后端服务内的一个组件，AI应用的表现层
改为服务层，不对外暴露API而是与主应用的服务层并列共同被主应用的路由层调用，其他的部分一起
作为主应用的核心层部分（各层分别集成在core/agent模块下）。
# 三、项目目录
最终目标是构建出类似下面目录的后端项目，但是不会太注重于传统后端业务实现。
```text
backendProject/
├── operations/            # 运维层（合并）
│   ├── monitoring.py      # 应用+AI监控
│   ├── loggings           # 日志系统
│   │   └── logger.py 
│   ├── settings/          # 配置管理 
│   │   └── config.py 
│   └── cost_tracking.py    # AI成本追踪
├── models/                # ORM模型
│   ├── product.py
│   ├── user.py
│   └── order.py
├── schemas/               # Pydantic验证模型  
│   ├── product_schemas.py
│   ├── user_schemas.py
│   └── order_schemas.py
├── core/                  # 核心层
│   ├── database.py        # 数据库引擎
│   ├── session_factory.py
│   └── ai/                   # AI核心（重构为清晰的层级）
│       ├── data/          # ⭐数据层（是智能化的数据基础设施层）
│       │   ├── models/
│       │   │   ├── product_vector.py   # 商品向量模型 对应限界上下文的AI上下文 
│       │   │   └── ai_session.py       # AI会话模型
│       │   ├── stores/         # AI数据存储（相当于AI的仓储层）
│       │   │   ├── product_vector_store.py   # 商品向量存储
│       │   │   ├── ai_session_store.py       # AI会话存储
│       │   │   └── knowledge_base.py         # 知识库
│       │   └── vector_store.py     # 向量数据库客户端
│       ├── execution/     # ⭐执行层
│       │   ├── llm_client.py
│       │   ├── tool_executor.py
│       │   └── api_clients.py
│       ├── agent/         # ⭐智能体层
│       │   ├── base_agent.py
│       │   ├── product_agent.py
│       │   ├── customer_agent.py
│       │   └── recommendation_agent.py
│       └── tools/         # ⭐智能体层（工具部分）
│           ├── registry.py
│           ├── inventory_tools.py
│           └── customer_tools.py
├── orchestration/         # ⭐新增：编排层（独立出来）
│   ├── orchestrator.py    # 主编排器
│   ├── task_decomposer.py # 任务分解器
│   ├── workflow_engine.py # 工作流引擎
│   └── agent_scheduler.py # 智能体调度器
├── repositories/          # 仓储层
│   ├── product_repo.py
│   ├── user_repo.py
│   └── order_repo.py
├── services/             # 服务层
│   ├── traditional/      # 传统业务服务
│   │   ├── order_service.py
│   │   └── user_service.py
│   └── ai/              # AI服务（原表现层）
│       └── chat_service.py
├── api/                  # ⭐表现层（重命名routers为api更清晰）
│   ├── routers/          # 路由定义
│   │   ├── product.py
│   │   └── order.py
│   ├── middleware/       # 中间件
│   └── dependencies/     # 依赖注入
└── main.py
```

