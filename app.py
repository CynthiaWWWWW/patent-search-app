import streamlit as st
import urllib.parse
import re

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 2. 強效清理函式：確保字串中完全沒有括號與分號 ---
def ultimate_clean(text):
    if text:
        # 移除任何括號、中括號、大括號與分號
        clean = re.sub(r'[()\[\]{};]', '', str(text))
        return clean.strip()
    return ""

# --- 3. CSS 美化介面 ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -5px; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板 (No-Bracket Version)</div>
    """, unsafe_allow_html=True)

# --- 4. 介面輸入區 ---
st.markdown("### 🚀 Google Patents 指令產生器")
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="label-en">Primary Keywords</span>', unsafe_allow_html=True)
        kw1 = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar", key="k1")
        
        st.markdown('<span class="label-en">Secondary Keywords</span>', unsafe_allow_html=True)
        kw2 = st.text_input("次要技術關鍵字", placeholder="例如: irrigat", key="k2")
        
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        assignee = st.text_input("專利權人 (公司)", placeholder="例如: KIRWAN", key="k3")
    
    with col2:
        st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
        cpc = st.text_input("CPC 分類號", placeholder="例如: A61B18/14", key="k4")

        st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
        inventor = st.text_input("發明人", placeholder="例如: Smith", key="k5")
        
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1)

# --- 5. 核心邏輯：參數拆解 (關鍵！解決括號問題的終極方案) ---
# 我們不把所有條件拼在一起，而是分開存放在字典中
params = {}

# 處理關鍵字 (放在 q 參數中)
kws = []
if kw1: kws.append(ultimate_clean(kw1))
if kw2: kws.append(ultimate_clean(kw2))
if kws:
    params['q'] = " ".join(kws)

# 處理專利權人 (獨立參數，不進 q)
if assignee:
    params['assignee'] = ultimate_clean(assignee)

# 處理發明人 (獨立參數)
if inventor:
    params['inventor'] = ultimate_clean(inventor)

# 處理 CPC 分類 (獨立參數)
if cpc:
    params['cpc'] = ultimate_clean(cpc)

# 結果筆數
params['num'] = p_limit

# --- 6. 生成網址與顯示 ---
if params:
    st.divider()
    
    # 建立 URL 編碼的查詢字串
    # 這會生成類似 q=keyword&assignee=COMPANY&cpc=CPC... 的結構
    query_string = urllib.parse.urlencode(params)
    google_url = f"https://patents.google.com/?{query_string}"
    
    # 顯示目前條件摘要
    st.markdown("#### 📋 檢索條件確認")
    st.info(f"技術關鍵字: {params.get('q', '無')} | 專利權人: {params.get('assignee', '無')} | 分類號: {params.get('cpc', '無')}")

    # 使用 Streamlit 官方按鈕組件跳轉
    st.link_button("🔍 點此前往 Google Patents 搜尋 (已優化 URL 結構)", google_url, use_container_width=True, type="primary")
    
    # 除錯資訊 (可選)
    with st.expander("🛠️ 查看生成的完整網址"):
        st.code(google_url)
else:
    st.info("💡 請在上方欄位填寫至少一個搜尋條件。")

st.divider()
st.caption("註：此版本透過拆解參數傳送至 Google 進階搜尋欄位，可最大程度避免搜尋框出現自動分組括號 ()。")
