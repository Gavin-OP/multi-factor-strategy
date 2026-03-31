# Quant Factor Strategy Framework

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个专业的量化因子策略框架，按照百亿量化私募标准设计和实现。

## 📋 项目概述

本项目是一个完整的量化因子研究和策略实现框架，包含从数据处理、因子挖掘、信号生成、组合构建到回测评估的全流程实现。

### 核心特性

- **📐 架构设计**: 分层架构，Separation of Concerns，易于维护和扩展
- **📊 因子库**: 实现 14 个量价因子（参考 WorldQuant 101）
- **🔍 因子测试**: IC/IR 分析、分组测试、单调性检验、换手率分析
- **⚙️ 信号生成**: 多因子融合、信号标准化、股票筛选
- **💼 组合构建**: 多种加权方式、再平衡逻辑、持仓管理
- **📈 回测引擎**: Backtrader 事件驱动回测
- **📉 风险管理**: VaR/CVaR、最大回撤、风险预算
- **📊 可视化**: React 仪表盘 + QuantStats 报告

## 🗂️ 项目结构

```
quant_factor_strategy/
├── config/                     # 配置文件
│   └── config.ini             # 主配置文件
├── src/                       # 源代码
│   ├── data/                  # 数据层
│   │   ├── fetcher.py        # 数据获取 (Akshare/Tushare/yfinance)
│   │   ├── storage.py        # 数据存储 (SQLAlchemy ORM)
│   │   ├── cache.py          # 数据缓存
│   │   └── manager.py        # 数据管理器
│   ├── factors/              # 因子层
│   │   ├── base.py           # 因子基类
│   │   ├── factor_library.py # 因子库 (14 个量价因子)
│   │   └── engine.py         # 因子引擎 (计算/测试/入库)
│   ├── signals/              # 信号层
│   │   ├── combiner.py       # 因子融合 (ICIR/MaxSharpe/PCA)
│   │   ├── selector.py       # 股票筛选
│   │   └── generator.py      # 信号生成器
│   ├── portfolio/            # 组合层
│   │   ├── weighting.py      # 权重分配 (6 种加权方式)
│   │   ├── constructor.py    # 组合构建
│   │   └── rebalancer.py     # 再平衡逻辑
│   ├── backtest/             # 回测层
│   │   ├── engine.py         # Backtrader 回测引擎
│   │   └── strategy.py       # 因子策略实现
│   ├── risk/                 # 风险层
│   │   ├── manager.py        # 风险管理 (VaR/CVaR)
│   │   ├── analytics.py      # 风险分析 (QuantStats)
│   │   └── reporter.py       # 报告生成
│   └── utils/                # 工具函数
├── scripts/                  # 运行脚本
│   └── run_pipeline.py       # 主流程脚本
├── notebooks/                # Jupyter 研究
│   └── factor_research.ipynb # 因子研究笔记本
├── docker/                   # Docker 配置
│   ├── Dockerfile
│   └── docker-compose.yml    # 包含 PostgreSQL + Redis
├── frontend/                 # React 可视化
│   └── src/
│       ├── App.tsx           # 仪表盘主界面
│       └── main.tsx
├── outputs/                  # 输出目录
├── requirements.txt          # Python 依赖
└── README.md
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行主流程

```bash
python scripts/run_pipeline.py
```

这将执行完整的量化流程：
1. 加载市场数据
2. 计算并测试因子
3. 生成交易信号
4. 构建投资组合
5. 执行策略回测
6. 风险分析和报告

### 使用 Docker

```bash
cd docker
docker-compose up -d
```

## 📊 因子库

项目实现了 14 个量价因子，参考 WorldQuant 101：

| 因子名称 | 类型 | 描述 |
|---------|------|------|
| Factor001 | Volume-Price | 价格-成交量相关性 |
| Factor002 | Momentum | 日内动量变化 |
| Factor003 | Volume-Price | 成交量排名求和 |
| Factor004 | Volume-Price | 成交量振荡器 |
| Factor005 | Momentum | VWAP 价格动量 |
| Factor006 | Volume-Price | 开盘价-成交量相关性 |
| Factor007 | Volume-Price | 成交量突破 |
| Factor008 | Momentum | 收盘价动量 |
| Factor009 | Volume-Price | 成交量比率 |
| Factor010 | Volume-Price | 收益相关性 |
| VolumePriceMomentum | Volume-Price | 量价动量组合 |
| Momentum | Momentum | 风险调整动量 |
| Volatility | Risk | 低波动率因子 |
| Liquidity | Liquidity | Amihud 非流动性因子 |

### 因子测试

每个因子都经过严格的测试：
- **IC 分析**: Spearman/Pearson 相关系数
- **IR 计算**: IC 均值 / IC 标准差
- **分组测试**: 5 分位收益率分析
- **单调性检验**: 组间收益率单调性
- **换手率分析**: Top 股票变化频率

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│                   (scripts / notebooks)                  │
├─────────────────────────────────────────────────────────┤
│                      Risk Layer                          │
│              (RiskManager, Analytics, Reporter)          │
├─────────────────────────────────────────────────────────┤
│                   Backtest Layer                         │
│                 (BacktestEngine, Strategy)               │
├─────────────────────────────────────────────────────────┤
│                   Portfolio Layer                        │
│         (WeightAllocator, Constructor, Rebalancer)       │
├─────────────────────────────────────────────────────────┤
│                    Signal Layer                          │
│           (FactorCombiner, StockSelector, Generator)     │
├─────────────────────────────────────────────────────────┤
│                    Factor Layer                          │
│          (FactorBase, FactorLibrary, FactorEngine)       │
├─────────────────────────────────────────────────────────┤
│                     Data Layer                           │
│           (DataFetcher, DataStorage, DataCache)          │
└─────────────────────────────────────────────────────────┘
```

