Quantitative Data Engineer – Take-Home Test

This repository implements a tick-data processing, trading strategy backtest, and risk & stress testing framework for the Quantitative Data Engineer – Trading Systems take-home assignment.

The system is organized into three clear processing stages, each producing artifacts consumed by the next stage.

--------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------
```

├── tick_data/                  (Input tick-level CSV data)
│   └── sample_tick_data.csv
│
├── processed_Files/            (Stage 1 output – market data processing)
│   └── ohlcv.csv
│
├── reports_and_graphs/         (Stage 2 output – strategy backtest reports)
│   └── <symbol>/
│       ├── report.txt
│       └── graph.png
│
├── stressrun_reports/          (Stage 3 output – stress test results)
│   └── <symbol>/
│       ├── report.txt
│       └── graph.png
│
├── src/                        (Source code)
│   ├── run.py                  Entry point (Stage 1 → Stage 3)
│   ├── backtest.py             Strategy implementation
│   ├── stressrun.py            Stress testing logic
│
├── requirements.txt            Python dependencies
├── check_requirements.sh       Install required libraries
├── run.sh                      Pipeline entry point
└── README.txt                  This file

```
--------------------------------------------------
QUICK START
--------------------------------------------------

1. Install dependencies

chmod +x check_requirements.sh
./check_requirements.sh

2. Run the full pipeline

chmod +x run.sh
./run.sh

This runs:
- Market data processing
- Strategy backtesting
- Risk controls
- Stress testing
- Report and graph generation

--------------------------------------------------
PART 1: MARKET DATA PROCESSING
--------------------------------------------------

Input:
- Tick-level CSV data from tick_data/

Processing:
1. Read tick data
2. Resample into 1-minute OHLCV bars
3. Compute rolling indicators:
   - 20-period moving average
   - 20-period volatility (standard deviation)

Output:
processed_Files/ohlcv.csv

--------------------------------------------------
PART 2: TRADING STRATEGY BACKTEST
--------------------------------------------------

Strategy: Mean Reversion

Buy condition:
price < (20-period MA − 1 standard deviation)

Sell condition:
price > (20-period MA + 1 standard deviation)

Constraints:
- Flat at market close
- Commission: 0.01% per trade

Outputs (per symbol):
- PnL curve
- Win rate
- Sharpe ratio

Saved to:
reports_and_graphs/<symbol>/

--------------------------------------------------
PART 3: RISK & STRESS ANALYSIS
--------------------------------------------------

Risk Controls:
- Maximum position size: 1,000 shares per symbol
- Maximum daily loss: 2% of starting capital

Stress Test:
- Apply a −5% shock to all prices in a single trading day
- Recompute PnL under stressed conditions
- Found worst Preformance, Agressively loss making strategy
Outputs:
stressrun_reports/<symbol>/

--------------------------------------------------
METRICS
--------------------------------------------------

- Total trades
- Winning trades
- Win rate
- Sharpe ratio (annualized)
- Cumulative PnL
- Stress-scenario drawdown

--------------------------------------------------
AI USAGE DISCLOSURE
--------------------------------------------------

AI tools (ChatGPT) were used to:
- Validate trading logic
- Debug Pandas indexing and copy warnings
- Improve code safety and structure
- Assist with documentation

Accepted:
    - Error-handling patterns

Rejected:
- Over-engineered abstractions
- Excessive vectorization that reduced clarity

--------------------------------------------------
DESIGN & PERFORMANCE CONSIDERATIONS
--------------------------------------------------

- Single-pass processing where possible
- Symbol-level isolation for scalability
- File-based artifacts between stages

--------------------------------------------------
PRODUCTION SCALING (NEXT STEPS)
--------------------------------------------------
Not much aware for scaling python written strategies

--------------------------------------------------
REQUIREMENTS
--------------------------------------------------

pandas >= 1.3
numpy >= 1.21
matplotlib >= 3.4

--------------------------------------------------
AUTHOR
--------------------------------------------------

Tarun Pal
