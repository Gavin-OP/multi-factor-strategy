# Quant Factor Strategy Framework

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个专业的多因子量化策略框架，采用分层架构设计。

## 🌐 在线演示

- **前端**: [https://gavin-op.github.io/multi-factor-strategy/](https://gavin-op.github.io/multi-factor-strategy/)
- **API 文档**: https://quant-factor-api.onrender.com/docs

---

## 🏗️ 项目架构

```
src/
├── api/                    # API 层
│   ├── main.py             # FastAPI 入口
│   ├── router/v1/          # 路由定义
│   │   ├── factor_router.py
│   │   ├── backtest_router.py
│   │   └── data_router.py
│   ├── controller/         # 控制器
│   │   ├── factor_controller.py
│   │   ├── backtest_controller.py
│   │   └── data_controller.py
│   └── schema/             # 请求/响应格式
│       └── __init__.py
│
├── application/            # 应用层
│   ├── orchestrator/       # 编排器
│   │   ├── factor_research_orchestrator.py
│   │   └── strategy_backtest_orchestrator.py
│   ├── usecase/            # 用例
│   │   ├── factor/
│   │   │   ├── compute_factor.py
│   │   │   └── validate_factor.py
│   │   └── backtest/
│   │       └── run_backtest.py
│   └── workflow/           # 工作流
│
├── service/                # 服务层（核心业务逻辑）
│   ├── factor/
│   │   ├── factor_compute_service.py
│   │   ├── factor_validate_service.py
│   │   └── factor_analyze_service.py
│   ├── signal/
│   │   └── signal_generation_service.py
│   ├── backtest/
│   │   └── backtest_engine_service.py
│   └── data/
│       └── data_quality_service.py
│
├── model/                  # 模型层
│   ├── factor/
│   │   └── __init__.py     # FactorMeta, FactorValue, FactorResult
│   ├── signal/
│   │   └── __init__.py     # Signal, TradingSignal
│   ├── strategy/
│   │   └── __init__.py     # Strategy, Portfolio, Position, RebalancePlan
│   ├── backtest/
│   │   └── __init__.py     # BacktestResult, PerformanceMetric, TradeRecord
│   ├── risk/
│   │   └── __init__.py     # RiskMetric, Exposure
│   └── market/
│       └── __init__.py     # Stock, Price, Index
│
├── library/                # 因子库/信号库
│   ├── factor_library.py   # 因子注册、存储、查询
│   └── signal_library.py   # 信号注册、存储、查询
│
├── repository/             # 数据访问层
│   └── tushare_repository.py
│
├── config/                 # 配置
│   └── settings.py
│
└── utils/                  # 工具函数
    └── __init__.py
```

---

## 📊 架构层级说明

| 层级 | 职责 | 示例 |
|------|------|------|
| **api/router** | URL 路由定义 | `@router.post("/factors/test")` |
| **api/controller** | 处理 HTTP 请求/响应 | 调用 orchestrator，返回响应 |
| **application/orchestrator** | 编排多个 usecase | 协调因子计算、验证、注册流程 |
| **application/usecase** | 单一业务场景 | 验证一个因子 |
| **service** | 核心业务逻辑 | IC 计算、单调性检验 |
| **library** | 因子/信号管理 | 注册、存储、查询 |
| **repository** | 数据访问 | 从 Tushare 获取数据 |
| **model** | 数据结构 | Stock, Factor, Portfolio |

---

## 🔄 数据流向

```
HTTP Request
    ↓
Router（路由定义）
    ↓
Controller（请求处理）
    ↓
Orchestrator（业务编排）
    ↓
UseCase（用例执行）
    ↓
Service（业务逻辑）
    ↓
Repository（数据访问）
    ↓
Tushare API
```

---

## 🎯 核心流程

```
数据获取 → 因子挖掘 → 因子验证 → 因子注册 → 信号生成 → 组合构建 → 策略回测 → 风险管理
```

---

## 🚀 快速开始

### 后端

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TUSHARE_TOKEN=your_token_here

# 启动服务
uvicorn src.api.main:app --reload
```

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```

---

## 📦 部署

### 后端 (Render)

1. 连接 GitHub 仓库
2. 设置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
3. 添加环境变量：`TUSHARE_TOKEN`

### 前端 (GitHub Pages)

自动部署，更新 `frontend/.env.production` 中的 `VITE_API_URL`

---

## 🔑 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `TUSHARE_TOKEN` | Tushare API Token | 是 |

---

## 📝 命名规范

| 操作 | 命名 | 职责 |
|------|------|------|
| 计算因子 | `compute_factor` | 计算因子值 |
| 验证因子 | `validate_factor` | 验证预测能力 |
| 分析因子 | `analyze_factor` | IC/IR 分析 |
| 评估因子 | `evaluate_factor` | 综合评分 |
| 筛选因子 | `screen_factor` | 筛选有效因子 |
| 注册因子 | `register_factor` | 注册到因子库 |

---

## 📄 License

MIT License
