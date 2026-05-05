import streamlit as st
import requests
import json
from datetime import datetime
import urllib.parse

# --- 頁面基本設定 / Page Config ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- CSS 美化介面 / Custom CSS ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .search-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; }
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -5px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板 (Global Patent Advanced Search)</div>
    """, unsafe_allow_html=True)

# --- 側邊欄：資訊 / Sidebar Info ---
with st.sidebar:
    st.write("### ℹ️ 系統狀態 (System Info)")
    st.write("**USPTO API Status:** ⚠️ Restricted")
    st.write("**Google Patents:** ✅ Online")
    st.divider()
    st.write("### 📖 快速教學 (Quick Tip)")
    st.caption("1. 填寫關鍵字、公司或 CPC 分類。")
    st.caption("2. 系統會自動生成 Google 專用的搜尋指令。")
    st.caption("3. 點擊藍色大按鈕直接跳轉查看結果。")

# ==========================================
# 核心內容：專利進階搜尋產生器
# ==========================================
st.markdown("### 🚀 Google Patents 指令產生器 (Command Generator)")
st.caption("填寫欄位自動生成進階搜尋字串 / Fill fields to generate professional search string.")

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
        st.markdown('<span class="label-en">Publication Date Range (after/before)</span>', unsafe_allow_html=True)
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

# 顯示生成的字串與按鈕
if final_query:
    st.markdown("---")
    st.markdown("#### 🛠️ 生成的指令 (Generated Command):")
    st.code(final_query, language="bash")
    
    # 建立跳轉連結 / URL Encoding
    encoded_query = urllib.parse.quote(final_query)
    google_url = f"https://patents.google.com/?q={encoded_query}&num={p_limit}"
    
    st.markdown(f"""
        <a href="{google_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #4285F4; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; border: 2px solid #3367d6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                🔍 點此前往 Google Patents 搜尋 (Go to Google Patents)
            </div>
        </a>
    """, unsafe_allow_html=True)
else:
    st.info("💡 請填寫上方任一欄位以生成搜尋指令 (Please fill fields to generate command).")

# 頁尾說明
st.divider()
st.caption("Disclaimer: This tool generates search strings for Google Patents and does not guarantee complete FTO analysis.")
