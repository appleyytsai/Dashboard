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
# DATA_DIR = "ev_ebitda_data"
# os.makedirs(DATA_DIR, exist_ok=True)

def calculate_ratios(ticker):
    # 直接從 API 獲取數據
    ev_response = requests.get(EV_URL.format(ticker, API_KEY)).json()
    ebitda_response = requests.get(INCOME_URL.format(ticker, API_KEY)).json()
    
    if not isinstance(ev_response, list) or not isinstance(ebitda_response, list):
        print(f"API Error for {ticker}: EV or EBITDA data not available")
        return None
    
    ev_data = pd.DataFrame({
        "Date": [ev["date"] for ev in ev_response],
        "EnterpriseValue": [ev["enterpriseValue"] for ev in ev_response]
    })
    
    ebitda_data = pd.DataFrame({
        "Date": [inc["date"] for inc in ebitda_response],
        "EBITDA_TTM": [inc["ebitda"] for inc in ebitda_response]
    })
    
    # 合併 EV 和 EBITDA 數據
    merged = pd.merge(ev_data, ebitda_data, on="Date", how="inner")
    merged.insert(0, "Ticker", ticker)
    merged["Current EV/EBITDA Ratio"] = merged["EnterpriseValue"].astype(float) / merged["EBITDA_TTM"].astype(float)
    
    # 取過去 5 年的數據計算統計數值
    past_5_years = merged.head(20)["Current EV/EBITDA Ratio"].dropna()
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
    
    # 註解掉存儲數據的部分
    # merged.to_csv(os.path.join(DATA_DIR, f"{ticker}_ev_ebitda_ratio.csv"), index=False)
    
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
