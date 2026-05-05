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

# --- 3. 終極 CSS 優化 (壓縮空間 + 調整 Step 字體) ---
st.markdown("""
    <style>
    /* 移除 Streamlit 預設的上邊距，達成一頁式效果 */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 0rem !important; }
    
    /* 總標題樣式 - 稍微縮小以節省空間 */
    .main-title { font-size: 24px !important; font-weight: 800; color: #1E1E1E; margin-bottom: 10px; text-align: center; }
    
    /* Step 說明文字 - 調大至 20px */
    .step-text { 
        font-size: 20px !important; 
        font-weight: 700; 
        color: #333; 
        margin-bottom: 8px; 
        margin-top: 5px;
        border-left: 5px solid #4285F4;
        padding-left: 10px;
    }
    
    /* 欄位標籤 */
    .label-en { font-size: 11px; color: #777; display: block; margin-bottom: -5px; margin-top: 5px; font-weight: 600; }
    
    /* 緊湊化分隔線 */
    hr { margin: 0.5rem 0 !important; }

    /* 按鈕樣式強化 */
    .stButton>button {
        border-radius: 10px !important;
        height: 3em !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }

    /* 「確認」按鈕綠色 */
    div.stButton > button { background-color: #28a745 !important; color: white !important; border: none !important; }
    
    /* 「Google 搜尋」藍色 */
    .stLinkButton > a {
        background-color: #4285F4 !important;
        color: white !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 0.5rem 1rem !important;
        text-align: center !important;
        border: none !important;
        display: block;
    }
    
    /* 縮減 Widget 之間的間距 */
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板</div>
    """, unsafe_allow_html=True)

# 初始化確認狀態
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = False

def on_input_change():
    st.session_state.confirmed = False

# --- 4. 介面輸入區 ---
st.markdown('<div class="step-text">Step 1: 填寫檢索條件</div>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<span class="label-en">Keywords</span>', unsafe_allow_html=True)
        sub_c1, sub_c2 = st.columns(2)
        kw1 = sub_c1.text_input("主要關鍵字", placeholder="Bipolar", key="k1", on_change=on_input_change, label_visibility="collapsed")
        kw2 = sub_c2.text_input("次要關鍵字", placeholder="irrigat", key="k2", on_change=on_input_change, label_visibility="collapsed")
        exact_kw = st.checkbox("關鍵字精準比對", value=False, key="ex_kw", on_change=on_input_change)
        
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        assignee = st.text_input("公司名稱", placeholder="Medtronic", key="k3", on_change=on_input_change, label_visibility="collapsed")
        exact_as = st.checkbox("公司精準比對", value=True, key="ex_as", on_change=on_input_change)
    
    with col2:
        st.markdown('<span class="label-en">Inventor / CPC</span>', unsafe_allow_html=True)
        sub_i1, sub_i2 = st.columns(2)
        inventor = sub_i1.text_input("發明人", placeholder="MALIS", key="k5", on_change=on_input_change, label_visibility="collapsed")
        cpc = sub_i2.text_input("CPC 分類", placeholder="A61B", key="k4", on_change=on_input_change, label_visibility="collapsed")
        exact_iv = st.checkbox("發明人精準比對", value=True, key="ex_iv", on_change=on_input_change)
        
        st.markdown('<span class="label-en">Display Results</span>', unsafe_allow_html=True)
        p_limit = st.selectbox("每頁筆數", [10, 20, 50, 100], index=1, on_change=on_input_change, label_visibility="collapsed")

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
    # 摘要摘要 (一行式)
    summary = []
    if 'q' in params: summary.append(f"關鍵字: **{params['q']}**")
    if 'assignee' in params: summary.append(f"公司: **{params['assignee']}**")
    if 'inventor' in params: summary.append(f"人名: **{params['inventor']}**")
    
    st.info(" | ".join(summary))

    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown('<div class="step-text">Step 2: 驗證</div>', unsafe_allow_html=True)
        if st.button("🚀 點此確認條件", use_container_width=True):
            st.session_state.confirmed = True
            st.rerun()
            
    with c2:
        st.markdown('<div class="step-text">Step 3: 搜尋</div>', unsafe_allow_html=True)
        if st.session_state.confirmed:
            query_string = urllib.parse.urlencode(params)
            google_url = f"https://patents.google.com/?{query_string}"
            st.link_button("🔍 前往 Google Patents", google_url, use_container_width=True)
        else:
            st.button("待解鎖...", disabled=True, use_container_width=True)
else:
    st.empty() # 保持空間整潔

st.caption("Tip: 一頁式佈局。修改條件後需重新確認 Step 2。")
