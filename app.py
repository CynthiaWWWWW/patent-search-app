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
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -5px; }
    .exact-toggle { background-color: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板 (Exact Match Pro)</div>
    """, unsafe_allow_html=True)

# --- 4. 介面輸入區 ---
st.markdown("### 🚀 Google Patents 指令產生器")
with st.container(border=True):
    # 新增精準搜尋切換開關
    is_exact = st.toggle("使用精準搜尋 (Exact Match)", value=False, help="開啟後會自動在關鍵字加上引號，避免 Google 自動變換字根。")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="label-en">Primary Keywords</span>', unsafe_allow_html=True)
        kw1 = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar", key="k1")
        
        st.markdown('<span class="label-en">Secondary Keywords</span>', unsafe_allow_html=True)
        kw2 = st.text_input("次要技術關鍵字", placeholder="例如: irrigat", key="k2")
        
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        assignee = st.text_input("專利權人 (公司)", placeholder="例如: Medtronic", key="k3")
    
    with col2:
        st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
        cpc = st.text_input("CPC 分類號", placeholder="例如: A61B18/14", key="k4")

        st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
        inventor = st.text_input("發明人", placeholder="例如: MALIS", key="k5")
        
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1)

# --- 5. 核心邏輯：處理精準搜尋與參數拆解 ---
params = {}

# 處理關鍵字邏輯
kws = []
clean_kw1 = ultimate_clean(kw1)
clean_kw2 = ultimate_clean(kw2)

if clean_kw1:
    # 如果開啟精準搜尋，就加上引號
    kws.append(f'"{clean_kw1}"' if is_exact else clean_kw1)
if clean_kw2:
    kws.append(f'"{clean_kw2}"' if is_exact else clean_kw2)

if kws:
    params['q'] = " ".join(kws)

# 處理其他欄位 (專利權人與發明人通常建議直接精準，這裡我們維持原樣或也可同步加上引號)
if assignee:
    params['assignee'] = f'"{ultimate_clean(assignee)}"' if is_exact else ultimate_clean(assignee)
if inventor:
    params['inventor'] = f'"{ultimate_clean(inventor)}"' if is_exact else ultimate_clean(inventor)
if cpc:
    params['cpc'] = ultimate_clean(cpc)

params['num'] = p_limit

# --- 6. 生成網址與顯示 ---
if params:
    st.divider()
    
    query_string = urllib.parse.urlencode(params)
    google_url = f"https://patents.google.com/?{query_string}"
    
    st.markdown("#### 📋 檢索條件確認")
    
    summary_parts = []
    if 'q' in params: summary_parts.append(f"關鍵字: **{params['q']}**")
    if 'assignee' in params: summary_parts.append(f"專利權人: **{params['assignee']}**")
    if 'inventor' in params: summary_parts.append(f"發明人: **{params['inventor']}**")
    if 'cpc' in params: summary_parts.append(f"分類號: **{params['cpc']}**")
    
    st.info(" | ".join(summary_parts))

    if is_exact:
        st.warning("⚠️ **已啟動精準模式**：Google 將不會搜尋同義詞或字根變化 (Stemming)。")

    st.link_button("🔍 點此前往 Google Patents 搜尋", google_url, use_container_width=True, type="primary")
    
else:
    st.info("💡 請在上方欄位填寫至少一個搜尋條件。")

st.divider()
st.caption("版本說明：新增 Exact Match 切換功能，自動處理雙引號包覆邏輯。")
