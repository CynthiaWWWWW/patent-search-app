import streamlit as st
import urllib.parse
import re

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 2. 強效清理函式 ---
def ultimate_clean(text):
    if text:
        # 只保留字母、數字、空格、引號、冒號 (移除所有括號、分號、特殊符號)
        clean = re.sub(r'[()\[\]{};]', '', str(text))
        return clean.strip()
    return ""

# --- 3. 介面輸入區 ---
st.markdown("### 🚀 Google Patents 指令產生器 (V3 終極版)")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        kw1 = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar", key="k1")
        kw2 = st.text_input("次要技術關鍵字", placeholder="例如: irrigat", key="k2")
        assignee = st.text_input("專利權人 (公司)", placeholder="例如: KIRWAN", key="k3")
    
    with col2:
        cpc = st.text_input("CPC 分類號", key="k4")
        inventor = st.text_input("發明人", key="k5")
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1)

# --- 4. 核心邏輯：手動構建乾淨的字串 ---
query_list = []

# 個別清理並加入列表
if kw1: query_list.append(ultimate_clean(kw1))
if kw2: query_list.append(ultimate_clean(kw2))
if assignee: query_list.append(f'assignee:"{ultimate_clean(assignee)}"')
if inventor: query_list.append(f'inventor:"{ultimate_clean(inventor)}"')
if cpc: query_list.append(f'cpc:{ultimate_clean(cpc)}')

# 將列表結合為單一字串，並進行最終檢查
# 確保這是一個純 String (str)，絕對不是 Tuple
raw_query_string = " ".join(query_list)
final_query = str(raw_query_string).replace("(", "").replace(")", "").strip()

# --- 5. 顯示與輸出 ---
if final_query:
    st.divider()
    
    # 【除錯區】讓你確認程式內部的字串是否乾淨
    with st.expander("🔍 系統內部字串檢查 (Debug)"):
        st.write(f"目前字串內容: `{final_query}`")
        st.write(f"字串型別: `{type(final_query)}`")

    # 使用 quote_plus 把空格變成 +，這能防止 Google 自動加括號
    encoded_query = urllib.parse.quote_plus(final_query)
    google_url = f"https://patents.google.com/?q={encoded_query}&num={p_limit}"
    
    st.info(f"生成的指令: **{final_query}**")
    
    # 這裡改用 st.link_button，這是 Streamlit 官方更新的按鈕組件，較穩定
    st.link_button("🔍 前往 Google Patents 搜尋", google_url, use_container_width=True, type="primary")

else:
    st.info("💡 請填寫欄位以生成指令。")
