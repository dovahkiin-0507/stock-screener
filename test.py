import pandas as pd
import requests

# 1. 取得本益比資料
pe_url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"
df_pe = pd.DataFrame(requests.get(pe_url).json())

# 2. 取得每日收盤行情（含股價）
price_url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
df_price = pd.DataFrame(requests.get(price_url).json())

# 3. 雙表合併：以股票代碼 (Code) 作為共同鍵值橫向串接
df = pd.merge(df_pe, df_price, on="Code")

# 4. 文字轉數值（清洗資料）
# errors='coerce' 代表若遇到留白或無效字元，自動轉為 NaN (空值) 而不報錯
df["PE"] = pd.to_numeric(df["PEratio"], errors="coerce")
df["Price"] = pd.to_numeric(df["ClosingPrice"], errors="coerce")
df["Yield"] = pd.to_numeric(df["DividendYield"], errors="coerce")

# 5. 多條件過濾：排除無本益比者、本益比 <= 20、股價 < 100
filtered_df = df[
    (df["PE"] > 0) & 
    (df["PE"] <= 20) & 
    (df["Price"] < 100)
].copy()

# 6. 挑選要看的欄位，並依照殖利率由高到低排序
result = filtered_df[["Code", "Name_x", "Price", "PE", "Yield"]].sort_values(
    by="Yield", ascending=False
)

# 7. 印出前 10 檔來驗證
print(f"符合條件的總檔數：{len(result)} 檔")
print(result.head(10))