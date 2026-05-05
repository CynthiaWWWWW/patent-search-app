import streamlit as st
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 頁面基本設定 ---
st.set_page_config(page_title="RegTech 搜尋儀表板", page_icon="🛡️", layout="wide")

st.title("🛡️ 醫材與專利整合搜尋儀表板")

# --- 建立分頁標籤 ---
tab1, tab2 = st.tabs(["🔍 FDA 510(k) 醫材搜尋", "💡 USPTO 專利搜尋"])

# --- 通用：建立一個強大的 Request Session (解決連線不穩) ---
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

# ==========================================
# 分頁 1：FDA 510(k) 搜尋邏輯
# ==========================================
with tab1:
    st.header("FDA 510(k) 快速檢索")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            k_num = st.text_input("510(k) 號碼", key="k_in")
            k_limit = st.slider("顯示筆數", 5, 50, 10, key="k_sl")
        with col2:
            k_kw1 = st.text_input("關鍵字 (例: Laser)", key="k_kw1")
            k_kw2 = st.text_input("關鍵字 (選填)", key="k_kw2")
    
    if st.button("執行醫材搜尋", type="primary"):
        query = f'k_number:"{k_num}"' if k_num else "+AND+".join([f'device_name:{k}*' for k in [k_kw1, k_kw2] if k])
        api_url = f'https://api.fda.gov/device/510k.json?search={query}&limit={k_limit}'
        
        with st.spinner('連線 FDA 中...'):
            try:
                res = session.get(api_url)
                if res.status_code == 200:
                    results = res.json().get('results', [])
                    for i, r in enumerate(results, 1):
                        kn = r.get('k_number')
                        st.markdown(f"""
                        <div style="border-left: 5px solid #28a745; padding: 10px; margin-bottom: 10px; background-color: #f0fdf4; border-radius: 5px;">
                            <b>#{i} 510(k): {kn}</b><br>
                            產品：{r.get('device_name')}<br>
                            廠商：{r.get('applicant')}<br>
                            <a href="https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID={kn}" target="_blank">查看官方登記</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("查無資料或 API 繁忙。")
            except Exception as e:
                st.error(f"連線失敗: {e}")

# ==========================================
# 分頁 2：USPTO 專利搜尋邏輯
# ==========================================
with tab2:
    st.header("USPTO 專利檢索")
    st.caption("使用字串編碼優化版，避開伺服器阻擋。")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            p_num = st.text_input("專利號碼", key="p_in")
            p_limit = st.slider("顯示筆數", 5, 50, 10, key="p_sl")
        with col2:
            p_kw1 = st.text_input("技術關鍵字", "Semiconductor", key="p_kw1")
            p_kw2 = st.text_input("關鍵字 (選填)", key="p_kw2")

    if st.button("執行專利搜尋", type="primary"):
        # 構建搜尋語法
        if p_num:
            q = {"patent_number": p_num}
        else:
            k_list = [k for k in [p_keyword_1, p_keyword_2] if k] # 這裡修正變數名稱
            # 修正變數名稱錯誤
            k_list = [k for k in [p_kw1, p_kw2] if k]
            q = {"_text_any": {"patent_title": k_list[0]}} if len(k_list)==1 else {"_and": [{"_text_any": {"patent_title": k}} for k in k_list]}
        
        f = ["patent_number", "patent_title", "patent_date", "assignee_organization"]
        params = {"q": json.dumps(q), "f": json.dumps(f), "o": json.dumps({"per_page": p_limit})}
        
        with st.spinner('正在挑戰 USPTO 防火牆...'):
            try:
                # 這裡使用最穩定的參數傳遞方式
                response = session.get("https://api.patentsview.org/patents/query", params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    patents = data.get('patents')
                    if patents:
                        for i, p in enumerate(patents, 1):
                            pid = p.get('patent_number')
                            st.markdown(f"""
                            <div style="border-left: 5px solid #6366f1; padding: 10px; margin-bottom: 10px; background-color: #f5f3ff; border-radius: 5px;">
                                <b>#{i} US {pid}</b> | {p.get('patent_date')}<br>
                                標題：{p.get('patent_title')}<br>
                                <a href="https://patents.google.com/patent/US{pid}" target="_blank">👉 Google Patents 查看</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("API 沒回傳結果，請檢查關鍵字。")
                else:
                    # 如果 API 還是擋，我們至少提供一個「智慧導引」
                    st.error(f"API 暫時阻擋連線 (代碼: {response.status_code})")
                    search_txt = f"{p_kw1} {p_kw2}".strip()
                    st.info(f"💡 由於 USPTO 官方 API 限制，請直接點擊下方連結查詢：")
                    st.markdown(f"[直接在 Google Patents 搜尋: {search_txt}](https://patents.google.com/?q={search_txt})")

            except Exception as e:
                st.error(f"連線異常: {e}")
