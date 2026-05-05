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
    .stButton>button { border-radius: 8px; height: 3em; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板 (Verified Search)</div>
    """, unsafe_allow_html=True)

# 初始化確認狀態 (Session State)
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = False

# 當輸入變更時，重設確認狀態的函式
def on_input_change():
    st.session_state.confirmed = False

# --- 4. 介面輸入區 ---
st.markdown("### 🚀 Step 1: 填寫檢索條件 (即時生成預覽)")

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<span class="label-en">Technology Keywords</span>', unsafe_allow_html=True)
        kw1 = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar", key="k1", on_change=on_input_change)
        kw2 = st.text_input("次要技術關鍵字", placeholder="例如: irrigat", key="k2", on_change=on_input_change)
        exact_kw = st.checkbox("關鍵字需完全符合", value=False, key="ex_kw", on_change=on_input_change)
        
        st.divider()
        
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        assignee = st.text_input("專利權人 (公司)", placeholder="例如: Medtronic", key="k3", on_change=on_input_change)
        exact_as = st.checkbox("公司名稱需完全符合", value=True, key="ex_as", on_change=on_input_change)
    
    with col2:
        st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
        inventor = st.text_input("發明人", placeholder="例如: MALIS", key="k5", on_change=on_input_change)
        exact_iv = st.checkbox("發明人姓名需完全符合", value=True, key="ex_iv", on_change=on_input_change)
        
        st.divider()
        
        st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
        cpc = st.text_input("CPC 分類號", key="k4", on_change=on_input_change)
        
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1, on_change=on_input_change)

# --- 5. 核心邏輯處理 ---
params = {}
kws = []
c_kw1 = ultimate_clean(kw1)
c_kw2 = ultimate_clean(kw2)
if c_kw1: kws.append(f'"{c_kw1}"' if exact_kw else c_kw1)
if c_kw2: kws.append(f'"{c_kw2}"' if exact_kw else c_kw2)
if kws: params['q'] = " ".join(kws)

if assignee:
    c_as = ultimate_clean(assignee)
    params['assignee'] = f'"{c_as}"' if exact_as else c_as

if inventor:
    c_iv = ultimate_clean(inventor)
    params['inventor'] = f'"{c_iv}"' if exact_iv else c_iv

if cpc: params['cpc'] = ultimate_clean(cpc)
params['num'] = p_limit

# --- 6. 即時預覽與確認區 ---
if params:
    st.divider()
    st.markdown("### 🚀 Step 2: 確認檢索指令")
    
    # 即時顯示目前條件 (即使還沒按確認也會變動)
    summary_parts = []
    if 'q' in params: summary_parts.append(f"關鍵字: **{params['q']}**")
    if 'assignee' in params: summary_parts.append(f"公司: **{params['assignee']}**")
    if 'inventor' in params: summary_parts.append(f"發明人: **{params['inventor']}**")
    if 'cpc' in params: summary_parts.append(f"分類: **{params['cpc']}**")
    
    st.info(" | ".join(summary_parts))

    # 確認按鈕
    if st.button("✅ 確認以上條件並鎖定指令", use_container_width=True):
        st.session_state.confirmed = True

    # --- 7. 最終搜尋按鈕 (僅在確認後顯示) ---
    if st.session_state.confirmed:
        st.success("🎉 指令已確認，您可以前往 Google Patents 搜尋了！")
        query_string = urllib.parse.urlencode(params)
        google_url = f"https://patents.google.com/?{query_string}"
        
        st.link_button("🔍 開啟 Google Patents 檢索頁面", google_url, use_container_width=True, type="primary")
        
        with st.expander("🛠️ 查看最終 URL"):
            st.code(google_url)
    else:
        st.warning("☝️ 請先點擊下方的『確認』按鈕來解鎖搜尋連結。")

else:
    st.info("💡 請填寫左方欄位以開始生成指令。")

st.divider()
st.caption("運作方式：此系統保持即時預覽。若修改任何欄位，須重新點選確認按鈕方可進行搜尋。")
