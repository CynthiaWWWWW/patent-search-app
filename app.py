import streamlit as st
import urllib.parse
import re

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 2. 強效清理函式 ---
def ultimate_clean(text):
    if text:
        # 移除任何括號、中括號、大括號與分號
        clean = re.sub(r'[()\[\]{};]', '', str(text))
        return clean.strip()
    return ""

# --- 3. CSS 美化 ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -2px; margin-top: 10px; }
    .stCheckbox { margin-bottom: -15px; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板 (Granular Control)</div>
    """, unsafe_allow_html=True)

# --- 4. 介面輸入區 ---
st.markdown("### 🚀 Google Patents 指令產生器")

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        # --- 關鍵字區塊 ---
        st.markdown('<span class="label-en">Technology Keywords</span>', unsafe_allow_html=True)
        kw1 = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar", key="k1")
        kw2 = st.text_input("次要技術關鍵字", placeholder="例如: irrigat", key="k2")
        exact_kw = st.checkbox("關鍵字需完全符合 (Exact Match)", value=False, key="ex_kw")
        
        st.divider()
        
        # --- 專利權人區塊 ---
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        assignee = st.text_input("專利權人 (公司)", placeholder="例如: Medtronic", key="k3")
        exact_as = st.checkbox("公司名稱需完全符合", value=True, key="ex_as")
    
    with col2:
        # --- 發明人區塊 ---
        st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
        inventor = st.text_input("發明人", placeholder="例如: MALIS", key="k5")
        exact_iv = st.checkbox("發明人姓名需完全符合", value=True, key="ex_iv")
        
        st.divider()
        
        # --- 其他設定 ---
        st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
        cpc = st.text_input("CPC 分類號", placeholder="例如: A61B18/14", key="k4")
        
        st.markdown('<span class="label-en">Display Settings</span>', unsafe_allow_html=True)
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1)

# --- 5. 核心邏輯：分別處理各個欄位的精準邏輯 ---
params = {}

# A. 處理關鍵字
kws = []
c_kw1 = ultimate_clean(kw1)
c_kw2 = ultimate_clean(kw2)
if c_kw1: kws.append(f'"{c_kw1}"' if exact_kw else c_kw1)
if c_kw2: kws.append(f'"{c_kw2}"' if exact_kw else c_kw2)
if kws:
    params['q'] = " ".join(kws)

# B. 處理專利權人
if assignee:
    c_as = ultimate_clean(assignee)
    params['assignee'] = f'"{c_as}"' if exact_as else c_as

# C. 處理發明人
if inventor:
    c_iv = ultimate_clean(inventor)
    params['inventor'] = f'"{c_iv}"' if exact_iv else c_iv

# D. 處理 CPC
if cpc:
    params['cpc'] = ultimate_clean(cpc)

params['num'] = p_limit

# --- 6. 生成網址與顯示 ---
if params:
    st.divider()
    
    query_string = urllib.parse.urlencode(params)
    google_url = f"https://patents.google.com/?{query_string}"
    
    st.markdown("#### 📋 檢索條件確認")
    
    # 動態產生摘要文字
    summary_parts = []
    if 'q' in params: 
        mode = "(精準)" if exact_kw else "(模糊)"
        summary_parts.append(f"關鍵字: **{params['q']}** {mode}")
    if 'assignee' in params: 
        mode = "(精準)" if exact_as else "(模糊)"
        summary_parts.append(f"公司: **{params['assignee']}** {mode}")
    if 'inventor' in params: 
        mode = "(精準)" if exact_iv else "(模糊)"
        summary_parts.append(f"發明人: **{params['inventor']}** {mode}")
    if 'cpc' in params: 
        summary_parts.append(f"分類號: **{params['cpc']}**")
    
    st.info(" | ".join(summary_parts))

    # 按鈕
    st.link_button("🔍 點此前往 Google Patents 搜尋", google_url, use_container_width=True, type="primary")
    
    # 除錯與連結檢查
    with st.expander("🛠️ 查看生成的 URL 參數結構"):
        st.code(google_url)
else:
    st.info("💡 請填寫至少一個欄位。")

st.divider()
st.caption("版本說明：支援關鍵字、公司、發明人獨立精準比對設定。")
