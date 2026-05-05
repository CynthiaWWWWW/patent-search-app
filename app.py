import streamlit as st
import requests
import json
from datetime import datetime
import urllib.parse

# --- 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 清理函式：自動移除括號 ---
def clean_str(text):
    if text:
        # 移除左括號、右括號並修剪前後空格
        return str(text).replace("(", "").replace(")", "").strip()
    return ""

# --- CSS 美化 ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -5px; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板 (Global Patent Advanced Search)</div>
    """, unsafe_allow_html=True)

# --- 核心內容 ---
st.markdown("### 🚀 Google Patents 指令產生器")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="label-en">Primary Keywords</span>', unsafe_allow_html=True)
        g_kw = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar Electrosurgical", key="g1")
        
        st.markdown('<span class="label-en">Secondary Keywords</span>', unsafe_allow_html=True)
        g_kw2 = st.text_input("次要技術/應用關鍵字", placeholder="例如: Robotic Surgery", key="g1_2")
        
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        g_assignee = st.text_input("專利權人 (公司)", placeholder="例如: Medtronic", key="g2")
    
    with col2:
        st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
        g_cpc = st.text_input("CPC 分類號", placeholder="例如: A61B18/14", key="g3")

        st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
        g_inventor = st.text_input("發明人", placeholder="例如: Smith", key="g6")
        
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1)

# --- 核心邏輯：自動生成字串並移除括號 ---
query_parts = []

# 對每個欄位使用 clean_str 進行過濾
if g_kw: 
    query_parts.append(clean_str(g_kw))
if g_kw2: 
    query_parts.append(clean_str(g_kw2))
if g_assignee: 
    query_parts.append(f'assignee:"{clean_str(g_assignee)}"')
if g_inventor: 
    query_parts.append(f'inventor:"{clean_str(g_inventor)}"')
if g_cpc: 
    query_parts.append(f'cpc:{clean_str(g_cpc)}')

final_query = " ".join(query_parts)

# --- 顯示與按鈕 ---
if final_query:
    st.markdown("---")
    st.markdown("#### 🛠️ 生成的指令 (不含括號):")
    st.code(final_query, language="bash")
    
    # 進行 URL 編碼
    encoded_query = urllib.parse.quote(final_query)
    google_url = f"https://patents.google.com/?q={encoded_query}&num={p_limit}"
    
    st.markdown(f"""
        <a href="{google_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #4285F4; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; border: 2px solid #3367d6;">
                🔍 點此前往 Google Patents 搜尋
            </div>
        </a>
    """, unsafe_allow_html=True)
else:
    st.info("💡 請填寫欄位以生成指令。")
