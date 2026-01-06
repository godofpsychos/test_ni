import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
# import copy



commission_rate = 0.0001  # 0.01%
max_position_size = 1000  # shares
starting_capital = 100_000
max_daily_loss_pct = 0.02  # 2%
ohlcv_data_path = "./processed_Files/ohlcv.csv"
base_path = "./stressrun_reports"

def stress_run_strategy(symbol,starting_capital):

    report_storage_path = f"{base_path}/{symbol}"
    report_path = f"{report_storage_path}/report.txt"
    graph_path = f"{report_storage_path}/graph.png"
    output_dir = Path(report_storage_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    ohlcv = pd.read_csv(ohlcv_data_path)
    ohlcv_shock = ohlcv.loc[ohlcv["symbol"] == symbol].copy()
    ohlcv_shock.loc[:, "close"] *= 0.95


    # Re-run backtest under stress
    position = 0
    entry_price = 0
    cash_stress = starting_capital
    pnl_curve_stress = []

    for ind, row in ohlcv_shock.iterrows():
        price = row["close"]
        ma20 = row["MA20"]
        vol20 = row["Vol20"]
        
        if pd.isna(ma20) or pd.isna(vol20):
            pnl_curve_stress.append(cash_stress)
            continue
        
        upper_band = ma20 + vol20
        lower_band = ma20 - vol20
        
        # Max daily loss
        if (starting_capital - cash_stress) / starting_capital >= max_daily_loss_pct:
            pnl_curve_stress.append(cash_stress)
            continue
        
        # Entry
        if position == 0:
            if price < lower_band:
                position = min(max_position_size, 1)
                entry_price = price
                cash_stress -= commission_rate * price * position
            elif price > upper_band:
                position = -min(max_position_size, 1)
                entry_price = price
                cash_stress -= commission_rate * price * abs(position)
        
        # Exit
        elif position > 0 and price > ma20:
            trade_pnl = (price - entry_price) * position - commission_rate * price * abs(position)
            cash_stress += trade_pnl
            position = 0
        elif position < 0 and price < ma20:
            trade_pnl = (entry_price - price) * abs(position) - commission_rate * price * abs(position)
            cash_stress += trade_pnl
            position = 0
        
        pnl_curve_stress.append(cash_stress)

    pnl_series_stress = pd.Series(pnl_curve_stress, index=ohlcv_shock["timeStamp"])

    # Plot stress test
    plt.figure(figsize=(12,6))
    # plt.plot(pnl_series.index, pnl_series.values, label="Original PnL")
    plt.plot(pnl_series_stress.index, pnl_series_stress.values, label="Stress Test PnL (-5% shock)")
    plt.title(f"PnL Curve Stress Test for {symbol}")
    plt.xlabel("Time")
    plt.ylabel("Cumulative PnL")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()  # prevent clipping
    plt.savefig(graph_path)
    plt.close()
