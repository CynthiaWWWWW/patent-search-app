import streamlit as st
import urllib.parse
import re

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 2. 清理函式 ---
def ultimate_clean(text):
    if text:
        clean = re.sub(r'[()\[\]{};]', '', str(text))
        return clean.strip()
    return ""

# --- 3. CSS 修正版 (解決文字卡住問題) ---
st.markdown("""
    <style>
    /* 1. 確保內容不被頂部導覽列遮擋，並預留文字溢出空間 */
    .block-container { 
        padding-top: 4.5rem !important; 
        padding-bottom: 1rem !important; 
        max-width: 1100px; 
    }
    
    header { visibility: hidden; }

    /* 2. 標題：增加 line-height 確保中文字不被削掉 */
    .main-title { 
        font-size: 30px !important; 
        font-weight: 800; 
        color: #1E1E1E; 
        margin-bottom: 20px; 
        text-align: center;
        line-height: 1.4 !important; /* 關鍵：增加行高 */
    }
    
    /* 3. Step 標題：放寬容器高度 */
    .step-text { 
        font-size: 22px !important; 
        font-weight: 700; 
        color: #1E1E1E; 
        margin-bottom: 10px !important; 
        margin-top: 5px !important; 
        display: flex;
        align-items: center;
        line-height: 1.5 !important; /* 關鍵：增加行高 */
        overflow: visible !important; /* 確保不截斷 */
    }
    
    .step-num {
        background-color: #4285F4;
        color: white;
        border-radius: 50%;
        min-width: 32px; /* 改用 min-width 避免圓形變形 */
        height: 32px;
        display: inline-flex;
        justify-content: center;
        align-items: center;
        margin-right: 12px;
        font-size: 18px;
    }
    
    /* 4. 欄位標籤：加大垂直間距 */
    .field-label { 
        font-size: 16px !important; 
        color: #333; 
        display: block; 
        margin-bottom: 8px !important; 
        margin-top: 12px !important; 
        font-weight: 700; 
        line-height: 1.4 !important;
    }
    .label-en-span { font-size: 16px !important; font-weight: 700; margin-left: 5px; }
    
    /* 5. 搜尋按鈕：優化文字間距 */
    .stLinkButton > a {
        background: linear-gradient(135deg, #4285F4 0%, #3367D6 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        padding: 0.8rem !important;
        text-align: center !important;
        border: none !important;
        display: block !important;
        box-shadow: 0 5px 15px rgba(66, 133, 244, 0.2) !important;
        line-height: 1.2 !important;
    }

    /* 6. 稍微放寬元件間距，避免擠壓 */
    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
    
    /* 修正摘要資訊框文字 */
    .stAlert { 
        padding: 0.8rem 1rem !important; 
        border-radius: 10px !important; 
        line-height: 1.4 !important;
    }

    .stCheckbox { margin-top: 2px; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋產生器</div>
    """, unsafe_allow_html=True)

# --- 4. Step 1: 輸入區 ---
st.markdown('<div class="step-text"><span class="step-num">1</span> 填寫條件 Fill Conditions</div>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<span class="field-label">技術關鍵字 <span class="label-en-span">Technology Keywords</span></span>', unsafe_allow_html=True)
        sub_c1, sub_c2 = st.columns(2)
        kw1 = sub_c1.text_input("主", placeholder="例如: bipolar", key="k1", label_visibility="collapsed")
        kw2 = sub_c2.text_input("次", placeholder="例如: irrigation", key="k2", label_visibility="collapsed")
        exact_kw = st.checkbox("關鍵字精準比對 Exact Match", value=False, key="ex_kw")
        
        st.markdown('<span class="field-label">專利權人 (公司) <span class="label-en-span">Assignee / Company</span></span>', unsafe_allow_html=True)
        assignee = st.text_input("公司", placeholder="例如: Medtronic", key="k3", label_visibility="collapsed")
        exact_as = st.checkbox("公司精準比對 Exact Assignee", value=True, key="ex_as")
    
    with col2:
        st.markdown('<span class="field-label">發明人與分類 <span class="label-en-span">Inventor & CPC</span></span>', unsafe_allow_html=True)
        sub_i1, sub_i2 = st.columns(2)
        inventor = sub_i1.text_input("發明人", placeholder="例如: MALIS", key="k5", label_visibility="collapsed")
        cpc = sub_i2.text_input("CPC", placeholder="例如: A61B18", key="k4", label_visibility="collapsed")
        exact_iv = st.checkbox("發明人精準比對 Exact Inventor", value=True, key="ex_iv")
        
        st.markdown('<span class="field-label">每頁顯示筆數 <span class="label-en-span">Results Per Page</span></span>', unsafe_allow_html=True)
        p_limit = st.selectbox("筆數", [10, 20, 50, 100], index=1, label_visibility="collapsed")

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

# --- 6. Step 2: 確認與搜尋區 ---
if params:
    st.markdown('<div class="step-text"><span class="step-num">2</span> 確認並搜尋 Confirm & Search</div>', unsafe_allow_html=True)
    
    summary = []
    if 'q' in params: summary.append(f"🔍 **{params['q']}**")
    if 'assignee' in params: summary.append(f"🏢 **{params['assignee']}**")
    if 'inventor' in params: summary.append(f"👤 **{params['inventor']}**")
    if 'cpc' in params: summary.append(f"📂 **{params['cpc']}**")
    
    st.info(" | ".join(summary))

    query_string = urllib.parse.urlencode(params)
    google_url = f"https://patents.google.com/?{query_string}"
    
    st.link_button(f"🚀 前往 Google Patents 檢索結果", google_url, use_container_width=True)

else:
    st.info("💡 請於上方填寫至少一個關鍵字或條件以啟用搜尋。")
