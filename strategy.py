import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

commission_rate = 0.0001  # 0.01%
max_position_size = 1000  # shares
starting_capital = 100_000
max_daily_loss_pct = 0.02  # 2%
ohlcv_data_path = "./processed_Files/ohlcv.csv"
base_path = "./reports_and_graphs"

def strategy(symbol,starting_capital):
    report_storage_path = f"{base_path}/{symbol}"
    report_path = f"{report_storage_path}/report.txt"
    graph_path = f"{report_storage_path}/graph.png"
    output_dir = Path(report_storage_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ohlcv = pd.read_csv(ohlcv_data_path)
    ohlcv = ohlcv.loc[ohlcv["symbol"] == symbol].copy()
    
    cash = starting_capital
    daily_start_cash = starting_capital
    
    trades = []
    pnl_curve = []
    position = 0
    entry_price = 0


    for ind, row in ohlcv.iterrows():
        price = row["close"]
        ma20 = row["MA20"]
        vol20 = row["Vol20"]
        
        if pd.isna(ma20) or pd.isna(vol20):
            pnl_curve.append(cash)
            continue
        
        upper_band = ma20 + vol20
        lower_band = ma20 - vol20
        
        # Check max daily loss
        if (daily_start_cash - cash) / starting_capital >= max_daily_loss_pct:
            # Skip trading today
            pnl_curve.append(cash)
            continue
        
        # Entry rules with max position size
        if position == 0:
            if price < lower_band:
                position = min(max_position_size, 1)  # 1 unit or capped by max_position_size
                entry_price = price
                cash -= commission_rate * price * position
            elif price > upper_band:
                position = -min(max_position_size, 1)
                entry_price = price
                cash -= commission_rate * price * abs(position)
        
        # Exit rules
        elif position > 0 and price > ma20:
            trade_pnl = (price - entry_price) * position - commission_rate * price * abs(position)
            cash += trade_pnl
            trades.append(trade_pnl)
            position = 0
        elif position < 0 and price < ma20:
            trade_pnl = (entry_price - price) * abs(position) - commission_rate * price * abs(position)
            cash += trade_pnl
            trades.append(trade_pnl)
            position = 0
        
        pnl_curve.append(cash)
        
        # Reset daily start cash at new day (assume 'timeStamp' contains date info)
        if ind < len(ohlcv) - 1:
            next_day = pd.to_datetime(ohlcv["timeStamp"].iloc[ind + 1]).date()
            curr_day = pd.to_datetime(row["timeStamp"]).date()
            if next_day != curr_day:
                daily_start_cash = cash  # reset daily tracking

    # Convert to Series
    pnl_series = pd.Series(pnl_curve, index=ohlcv["timeStamp"])

    # Metrics
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t > 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    sharpe_ratio = (np.mean(trades) / np.std(trades)) * np.sqrt(252) if np.std(trades) != 0 else 0

    # print(f"Total trades: {total_trades}")
    # print(f"Winning trades: {winning_trades}")
    # print(f"Win rate: {win_rate:.2%}")
    # print(f"Sharpe ratio: {sharpe_ratio:.2f}")
    with open(report_path, "w") as f:
        f.write(f"Total trades: {total_trades}\n")
        f.write(f"Winning trades: {winning_trades}\n")
        f.write(f"Win rate: {win_rate:.2%}\n")
        f.write(f"Sharpe ratio: {sharpe_ratio:.2f}\n")
    # PnL curve
    plt.figure(figsize=(12,6))
    plt.plot(pnl_series.index, pnl_series.values, label="Original PnL")
    plt.title(f"PnL Curve with Risk Controls for {symbol}")
    plt.xlabel("Time")
    plt.ylabel("Cumulative PnL")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()  # prevent clipping
    plt.savefig(graph_path)
    plt.close()