# Quant Factor Strategy Framework

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy](https://github.com/Gavin-OP/multi-factor-strategy/actions/workflows/deploy.yml/badge.svg)](https://github.com/Gavin-OP/multi-factor-strategy/actions)

一个专业的量化因子策略框架，按照百亿量化私募标准设计和实现。

## 🌐 在线演示

- **前端**: [https://gavin-op.github.io/multi-factor-strategy/](https://gavin-op.github.io/multi-factor-strategy/)
- **API 文档**: 部署后端后访问 `/docs`

## 📋 项目概述

本项目是一个完整的量化因子研究和策略实现框架，包含从数据处理、因子挖掘、信号生成、组合构建到回测评估的全流程实现。

### 核心特性

- **📐 架构设计**: 分层架构，Separation of Concerns，易于维护和扩展
- **📊 因子库**: 实现 14 个量价因子（参考 WorldQuant 101）
- **🔍 因子测试**: IC/IR 分析、分组测试、单调性检验、换手率分析
- **⚙️ 信号生成**: 多因子融合、信号标准化、股票筛选
- **💼 组合构建**: 多种加权方式、再平衡逻辑、持仓管理
- **📈 回测引擎**: 完整回测系统
- **📉 风险管理**: VaR/CVaR、最大回撤、风险预算
- **📊 可视化**: React + Ant Design + ECharts 仪表盘

## 🗂️ 项目结构

```
quant_factor_strategy/
├── api/                        # 后端 API
│   ├── main.py                # FastAPI 主应用
│   └── requirements.txt       # Python 依赖
├── frontend/                   # 前端
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # 公共组件
│   │   ├── i18n/             # 国际化
│   │   └── theme/            # 主题配置
│   └── package.json
├── src/                       # 核心代码
│   ├── data/                  # 数据层
│   │   └── providers.py      # Tushare/AkShare 数据提供者
│   ├── factors/              # 因子层
│   │   └── factor_engine.py # 因子计算引擎
│   ├── backtest/             # 回测层
│   │   └── backtest_engine.py
│   └── ...
├── render.yaml               # Render 部署配置
└── railway.json              # Railway 部署配置
```

## 🚀 快速开始

### 前端 (本地开发)

```bash
cd frontend
pnpm install
pnpm dev
```

### 后端 (本地开发)

```bash
# 安装依赖
pip install -r api/requirements.txt
pip install tushare

# 设置环境变量
export TUSHARE_TOKEN=your_token_here

# 启动服务
cd api
uvicorn main:app --reload
```

## 📦 部署指南

### 方案一：Render (推荐)

1. Fork 本仓库
2. 访问 [Render](https://render.com/) 并连接 GitHub
3. 创建新的 Web Service
4. 选择本仓库，Render 会自动检测 `render.yaml`
5. 设置环境变量 `TUSHARE_TOKEN`
6. 部署完成后，更新前端的 `VITE_API_URL`

### 方案二：Railway

1. Fork 本仓库
2. 访问 [Railway](https://railway.app/) 并连接 GitHub
3. 选择本仓库部署
4. 设置环境变量 `TUSHARE_TOKEN`
5. 部署完成后获得后端 URL

### 前端部署

前端自动部署到 GitHub Pages，只需更新 `frontend/.env.production` 中的 API URL：

```env
VITE_API_URL=https://your-backend-url.onrender.com
```

## 🔑 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `TUSHARE_TOKEN` | Tushare API Token | 是 |
| `DATABASE_URL` | PostgreSQL 连接字符串 | 否 |
| `ALLOWED_ORIGINS` | CORS 允许的域名 | 否 |

## 📊 数据源

| 数据源 | 类型 | 说明 |
|--------|------|------|
| [Tushare](https://tushare.pro/) | 免费/付费 | A股主要数据源 |
| [AkShare](https://akshare.xyz/) | 免费 | 开源财经数据接口 |
| [BaoStock](http://baostock.com/) | 免费 | 证券宝数据 |

## 🛠️ 技术栈

### 前端
- React 18 + TypeScript
- Ant Design 5
- ECharts 5
- AG Grid
- TailwindCSS

### 后端
- Python 3.11
- FastAPI
- Pandas / NumPy
- Tushare

## 📝 License

MIT License
