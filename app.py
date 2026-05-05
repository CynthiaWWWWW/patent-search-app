import streamlit as st
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 頁面基本設定 ---
st.set_page_config(page_title="RegTech Dashboard", page_icon="🛡️", layout="wide")

# --- 自定義 CSS ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 40px; background-color: #f0f2f6; border-radius: 5px 5px 0px 0px; }
    </style>
    <div class="main-title">🛡️ 醫材與專利整合搜尋儀表板</div>
    """, unsafe_allow_html=True)

# --- 強效連線 Session ---
def get_robust_session():
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retry))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    })
    return session

session = get_robust_session()

tab1, tab2 = st.tabs(["🔍 FDA 510(k) 醫材搜尋", "💡 USPTO 專利搜尋"])

# ==========================================
# 分頁 1：FDA 510(k) (邏輯不變，維持穩定)
# ==========================================
with tab1:
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1: kn_in = st.text_input("510(k) 號碼", key="k_in")
        with c2: kw1 = st.text_input("產品關鍵字", key="k_kw1")
    
    if st.button("搜尋醫材資料", type="primary", use_container_width=True):
        query = f'k_number:"{kn_in}"' if kn_in else f'device_name:{kw1}*'
        api_url = f'https://api.fda.gov/device/510k.json?search={query}&limit=10'
        try:
            res = session.get(api_url, timeout=10)
            if res.status_code == 200:
                results = res.json().get('results', [])
                st.success(f"找到 {len(results)} 筆結果")
                for r in results:
                    st.write(f"✅ {r.get('k_number')} - {r.get('device_name')}")
            else: st.warning("FDA API 暫時無回應。")
        except Exception as e: st.error(f"連線失敗: {e}")

# ==========================================
# 分頁 2：USPTO 專利 (重寫連線與診斷邏輯)
# ==========================================
with tab2:
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            p_num = st.text_input("專利號碼", placeholder="例如: 11500000", key="p_in")
            p_limit = st.slider("筆數", 5, 50, 10, key="p_sl")
        with c2:
            p_kw1 = st.text_input("專利關鍵字 1", "bipolar", key="p_kw1")
            p_kw2 = st.text_input("專利關鍵字 2", "irrigat", key="p_kw2")

    if st.button("搜尋專利資料", type="primary", use_container_width=True):
        # 1. 構建語法
        if p_num:
            q = {"patent_number": p_num}
        else:
            k_list = [k.strip() for k in [p_kw1, p_kw2] if k.strip()]
            if not k_list:
                st.error("請輸入關鍵字")
                st.stop()
            q = {"_text_any": {"patent_title": k_list[0]}} if len(k_list)==1 else {"_and": [{"_text_any": {"patent_title": k}} for k in k_list]}
        
        f = ["patent_number", "patent_title", "patent_date", "assignee_organization"]
        params = {"q": json.dumps(q), "f": json.dumps(f), "o": json.dumps({"per_page": p_limit})}
        
        api_url = "https://api.patentsview.org/patents/query"
        
        with st.spinner('正在與 USPTO 進行通訊...'):
            try:
                # 嘗試發送請求
                resp = session.get(api_url, params=params, timeout=15)
                
                # 診斷：如果不是 200，抓出原因
                if resp.status_code != 200:
                    st.error(f"❌ 伺服器拒絕連線 (錯誤碼: {resp.status_code})")
                    if resp.status_code == 403:
                        st.info("💡 診斷：Streamlit 的 IP 被 USPTO 防火牆暫時封鎖了。")
                    with st.expander("查看原始錯誤回應內容"):
                        st.code(resp.text[:500])
                    st.markdown(f"**[建議直接點此在 Google Patents 搜尋]({f'https://patents.google.com/?q={p_kw1}+{p_kw2}'})**")
                    st.stop()

                # 解析 JSON
                data = resp.json()
                patents = data.get('patents')
                
                if patents:
                    st.success(f"找到 {len(patents)} 筆專利")
                    for p in patents:
                        pid = p.get('patent_number')
                        st.markdown(f"""
                        <div style="border-left: 5px solid #6366f1; padding: 10px; margin-bottom: 10px; background-color: #f5f3ff; border-radius: 8px;">
                            <b>US {pid}</b> | {p.get('patent_date')}<br>
                            標題：{p.get('patent_title')}<br>
                            <a href="https://patents.google.com/patent/US{pid}" target="_blank">👉 前往查看</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("API 回傳空結果。")

            except json.JSONDecodeError:
                st.error("⚠️ 伺服器回傳了 HTML 網頁而非數據。")
                st.info("這通常代表 USPTO 偵測到自動化行為並攔截了連線。")
            except Exception as e:
                st.error(f"連線異常: {e}")
