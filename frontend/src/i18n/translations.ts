// Internationalization configuration
export type Language = 'zh' | 'en';

export const translations = {
  zh: {
    // Navigation
    nav: {
      title: '量化因子策略',
      database: '数据库架构',
      factors: '因子分析',
      backtest: '策略回测',
      dataSource: '数据源',
      marketData: '行情数据'
    },
    // Theme
    theme: {
      light: '浅色',
      dark: '深色',
      toggle: '切换主题'
    },
    // Language
    lang: {
      toggle: '切换语言',
      zh: '中文',
      en: 'English'
    },
    // Factor Analysis Page
    factor: {
      title: '因子有效性分析',
      subtitle: '专业级因子检测框架',
      selectFactor: '选择因子',
      factorType: '因子类型',
      momentum: '动量因子',
      value: '价值因子',
      quality: '质量因子',
      growth: '成长因子',
      volatilityFactor: '波动率因子',
      liquidity: '流动性因子',
      sentiment: '情绪因子',
      technical: '技术因子',
      
      config: '参数配置',
      startDate: '开始日期',
      endDate: '结束日期',
      quantiles: '分位数',
      forwardPeriod: '预测周期',
      neutralize: '中性化处理',
      industryNeutral: '行业中性',
      marketCapNeutral: '市值中性',
      
      runTest: '运行测试',
      testing: '测试中...',
      
      // Results
      results: '测试结果',
      icAnalysis: 'IC分析',
      icMean: 'IC均值',
      icStd: 'IC标准差',
      icir: 'ICIR',
      icTStat: 'IC t统计量',
      icPositive: 'IC正值比例',
      icSignificant: 'IC显著比例',
      
      regression: '回归分析',
      factorReturn: '因子收益率',
      factorTStat: 't统计量',
      rSquared: 'R²',
      
      quantileAnalysis: '分位数分析',
      quantile: '分位数',
      return: '收益率',
      sharpe: '夏普比率',
      volatility: '波动率',
      maxDrawdown: '最大回撤',
      hitRate: '胜率',
      
      spread: '多空价差',
      spreadReturn: '价差收益',
      spreadSharpe: '价差夏普',
      spreadTStat: '价差t统计量',
      spreadPValue: 'p值',
      
      monotonicity: '单调性',
      monotonicityScore: '单调性得分',
      
      icDecay: 'IC衰减分析',
      halfLife: '半衰期(期)',
      
      turnover: '换手率分析',
      avgTurnover: '平均换手率',
      rankAutocorr: '排名自相关',
      
      predictive: '预测能力',
      auc: 'AUC',
      f1Score: 'F1分数',
      precision: '精确率',
      recall: '召回率',
      
      stability: '稳定性分析',
      rollingIC: '滚动IC',
      bullIC: '牛市IC',
      bearIC: '熊市IC',
      oosIC: '样本外IC',
      
      risk: '风险指标',
      sortino: '索提诺比率',
      calmar: '卡尔马比率',
      var95: 'VaR(95%)',
      cvar95: 'CVaR(95%)',
      
      effectiveness: '有效性评估',
      grade: '评级',
      score: '得分',
      effective: '有效',
      notEffective: '无效',
      strengths: '优势',
      weaknesses: '不足',
      
      charts: {
        icTs: 'IC时间序列',
        quantileReturn: '分位数收益',
        icDecay: 'IC衰减曲线',
        cumulative: '累计收益'
      }
    },
    // Backtest Page
    backtest: {
      title: '策略回测',
      subtitle: '多因子组合策略回测',
      
      strategy: '策略配置',
      selectFactors: '选择因子',
      weightMethod: '权重方法',
      equal: '等权',
      icWeighted: 'IC加权',
      icirWeighted: 'ICIR加权',
      maxSharpe: '最大夏普',
      minVariance: '最小方差',
      
      rebalance: '调仓配置',
      frequency: '调仓频率',
      daily: '每日',
      weekly: '每周',
      monthly: '每月',
      quarterly: '每季',
      
      positionSize: '持仓配置',
      topN: '持仓数量',
      maxWeight: '最大权重',
      minWeight: '最小权重',
      
      cost: '交易成本',
      commission: '手续费',
      slippage: '滑点',
      
      run: '运行回测',
      running: '回测中...',
      
      // Results
      performance: '业绩表现',
      totalReturn: '总收益',
      annualReturn: '年化收益',
      excessReturn: '超额收益',
      annualVolatility: '年化波动率',
      sharpeRatio: '夏普比率',
      informationRatio: '信息比率',
      maxDrawdown: '最大回撤',
      winRate: '胜率',
      profitLossRatio: '盈亏比',
      
      monthlyReturns: '月度收益',
      yearlyReturns: '年度收益',
      
      positions: '持仓分析',
      avgHoldingPeriod: '平均持仓周期',
      turnoverRate: '换手率',
      
      risk: '风险分析',
      beta: 'Beta',
      alpha: 'Alpha',
      trackingError: '跟踪误差',
      downsideRisk: '下行风险',
      
      charts: {
        nav: '净值曲线',
        drawdown: '回撤曲线',
        monthlyHeatmap: '月度收益热力图',
        exposure: '因子暴露'
      }
    },
    // Market Data Page
    market: {
      title: '行情数据',
      subtitle: '指数与股票行情展示',
      indexList: '指数列表',
      selectIndex: '选择指数',
      searchStock: '搜索股票',
      stockSearch: '股票搜索',
      stockKline: '股票K线',
      enterCode: '输入代码或名称',
      daily: '日线',
      weekly: '周线',
      monthly: '月线',
      tradeDate: '交易日期',
      open: '开盘',
      high: '最高',
      low: '最低',
      close: '收盘',
      volume: '成交量',
      klineChart: 'K线图',
      indexKline: '指数K线',
      noResults: '未找到结果',
      loading: '加载中...',
      dataSource: '数据来源'
    },
    // Factor Code
    factorCode: {
      title: '因子代码',
      viewCode: '查看代码',
      description: '描述',
      parameters: '参数',
      references: '参考文献',
      copyCode: '复制代码',
      copied: '已复制'
    },
    // Common
    common: {
      loading: '加载中...',
      noData: '暂无数据',
      confirm: '确认',
      cancel: '取消',
      reset: '重置',
      export: '导出',
      refresh: '刷新'
    },
    // Footer
    footer: {
      text: '量化因子策略框架',
      freeDb: '免费数据库',
      freeData: '免费数据源'
    }
  },
  en: {
    // Navigation
    nav: {
      title: 'Quant Factor Strategy',
      database: 'Database',
      factors: 'Factor Analysis',
      backtest: 'Backtest',
      dataSource: 'Data Source',
      marketData: 'Market Data'
    },
    // Theme
    theme: {
      light: 'Light',
      dark: 'Dark',
      toggle: 'Toggle Theme'
    },
    // Language
    lang: {
      toggle: 'Toggle Language',
      zh: '中文',
      en: 'English'
    },
    // Factor Analysis Page
    factor: {
      title: 'Factor Effectiveness Analysis',
      subtitle: 'Professional Factor Testing Framework',
      selectFactor: 'Select Factor',
      factorType: 'Factor Type',
      momentum: 'Momentum',
      value: 'Value',
      quality: 'Quality',
      growth: 'Growth',
      volatilityFactor: 'Volatility',
      liquidity: 'Liquidity',
      sentiment: 'Sentiment',
      technical: 'Technical',
      
      config: 'Configuration',
      startDate: 'Start Date',
      endDate: 'End Date',
      quantiles: 'Quantiles',
      forwardPeriod: 'Forward Period',
      neutralize: 'Neutralization',
      industryNeutral: 'Industry Neutral',
      marketCapNeutral: 'Market Cap Neutral',
      
      runTest: 'Run Test',
      testing: 'Testing...',
      
      // Results
      results: 'Results',
      icAnalysis: 'IC Analysis',
      icMean: 'IC Mean',
      icStd: 'IC Std',
      icir: 'ICIR',
      icTStat: 'IC t-Stat',
      icPositive: 'IC Positive %',
      icSignificant: 'IC Significant %',
      
      regression: 'Regression',
      factorReturn: 'Factor Return',
      factorTStat: 't-Statistic',
      rSquared: 'R²',
      
      quantileAnalysis: 'Quantile Analysis',
      quantile: 'Quantile',
      return: 'Return',
      sharpe: 'Sharpe',
      volatility: 'Volatility',
      maxDrawdown: 'Max Drawdown',
      hitRate: 'Hit Rate',
      
      spread: 'Spread Analysis',
      spreadReturn: 'Spread Return',
      spreadSharpe: 'Spread Sharpe',
      spreadTStat: 'Spread t-Stat',
      spreadPValue: 'p-Value',
      
      monotonicity: 'Monotonicity',
      monotonicityScore: 'Monotonicity Score',
      
      icDecay: 'IC Decay Analysis',
      halfLife: 'Half-Life (periods)',
      
      turnover: 'Turnover Analysis',
      avgTurnover: 'Avg Turnover',
      rankAutocorr: 'Rank Autocorr',
      
      predictive: 'Predictive Power',
      auc: 'AUC',
      f1Score: 'F1 Score',
      precision: 'Precision',
      recall: 'Recall',
      
      stability: 'Stability Analysis',
      rollingIC: 'Rolling IC',
      bullIC: 'Bull Market IC',
      bearIC: 'Bear Market IC',
      oosIC: 'Out-of-Sample IC',
      
      risk: 'Risk Metrics',
      sortino: 'Sortino Ratio',
      calmar: 'Calmar Ratio',
      var95: 'VaR(95%)',
      cvar95: 'CVaR(95%)',
      
      effectiveness: 'Effectiveness',
      grade: 'Grade',
      score: 'Score',
      effective: 'Effective',
      notEffective: 'Not Effective',
      strengths: 'Strengths',
      weaknesses: 'Weaknesses',
      
      charts: {
        icTs: 'IC Time Series',
        quantileReturn: 'Quantile Returns',
        icDecay: 'IC Decay Curve',
        cumulative: 'Cumulative Returns'
      }
    },
    // Backtest Page
    backtest: {
      title: 'Strategy Backtest',
      subtitle: 'Multi-Factor Portfolio Backtest',
      
      strategy: 'Strategy Config',
      selectFactors: 'Select Factors',
      weightMethod: 'Weighting Method',
      equal: 'Equal Weight',
      icWeighted: 'IC Weighted',
      icirWeighted: 'ICIR Weighted',
      maxSharpe: 'Max Sharpe',
      minVariance: 'Min Variance',
      
      rebalance: 'Rebalancing',
      frequency: 'Frequency',
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      
      positionSize: 'Position Sizing',
      topN: 'Top N Holdings',
      maxWeight: 'Max Weight',
      minWeight: 'Min Weight',
      
      cost: 'Transaction Costs',
      commission: 'Commission',
      slippage: 'Slippage',
      
      run: 'Run Backtest',
      running: 'Running...',
      
      // Results
      performance: 'Performance',
      totalReturn: 'Total Return',
      annualReturn: 'Annual Return',
      excessReturn: 'Excess Return',
      annualVolatility: 'Annual Volatility',
      sharpeRatio: 'Sharpe Ratio',
      informationRatio: 'Information Ratio',
      maxDrawdown: 'Max Drawdown',
      winRate: 'Win Rate',
      profitLossRatio: 'Profit/Loss Ratio',
      
      monthlyReturns: 'Monthly Returns',
      yearlyReturns: 'Yearly Returns',
      
      positions: 'Position Analysis',
      avgHoldingPeriod: 'Avg Holding Period',
      turnoverRate: 'Turnover Rate',
      
      risk: 'Risk Analysis',
      beta: 'Beta',
      alpha: 'Alpha',
      trackingError: 'Tracking Error',
      downsideRisk: 'Downside Risk',
      
      charts: {
        nav: 'NAV Curve',
        drawdown: 'Drawdown Curve',
        monthlyHeatmap: 'Monthly Returns Heatmap',
        exposure: 'Factor Exposure'
      }
    },
    // Market Data Page
    market: {
      title: 'Market Data',
      subtitle: 'Index and Stock Quotes',
      indexList: 'Index List',
      selectIndex: 'Select Index',
      searchStock: 'Search Stock',
      stockSearch: 'Stock Search',
      stockKline: 'Stock K-Line',
      enterCode: 'Enter code or name',
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      tradeDate: 'Trade Date',
      open: 'Open',
      high: 'High',
      low: 'Low',
      close: 'Close',
      volume: 'Volume',
      klineChart: 'K-Line Chart',
      indexKline: 'Index K-Line',
      noResults: 'No results found',
      loading: 'Loading...',
      dataSource: 'Data Source'
    },
    // Factor Code
    factorCode: {
      title: 'Factor Code',
      viewCode: 'View Code',
      description: 'Description',
      parameters: 'Parameters',
      references: 'References',
      copyCode: 'Copy Code',
      copied: 'Copied'
    },
    // Common
    common: {
      loading: 'Loading...',
      noData: 'No Data',
      confirm: 'Confirm',
      cancel: 'Cancel',
      reset: 'Reset',
      export: 'Export',
      refresh: 'Refresh'
    },
    // Footer
    footer: {
      text: 'Quant Factor Strategy Framework',
      freeDb: 'Free Database',
      freeData: 'Free Data Source'
    }
  }
};

export type TranslationKey = keyof typeof translations.zh;
