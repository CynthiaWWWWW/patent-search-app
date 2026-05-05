import streamlit as st
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 頁面基本設定 ---
st.set_page_config(page_title="RegTech Dashboard", page_icon="🛡️", layout="wide")

# --- 自定義 CSS：維持縮小標題與美化間距 ---
st.markdown("""
    <style>
    .main-title {
        font-size: 22px !important;
        font-weight: 700;
        color: #1E1E1E;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        padding: 8px 16px;
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
# 分頁 1：FDA 510(k) - 恢復 PDF 連結功能
# ==========================================
with tab1:
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            k_num_in = st.text_input("510(k) 號碼", placeholder="例如: K231234", key="k_in")
            k_limit = st.slider("筆數", 5, 50, 10, key="k_sl")
        with col2:
            k_kw1 = st.text_input("產品關鍵字", placeholder="例: Laser", key="k_kw1")
            k_kw2 = st.text_input("產品關鍵字 2", placeholder="選填", key="k_kw2")
    
    if st.button("搜尋醫材資料", type="primary", use_container_width=True):
        query = f'k_number:"{k_num_in}"' if k_num_in else "+AND+".join([f'device_name:{k}*' for k in [k_kw1, k_kw2] if k])
        api_url = f'https://api.fda.gov/device/510k.json?search={query}&limit={k_limit}'
        
        with st.spinner('連線 FDA 並驗證 PDF 中...'):
            try:
                res = session.get(api_url, timeout=10)
                if res.status_code == 200:
                    results = res.json().get('results', [])
                    st.success(f"找到 {len(results)} 筆結果")
                    
                    for r in results:
                        kn = r.get('k_number')
                        prefix = kn[1:3]
                        base_pdf_url = f"https://www.accessdata.fda.gov/cdrh_docs/pdf{prefix}/{kn}"
                        db_url = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID={kn}"
                        
                        # 驗證 PDF 連結
                        valid_pdf = None
                        for ext in [".pdf", ".PDF"]:
                            try:
                                check = session.head(base_pdf_url + ext, timeout=3)
                                if check.status_code == 200:
                                    valid_pdf = base_pdf_url + ext
                                    break
                            except: continue
                        
                        # 顯示結果卡片
                        bg = "#f0fdf4" if valid_pdf else "#fffbef"
                        border = "#28a745" if valid_pdf else "#ffc107"
                        
                        st.markdown(f"""
                        <div style="border-left: 5px solid {border}; padding: 12px; margin-bottom: 12px; background-color: {bg}; border-radius: 8px;">
                            <div style="font-size: 1.1em; font-weight: 800; color: #333; margin-bottom: 5px;">510(k) Number: {kn}</div>
                            <div style="font-size: 0.9em; line-height: 1.6;">
                                <b>產品：</b> {r.get('device_name')}<br>
                                <b>廠商：</b> {r.get('applicant')}<br>
                                <div style="margin-top: 8px;">
                                    {f'<a href="{valid_pdf}" target="_blank" style="color: #007bff; font-weight: bold;">👉 開啟 PDF Summary</a> | ' if valid_pdf else '<span style="color: #d9534f;">⚠️ 無 Summary 文件 | </span>'}
                                    <a href="{db_url}" target="_blank" style="color: #666;">官方登記網頁</a>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.warning("查無資料。")
            except Exception as e: st.error(f"連線失敗: {e}")

# ==========================================
# 分頁 2：USPTO 專利 - 維持正常功能
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
                            <div style="border-left: 5px solid #6366f1; padding: 12px; margin-bottom: 12px; background-color: #f5f3ff; border-radius: 8px;">
                                <div style="font-size: 1.1em; font-weight: 800; color: #333; margin-bottom: 5px;">Patent Number: US {pid}</div>
                                <div style="font-size: 0.9em;">
                                    <b>公告日期：</b> {p.get('patent_date')}<br>
                                    <b>標題：</b> {p.get('patent_title')}<br>
                                    <a href="https://patents.google.com/patent/US{pid}" target="_blank" style="color: #4f46e5; font-weight: bold;">👉 Google Patents</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else: st.warning("查無結果。")
                else: st.error(f"API 繁忙 (Code: {response.status_code})")
            except Exception as e: st.error(f"連線異常: {e}")