### 设计原则

1. **Separation of Concerns**: 每层独立负责特定功能
2. **依赖注入**: 组件通过构造函数注入依赖
3. **接口抽象**: 使用抽象基类定义接口
4. **配置外部化**: 所有参数通过配置文件管理
5. **可测试性**: 每个模块可独立测试

## 📈 组合构建

### 加权方式

支持 6 种加权方式：
1. **Equal Weight**: 等权重
2. **Market Cap Weight**: 市值加权
3. **Signal Weight**: 信号强度加权
4. **Risk Parity**: 风险平价（逆波动率）
5. **Mean Variance**: 均值方差优化
6. **Smart Beta**: 因子倾斜加权

### 再平衡

- 时间触发：固定周期（日/周/月）
- 漂移触发：权重偏离阈值
- 信号触发：信号显著变化
- 换手约束：控制交易成本

## 📉 风险管理

### 风险指标

- **VaR/CVaR**: 历史/参数/Cornish-Fisher 方法
- **最大回撤**: 持续时间和恢复期
- **夏普比率**: 风险调整收益
- **索提诺比率**: 下行风险调整
- **信息比率**: 超额收益/跟踪误差
- **Beta/相关性**: 系统性风险暴露

### 风险控制

- 单一持仓限制
- 行业集中度限制
- 最大回撤预警
- 动态风险预算

## 🖥️ 可视化

### React 仪表盘

```bash
cd frontend
npm install
npm run dev
```

功能包括：
- 净值曲线图
- 月度收益柱状图
- 因子性能表格
- 持仓权重分布
- 风险指标概览

### QuantStats 报告

自动生成 HTML 报告，包含：
- 完整收益统计
- 风险指标分析
- 回撤分析
- 月度/年度收益

## 📝 数据源

支持多种数据源：

| 数据源 | 市场 | 特点 |
|--------|------|------|
| Akshare | A股 | 免费、开源 |
| Tushare | A股 | 专业数据 |
| yfinance | 全球 | 美股/港股 |
| Mock | - | 测试用模拟数据 |

### PostgreSQL 数据库

配置 `config/config.ini`:

```ini
[database]
driver = postgresql
host = localhost
port = 5432
database = quant_factor
username = quant
password = quant123
```

## 📋 GitHub 上传说明

**可以上传到 GitHub！** ✅

本项目：
- ✅ 使用 MIT 开源许可证
- ✅ 不包含任何敏感数据或密钥
- ✅ 不包含真实的交易代码或策略细节
- ✅ 仅使用公开的市场数据接口
- ✅ 教育和研究目的

建议上传前：
1. 检查是否有误提交的配置文件（如 API Token）
2. 确保 `.gitignore` 配置正确
3. 添加 LICENSE 文件

## 📚 参考资料

- [WorldQuant 101 Alpha Factors](https://arxiv.org/abs/1601.00991)
- [QuantStats Documentation](https://github.com/ranaroussi/quantstats)
- [Backtrader Documentation](https://www.backtrader.com/)
- [Barra Risk Model](https://www.msci.com/barra-models)

## 📄 许可证

MIT License - 可自由使用、修改和分发

---

**免责声明**: 本项目仅供学习和研究使用，不构成任何投资建议。使用本代码进行实际交易的风险由使用者自行承担。

