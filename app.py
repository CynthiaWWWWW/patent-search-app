import streamlit as st
import requests
import json
from datetime import datetime
import urllib.parse

# --- 頁面基本設定 / Page Config ---
st.set_page_config(page_title="RegTech Dashboard", page_icon="🛡️", layout="wide")

# --- CSS 美化介面 / Custom CSS ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 40px; background-color: #f0f2f6; border-radius: 5px 5px 0px 0px; padding: 8px 16px; font-size: 14px; }
    .search-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -5px; }
    </style>
    <div class="main-title">🛡️ 醫材與專利整合搜尋儀表板 (RegTech Search Dashboard)</div>
    """, unsafe_allow_html=True)

# --- 建立分頁標籤 / Tabs ---
tab1, tab2 = st.tabs([
    "🔍 FDA 510(k) 醫材搜尋 (Medical Device Search)", 
    "💡 全球專利進階搜尋 (Global Patent Advanced Search)"
])

# ==========================================
# 分頁 1：FDA 510(k) 搜尋
# ==========================================
with tab1:
    st.markdown("### 🔍 FDA 510(k) 醫材搜尋 (Medical Device Search)")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            k_num = st.text_input("510(k) 號碼 (510(k) Number)", placeholder="K231234", key="k1")
            k_limit = st.slider("顯示筆數 (Results Limit)", 5, 50, 10, key="ks")
        with col2:
            k_kw = st.text_input("產品關鍵字 (Device Keywords)", placeholder="Laser, Bipolar...", key="k2")

    if st.button("執行醫材搜尋 (Run Device Search)", type="primary", use_container_width=True):
        # 原有的 FDA API 邏輯 (保持穩定連線)
        query = f'k_number:"{k_num}"' if k_num else f'device_name:{k_kw}*'
        api_url = f'https://api.fda.gov/device/510k.json?search={query}&limit={k_limit}'
        with st.spinner('Connecting to FDA Database...'):
            try:
                res = requests.get(api_url, timeout=10)
                if res.status_code == 200:
                    results = res.json().get('results', [])
                    st.success(f"找到 {len(results)} 筆結果 (Found {len(results)} results)")
                    for r in results:
                        st.info(f"✅ {r.get('k_number')} | {r.get('device_name')} - {r.get('applicant')}")
                else: st.warning("查無資料 (No results found).")
            except: st.error("連線超時 (Connection Timeout).")

# ==========================================
# 分頁 2：專利進階搜尋產生器
# ==========================================
with tab2:
    st.markdown("### 🚀 Google Patents 指令產生器 (Command Generator)")
    st.caption("填寫欄位自動生成 Google 進階搜尋字串 / Fill fields to generate search string.")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<span class="label-en">Technology Keywords</span>', unsafe_allow_html=True)
            g_kw = st.text_input("技術關鍵字", placeholder="例如: Bipolar Electrosurgical", key="g1")
            
            st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
            g_assignee = st.text_input("專利權人 (公司)", placeholder="例如: Medtronic", key="g2")
            
            st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
            g_cpc = st.text_input("CPC 分類號", placeholder="例如: A61B18/14", key="g3")
        
        with col2:
            st.markdown('<span class="label-en">Priority / Publication Date Range</span>', unsafe_allow_html=True)
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1: g_after = st.date_input("日期起始 (From)", value=None, key="g4")
            with sub_c2: g_before = st.date_input("日期結束 (To)", value=None, key="g5")
            
            st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
            g_inventor = st.text_input("發明人", placeholder="例如: Smith", key="g6")
            
            p_limit = st.selectbox("每頁顯示筆數 (Results Per Page)", [10, 20, 50, 100], index=1)

    # --- 核心邏輯：自動生成字串 / Command Building ---
    query_parts = []
    if g_kw: query_parts.append(g_kw)
    if g_assignee: query_parts.append(f'assignee:"{g_assignee}"')
    if g_inventor: query_parts.append(f'inventor:"{g_inventor}"')
    if g_cpc: query_parts.append(f'cpc:{g_cpc}')
    if g_after: query_parts.append(f'after:{g_after.strftime("%Y%m%d")}')
    if g_before: query_parts.append(f'before:{g_before.strftime("%Y%m%d")}')
    
    final_query = " ".join(query_parts)
    
    if final_query:
        st.markdown("---")
        st.markdown("#### 🛠️ 生成的指令 (Generated Command):")
        st.code(final_query, language="bash")
        
        # 建立跳轉連結 / URL Encoding
        encoded_query = urllib.parse.quote(final_query)
        google_url = f"https://patents.google.com/?q={encoded_query}&num={p_limit}"
        
        st.markdown(f"""
            <a href="{google_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #4285F4; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; border: 2px solid #3367d6;">
                    🔍 點此前往 Google Patents 搜尋 (Go to Google Patents)
                </div>
            </a>
            <p style="text-align: center; font-size: 12px; color: #666; margin-top: 10px;">
                * 註：若點擊無反應，請手動複製上方代碼貼至 Google Patents 搜尋框。
            </p>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 請填寫上方欄位以生成指令 (Please fill fields to generate command).")

# --- 側邊欄：資訊 / Sidebar Info ---
with st.sidebar:
    st.write("### ℹ️ 系統資訊 (System Info)")
    st.write("**FDA API Status:** ✅ Online")
    st.write("**USPTO API Status:** ⚠️ Restricted IP")
    st.divider()
    st.write("### 📖 快速教學 (Quick Tip)")
    st.caption("使用 `assignee:` 可以鎖定特定公司，`cpc:` 可以鎖定特定技術類別。")
