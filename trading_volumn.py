import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Function to fetch Alibaba's historical trading volume
def get_alibaba_trading_volume():
    stock = yf.Ticker("9988.HK")  # Alibaba (HK Stock Exchange)
    df = stock.history(period="3mo")  # Fetch last 3 months of data

    # Keep relevant columns & sort by latest date
    if "Volume" in df.columns:
        df = df[["Volume"]].reset_index()
        df.rename(columns={"Volume": "Trading Volume"}, inplace=True)
    else:
        st.error("Error: 'Volume' column not found in Yahoo Finance data.")
        return pd.DataFrame()  # Return empty DataFrame if error occurs

    # **Remove rows where trading volume is 0**
    df = df[df["Trading Volume"] > 0]

    # **Calculate 5-Day Moving Average (MA)**
    df["5-Day MA"] = df["Trading Volume"].rolling(window=5).mean()

    # Sort newest to oldest
    df = df.sort_values("Date", ascending=False)

    return df

# Fetch data
df = get_alibaba_trading_volume()

if not df.empty:  # Proceed only if data is available
    # Streamlit UI
    st.title("📊 Alibaba (9988.HK) Trading Volume Tracker")

    # Plot bar chart with 5-Day MA trendline
    st.write("### 📊 Trading Volume Chart with 5-Day MA & Key Event")

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="white")

    # Plot daily volume bars
    ax.bar(df["Date"], df["Trading Volume"], color="#4A90E2", alpha=0.8, label="Daily Volume")

    # Plot 5-Day Moving Average trendline
    ax.plot(df["Date"], df["5-Day MA"], color="#E94E77", marker="o", linestyle="-", linewidth=2, markersize=5, label="5-Day MA")

    # **Add vertical line for January 20 event**
    event_date = pd.Timestamp("2025-01-30")
    ax.axvline(event_date, color="gray", linestyle="--", linewidth=1)

    # **Add annotation for DeepSeek event**
    ax.text(event_date, df["Trading Volume"].max(), "DeepSeek gained widespread attention", 
            color="black", fontsize=10, ha="left", va="bottom", bbox=dict(facecolor="white", edgecolor="gray", boxstyle="round,pad=0.3"))

    # Remove top & right borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Customize the axis colors to gray
    ax.spines["bottom"].set_color("gray")
    ax.spines["left"].set_color("gray")
    ax.xaxis.label.set_color("gray")
    ax.yaxis.label.set_color("gray")
    ax.tick_params(axis="x", colors="gray", rotation=45)
    ax.tick_params(axis="y", colors="gray")

    # Titles and labels
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Trading Volume", fontsize=12)
    ax.set_title("Alibaba (9988.HK) Trading Volume Over Time", fontsize=14, fontweight="bold", color="black")
    ax.legend()

    st.pyplot(fig)

    # Summary Section
    st.write("### 📈 Summary of Alibaba's Trading Volume (Last 3 Months)")
    latest_volume = df.iloc[0]["Trading Volume"]
    average_volume = df["Trading Volume"].mean()
    
    # Display Data Table (latest first)
    st.write("### 📅 Latest Trading Volume Data (Newest First)")
    st.dataframe(df)


    # Compare today and yesterday
    if len(df) > 1:
        yesterday_volume = df.iloc[1]["Trading Volume"]
        volume_change = latest_volume - yesterday_volume
        percentage_change = (volume_change / yesterday_volume) * 100 if yesterday_volume != 0 else 0

        trend_icon = "📈" if volume_change > 0 else "📉"
        st.write(f"- **Latest Trading Volume**: {latest_volume:,.0f} shares")
        st.write(f"- **Average Volume (Last 3 Months)**: {average_volume:,.0f} shares")
        st.write(f"- **Trend**: {trend_icon} **{volume_change:,.0f} shares** ({percentage_change:.2f}%) compared to yesterday")
    else:
        st.write(f"- **Latest Trading Volume**: {latest_volume:,.0f} shares")
        st.write(f"- **Average Volume (Last 3 Months)**: {average_volume:,.0f} shares")
        st.write(f"- **Trend**: Data insufficient for comparison")

else:
    st.error("⚠️ No trading volume data available. Please check the data source or try again later.")
