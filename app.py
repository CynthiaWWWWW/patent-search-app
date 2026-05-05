import streamlit as st
import urllib.parse
import re

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 2. 強效清理函式 ---
def ultimate_clean(text):
    if text:
        clean = re.sub(r'[()\[\]{};]', '', str(text))
        return clean.strip()
    return ""

# --- 3. CSS 進階美化 (包含縮小 Step 字體) ---
st.markdown("""
    <style>
    /* 總標題樣式 */
    .main-title { font-size: 26px !important; font-weight: 800; color: #1E1E1E; margin-bottom: 20px; text-align: center; }
    
    /* 讓 Step 說明文字變小 */
    .step-text { 
        font-size: 16px !important; 
        font-weight: 700; 
        color: #555; 
        margin-bottom: 10px; 
        margin-top: 10px;
        display: flex;
        align-items: center;
    }
    
    .label-en { font-size: 12px; color: #888; display: block; margin-bottom: -2px; margin-top: 10px; font-weight: 600; }
    
    /* 按鈕樣式強化 */
    .stButton>button {
        transition: all 0.3s ease;
        border-radius: 10px !important;
        height: 3.2em !important;
        font-size: 16px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* 「確認鎖定」按鈕 (綠色) */
    div.stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button:hover {
        background-color: #218838 !important;
        transform: translateY(-1px);
    }

    /* 「Google 搜尋」連結按鈕 (Google 藍) */
    .stLinkButton > a {
        background-color: #4285F4 !important;
        color: white !important;
        border-radius: 10px !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        padding: 0.7rem 1rem !important;
        text-align: center !important;
        border: 1px solid #3367d6 !important;
        box-shadow: 0 6px 12px rgba(66, 133, 244, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stLinkButton > a:hover {
        background-color: #3367d6 !important;
        transform: scale(1.01);
        text-decoration: none !important;
    }

    /* 調整間距 */
    .stAlert { border-radius: 10px !important; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板</div>
    """, unsafe_allow_html=True)

# 初始化確認狀態
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = False

def on_input_change():
    st.session_state.confirmed = False

# --- 4. 介面輸入區 ---
st.markdown('<div class="step-text">🚀 Step 1: 填寫檢索條件 (即時生成預覽)</div>', unsafe_allow_html=True)

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
        
        st.markdown('<span class="label-en">Results Per Page</span>', unsafe_allow_html=True)
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1, on_change=on_input_change)

# --- 5. 邏輯處理 ---
params = {}
kws = []
c_kw1 = ultimate_clean(kw1); c_kw2 = ultimate_clean(kw2)
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

# --- 6. 預覽與確認區 ---
if params:
    st.divider()
    
    # 指令摘要預覽
    summary = []
    if 'q' in params: summary.append(f"關鍵字: **{params['q']}**")
    if 'assignee' in params: summary.append(f"公司: **{params['assignee']}**")
    if 'inventor' in params: summary.append(f"發明人: **{params['inventor']}**")
    
    st.info(" | ".join(summary))

    if not st.session_state.confirmed:
        st.markdown('<div class="step-text">🛠️ Step 2: 驗證指令並解鎖按鈕</div>', unsafe_allow_html=True)
        if st.button("🚀 確認檢索條件", use_container_width=True):
            st.session_state.confirmed = True
            st.rerun()
    else:
        st.markdown('<div class="step-text">🏁 Step 3: 發送檢索</div>', unsafe_allow_html=True)
        query_string = urllib.parse.urlencode(params)
        google_url = f"https://patents.google.com/?{query_string}"
        
        st.link_button("🔍 立即前往 Google Patents 搜尋結果", google_url, use_container_width=True)
        
        st.write("") # 增加一點間距
        if st.button("🔄 修改條件 (重新鎖定)", use_container_width=False):
            st.session_state.confirmed = False
            st.rerun()
else:
    st.info("💡 請填寫上方欄位以生成檢索指令。")
