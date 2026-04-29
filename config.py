# DO NOT MODIFY — this is the evaluation contract

# ═══════════════════════════════════════════════════════
# Ticker 分层架构
# ═══════════════════════════════════════════════════════

# 开发集：指数 + 大盘稳定股（低波动，策略容易收敛）
# agent 日常循环只跑这组，快速迭代
DEV_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "JPM", "WMT"]

# 验证集 1：AI/科技（高相关性，测板块内泛化）
VAL_AI = ["NVDA", "AMD", "AVGO", "TSM", "PLTR", "CRM", "CRWD"]

# 验证集 2：跨板块（低相关性，测真正泛化）
VAL_CROSS = ["TSLA", "XOM", "CAT", "LLY", "UNH", "META", "AMZN", "V"]

# 所有 ticker（prepare.py 下载用）
ALL_TICKERS = sorted(set(DEV_TICKERS + VAL_AI + VAL_CROSS))

# ═══════════════════════════════════════════════════════
# 回测参数
# ═══════════════════════════════════════════════════════
TIMERANGE_START = "2019-01-01"
TIMERANGE_END = "2025-12-31"
TIMEFRAME = "1d"
CASH = 100_000
COMMISSION = 0.001              # 0.1% round-trip
TRADE_ON_CLOSE = True
EXCLUSIVE_ORDERS = True
