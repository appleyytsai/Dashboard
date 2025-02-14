import requests
import pandas as pd
import streamlit as st
import numpy as np
import os

# Financial Modeling Prep API Key
API_KEY = "KZZYxCMVitIeMucmW4UQm9xzUI2A4EXm"

# 七巨頭的股票代號
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]

# API URLs
EV_URL = "https://financialmodelingprep.com/api/v3/enterprise-values/{}?apikey={}"
INCOME_URL = "https://financialmodelingprep.com/api/v3/income-statement/{}?limit=5&apikey={}"  # 取5年數據

# 設置資料存儲文件夾
DATA_DIR = "ev_ebitda_data"
os.makedirs(DATA_DIR, exist_ok=True)

def calculate_ratios(ticker):
    ev_file = os.path.join(DATA_DIR, f"{ticker}_ev.csv")
    ebitda_file = os.path.join(DATA_DIR, f"{ticker}_ebitda.csv")
    ratio_file = os.path.join(DATA_DIR, f"{ticker}_ev_ebitda_ratio.csv")
    
    # 讀取歷史數據（如果存在）
    if os.path.exists(ratio_file):
        past_data = pd.read_csv(ratio_file)
    else:
        past_data = pd.DataFrame()
    
    if not os.path.exists(ev_file) or not os.path.exists(ebitda_file):
        return None
    
    # 讀取 EV 和 EBITDA 數據
    ev_data = pd.read_csv(ev_file)
    ebitda_data = pd.read_csv(ebitda_file)
    
    # 合併 EV 和 EBITDA 數據
    merged = pd.merge(ev_data, ebitda_data, on="Date", how="inner")
    merged.insert(0, "Ticker", ticker)
    merged["Current EV/EBITDA Ratio"] = merged["EnterpriseValue"].astype(float) / merged["EBITDA_TTM"].astype(float)
    
    # 合併歷史數據，確保過去 5 年的完整性
    full_data = pd.concat([past_data, merged], ignore_index=True).drop_duplicates()
    full_data.sort_values(by="Date", ascending=False, inplace=True)
    
    # 取過去 5 年的數據計算統計數值
    past_5_years = full_data.head(20)["Current EV/EBITDA Ratio"].dropna()
    median = past_5_years.median() if not past_5_years.empty else None
    high = past_5_years.max() if not past_5_years.empty else None
    low = past_5_years.min() if not past_5_years.empty else None
    
    # 根據歷史數據比較當前 EV/EBITDA 比率
    def categorize_ratio(value):
        if value >= high:
            return "High"
        elif value <= low:
            return "Low"
        else:
            return "Medium"
    
    merged["EV/EBITDA Compared to 5Y"] = merged["Current EV/EBITDA Ratio"].apply(categorize_ratio)
    merged["5Y Median"] = median
    merged["5Y High"] = high
    merged["5Y Low"] = low
    
    merged.fillna("N/A", inplace=True)
    merged.to_csv(ratio_file, index=False)
    return merged

# 讀取或獲取所有原始數據
df_ratios = pd.concat([calculate_ratios(ticker) for ticker in TICKERS if calculate_ratios(ticker) is not None], ignore_index=True)

# 只保留最新的數據
df_latest = df_ratios.sort_values(by="Date", ascending=False).groupby("Ticker").first().reset_index()

# 重新設定索引從 1 開始
df_latest.index = np.arange(1, len(df_latest) + 1)

# Streamlit 應用
st.title("Big 7 EV/EBITDA Ratio Analysis Dashboard")

# 顯示最新的數據
table_columns = ["Ticker", "Current EV/EBITDA Ratio", "EV/EBITDA Compared to 5Y", "5Y Median", "5Y High", "5Y Low"]
st.dataframe(df_latest[table_columns])

# 每日更新數據
st.write("Data updates daily.")
