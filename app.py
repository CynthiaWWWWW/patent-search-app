import streamlit as st
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 頁面基本設定 ---
st.set_page_config(page_title="RegTech Dashboard", page_icon="🛡️", layout="wide")

# --- 自定義 CSS：縮小標題與美化間距 ---
st.markdown("""
    <style>
    .main-title {
        font-size: 24px !important;
        font-weight: 700;
        color: #1E1E1E;
        margin-bottom: 10px;
        padding-top: 0px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    <div class="main-title">🛡️ 醫材與專利整合搜尋儀表板</div>
    """, unsafe_allow_html=True)

# --- 通用：連線 Session 設定 ---
def get_robust_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })
    return session

session = get_robust_session()

# --- 建立分頁標籤 ---
tab1, tab2 = st.tabs(["🔍 FDA 510(k) 醫材搜尋", "💡 USPTO 專利搜尋"])

# ==========================================
# 分頁 1：FDA 510(k)
# ==========================================
with tab1:
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            k_num = st.text_input("510(k) 號碼", placeholder="例如: K231234", key="k_in")
            k_limit = st.slider("筆數", 5, 50, 10, key="k_sl")
        with col2:
            k_kw1 = st.text_input("關鍵字 1", placeholder="例: Laser", key="k_kw1")
            k_kw2 = st.text_input("關鍵字 2", placeholder="選填", key="k_kw2")
    
    if st.button("搜尋醫材資料", type="primary", use_container_width=True):
        query = f'k_number:"{k_num}"' if k_num else "+AND+".join([f'device_name:{k}*' for k in [k_kw1, k_kw2] if k])
        api_url = f'https://api.fda.gov/device/510k.json?search={query}&limit={k_limit}'
        
        with st.spinner('連線 FDA 中...'):
            try:
                res = session.get(api_url, timeout=10)
                if res.status_code == 200:
                    results = res.json().get('results', [])
                    st.success(f"找到 {len(results)} 筆結果")
                    for r in results:
                        kn = r.get('k_number')
                        st.markdown(f"""
                        <div style="border-left: 5px solid #28a745; padding: 10px; margin-bottom: 10px; background-color: #f0fdf4; border-radius: 5px; font-size: 0.9em;">
                            <b>510(k): {kn}</b><br>
                            產品：{r.get('device_name')}<br>
                            廠商：{r.get('applicant')}<br>
                            <a href="https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID={kn}" target="_blank">官方登記網頁</a>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.warning("查無資料。")
            except Exception as e: st.error(f"連線失敗: {e}")

# ==========================================
# 分頁 2：USPTO 專利
# ==========================================
with tab2:
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            p_num = st.text_input("專利號碼", placeholder="例如: 11500000", key="p_in")
            p_limit = st.slider("筆數", 5, 50, 10, key="p_sl")
        with col2:
            p_kw1 = st.text_input("專利關鍵字 1", "Semiconductor", key="p_kw1")
            p_kw2 = st.text_input("專利關鍵字 2", key="p_kw2")

    if st.button("搜尋專利資料", type="primary", use_container_width=True):
        if p_num:
            q = {"patent_number": p_num}
        else:
            k_list = [k for k in [p_kw1, p_kw2] if k]
            q = {"_text_any": {"patent_title": k_list[0]}} if len(k_list)==1 else {"_and": [{"_text_any": {"patent_title": k}} for k in k_list]}
        
        f = ["patent_number", "patent_title", "patent_date", "assignee_organization"]
        params = {"q": json.dumps(q), "f": json.dumps(f), "o": json.dumps({"per_page": p_limit})}
        
        with st.spinner('連線 USPTO 中...'):
            try:
                response = session.get("https://api.patentsview.org/patents/query", params=params, timeout=15)
                if response.status_code == 200:
                    patents = response.json().get('patents')
                    if patents:
                        st.success(f"找到 {len(patents)} 筆專利")
                        for p in patents:
                            pid = p.get('patent_number')
                            st.markdown(f"""
                            <div style="border-left: 5px solid #6366f1; padding: 10px; margin-bottom: 10px; background-color: #f5f3ff; border-radius: 5px; font-size: 0.9em;">
                                <b>US {pid}</b> | {p.get('patent_date')}<br>
                                標題：{p.get('patent_title')}<br>
                                <a href="https://patents.google.com/patent/US{pid}" target="_blank">Google Patents</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else: st.warning("查無結果。")
                else:
                    st.error(f"API 繁忙 (Code: {response.status_code})")
                    st.info(f"建議直接搜尋：[Google Patents 連結](https://patents.google.com/?q={p_kw1}+{p_kw2})")
            except Exception as e: st.error(f"連線異常: {e}")
