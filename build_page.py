from datetime import datetime
import pandas as pd
import requests

# 1. 抓取當前台灣時間，顯示在網頁頂部，讓家人清楚知道資料何時更新
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 2. 抓取證交所 OpenAPI 數據
pe_url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"
price_url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

df_pe = pd.DataFrame(requests.get(pe_url).json())
df_price = pd.DataFrame(requests.get(price_url).json())

# 3. 雙表合併與型態清洗
df = pd.merge(df_pe, df_price, on="Code")
df["PE"] = pd.to_numeric(df["PEratio"], errors="coerce")
df["Price"] = pd.to_numeric(df["ClosingPrice"], errors="coerce")
df["Yield"] = pd.to_numeric(df["DividendYield"], errors="coerce")

# 4. 條件過濾：本益比 > 0 且 <= 20，股價 < 100
filtered_df = df[
    (df["PE"] > 0) & 
    (df["PE"] <= 20) & 
    (df["Price"] < 100)
].copy()

# 5. 依殖利率從高到低排序
filtered_df = filtered_df.sort_values(by="Yield", ascending=False)

# 6. 動態組裝 HTML 表格的每一列 (<tr>)
rows_html = ""
for _, row in filtered_df.iterrows():
    rows_html += f"""
    <tr class="border-b border-gray-100 hover:bg-slate-50 transition">
        <td class="py-3 px-4 font-bold text-gray-900">{row['Code']}</td>
        <td class="py-3 px-4 text-gray-700">{row['Name_x']}</td>
        <td class="py-3 px-4 font-semibold text-blue-600">NT$ {row['Price']:.2f}</td>
        <td class="py-3 px-4 text-gray-600">{row['PE']:.2f}</td>
        <td class="py-3 px-4 text-emerald-600 font-bold">{row['Yield']:.2f}%</td>
    </tr>
    """

# 7. 組裝完整 HTML 頁面（引入 Tailwind CSS 確保手機螢幕完美排版）
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>精選台股價值清單</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 min-h-screen p-4 sm:p-6 text-slate-800">
    <div class="max-w-3xl mx-auto">
        <!-- 資訊卡片 -->
        <div class="bg-white rounded-2xl shadow-sm p-5 mb-5 border border-slate-100">
            <h1 class="text-2xl font-black text-slate-900 tracking-tight">📈 台股精選價值清單</h1>
            <p class="text-sm text-slate-500 mt-2">
                篩選條件：本益比 ≤ 20 且 股價 < 100 元 ｜ 共 <span class="font-bold text-blue-600">{len(filtered_df)}</span> 檔
            </p>
            <p class="text-xs text-slate-400 mt-1">更新時間：{update_time}</p>
        </div>

        <!-- 股票清單表格（支援手機滑動） -->
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden border border-slate-100">
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm whitespace-nowrap">
                    <thead class="bg-slate-100 text-slate-500 uppercase text-xs">
                        <tr>
                            <th class="py-3 px-4">代號</th>
                            <th class="py-3 px-4">名稱</th>
                            <th class="py-3 px-4">收盤價</th>
                            <th class="py-3 px-4">本益比</th>
                            <th class="py-3 px-4">殖利率</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 8. 輸出成 index.html（必須指定 utf-8 編碼確保繁體中文不亂碼）
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"網頁生成成功！共寫入 {len(filtered_df)} 檔股票至 index.html")