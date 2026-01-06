import pandas as pd
from pathlib import Path
from strategy import strategy 
from stressrun import stress_run_strategy

tickDataPath = Path("./tick_data")
ohlcv_data_path = "./processed_Files/ohlcv.csv"
dfs = []
starting_capital = 10000000

for csv_file in tickDataPath.glob("*.csv"):
    df = pd.read_csv(csv_file)
    dfs.append(df)
    print(f"Processing {csv_file.name}")

df = pd.concat(dfs, ignore_index=True)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["time_hhmm"] = df["timestamp"].dt.strftime("%H%M")

bars = []
map_dict = {}
bar = {}
key = (0, 0)

# This will store the last 20 closes per symbol for rolling calculation
rolling_closes = {}

for ind, row in df.iterrows():
    key = (row.symbol, row.time_hhmm)
    
    if key not in map_dict:
        symbol, time = key
        if len(bar) > 0:
            # Compute rolling indicators before appending
            closes = rolling_closes.get(symbol, [])
            if len(closes) >= 20:
                ma20 = sum(closes[-20:]) / 20
                vol20 = pd.Series(closes[-20:]).std()
            else:
                ma20 = None
                vol20 = None

            bars.append([
                symbol,
                time,
                bar["open"],
                bar["high"],
                bar["low"],
                bar["close"],
                bar["volume"],
                ma20,
                vol20
            ])
        
        # Start a new bar
        bar["open"] = row.price
        bar["high"] = row.price
        bar["low"] = row.price
        bar["close"] = row.price
        bar["volume"] = row.volume

        # Initialize rolling closes if symbol not present
        if row.symbol not in rolling_closes:
            rolling_closes[row.symbol] = []
        
        rolling_closes[row.symbol].append(row.price)

    else:
        # Update existing bar
        bar["high"] = max(row.price, bar["high"])
        bar["low"] = min(row.price, bar["low"])
        bar["close"] = row.price
        bar["volume"] += row.volume

        # Update rolling closes
        rolling_closes[row.symbol].append(row.price)

# Add the last bar
if len(bar) > 0:
    symbol, time = key
    closes = rolling_closes.get(symbol, [])
    if len(closes) >= 20:
        ma20 = sum(closes[-20:]) / 20
        vol20 = pd.Series(closes[-20:]).std()
    else:
        ma20 = None
        vol20 = None

    bars.append([
        symbol,
        time,
        bar["open"],
        bar["high"],
        bar["low"],
        bar["close"],
        bar["volume"],
        ma20,
        vol20
    ])

ohlcv = pd.DataFrame(
    bars,
    columns=["symbol", "timeStamp", "open", "high", "low", "close", "volume", "MA20", "Vol20"]
)

print(ohlcv)
ohlcv.to_csv("./processed_Files/ohlcv.csv")

symbol_list = ohlcv["symbol"].unique().tolist()

for symbol in symbol_list:
    strategy(symbol,starting_capital)
    
for symbol in symbol_list:
    stress_run_strategy(symbol,starting_capital)