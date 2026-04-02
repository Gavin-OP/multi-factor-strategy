# 重构计划：分层架构

## 目标架构

```
src/
├── api/                    # 表现层 - 只负责 HTTP 请求/响应
│   ├── __init__.py
│   ├── main.py             # FastAPI 应用入口
│   ├── deps.py             # 依赖注入
│   └── routers/            # 路由/控制器
│       ├── __init__.py
│       ├── data.py         # 数据相关端点
│       ├── factors.py      # 因子分析端点
│       └── backtest.py     # 回测端点
│
├── services/               # 业务逻辑层 - 核心逻辑
│   ├── __init__.py
│   ├── data_service.py     # 数据服务
│   ├── factor_service.py   # 因子计算服务
│   └── backtest_service.py # 回测服务
│
├── repositories/           # 数据访问层 - 只负责数据获取
│   ├── __init__.py
│   ├── base.py             # 基础 Repository
│   ├── tushare_repo.py     # Tushare 数据源
│   ├── akshare_repo.py     # AkShare 数据源（备用）
│   └── cache_repo.py       # 缓存层
│
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── domain/             # 领域模型（业务实体）
│   │   ├── stock.py
│   │   ├── factor.py
│   │   └── portfolio.py
│   ├── dto/                # 数据传输对象（API 请求/响应）
│   │   ├── requests.py
│   │   └── responses.py
│   └── schemas.py          # Pydantic 模型
│
├── core/                   # 核心配置
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── exceptions.py       # 自定义异常
│   └── logging.py          # 日志配置
│
└── utils/                  # 工具函数
    ├── __init__.py
    └── helpers.py
```

## 层级职责

### 1. API 层（表现层）
```python
# api/routers/factors.py
@router.post("/test")
async def test_factor(
    request: FactorTestRequest,
    factor_service: FactorService = Depends(get_factor_service)
):
    """只负责：接收请求 → 调用服务 → 返回响应"""
    result = await factor_service.test_factor(request)
    return result
```

### 2. Service 层（业务逻辑）
```python
# services/factor_service.py
class FactorService:
    def __init__(self, stock_repo: StockRepository, factor_repo: FactorRepository):
        self.stock_repo = stock_repo
        self.factor_repo = factor_repo
    
    async def test_factor(self, request: FactorTestRequest) -> FactorTestResult:
        """核心业务逻辑"""
        # 1. 获取股票数据
        stocks = await self.stock_repo.get_stock_list()
        
        # 2. 计算因子
        factor_values = self._calculate_factor(stocks, request)
        
        # 3. 测试有效性
        test_result = self._test_effectiveness(factor_values, request)
        
        return test_result
```

### 3. Repository 层（数据访问）
```python
# repositories/tushare_repo.py
class TushareRepository(StockRepository):
    def __init__(self, token: str):
        self.pro = ts.pro_api(token)
    
    async def get_stock_list(self) -> List[Stock]:
        """只负责：从数据源获取数据"""
        df = self.pro.stock_basic(...)
        return [Stock(**row) for row in df.to_dict('records')]
    
    async def get_daily_prices(self, ts_code: str, ...) -> List[DailyPrice]:
        """只负责：获取价格数据"""
        df = self.pro.daily(ts_code=ts_code, ...)
        return [DailyPrice(**row) for row in df.to_dict('records')]
```

## 优势

| 方面 | 当前结构 | 新结构 |
|------|---------|--------|
| **可测试性** | 难以 mock 数据源 | ✅ 可以 mock Repository |
| **可维护性** | 逻辑分散 | ✅ 每层职责清晰 |
| **可扩展性** | 换数据源要改多处 | ✅ 只需新增 Repository |
| **依赖注入** | 无 | ✅ 使用 FastAPI Depends |
| **错误处理** | 分散 | ✅ 集中在 Service 层 |

## 示例：换数据源

当前：需要改 api/routes/data.py、api/routes/factors.py 等多处

新结构：
```python
# 只需改依赖注入
def get_stock_repo():
    if config.DATA_SOURCE == "tushare":
        return TushareRepository(config.TUSHARE_TOKEN)
    elif config.DATA_SOURCE == "akshare":
        return AkShareRepository()
    else:
        return MockRepository()
```

## 结论

你说得对，当前结构确实不够清晰。如果你想重构，我可以帮你按照正确的分层架构重新组织代码。
