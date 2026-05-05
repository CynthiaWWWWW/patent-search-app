import streamlit as st  # 匯入 Streamlit 套件，用於建立網頁應用程式介面
import urllib.parse  # 匯入 URL 處理套件，用於將搜尋參數編碼成網址格式
import re  # 匯入正則表達式套件，用於清理使用者輸入的特殊字元

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="全球專利產生器", page_icon="🚀", layout="wide")  # 設定網頁標籤標題、圖示以及寬版佈局

# --- 2. 核心清理函式 ---
def clean(text):  # 定義一個字串清理函式，確保產生的網址不含非法字元
    if text:  # 如果輸入框內有文字內容
        return re.sub(r'[()\[\]{};]', '', str(text)).strip()  # 使用正則表達式移除所有括號、分號，並修剪前後空格
    return ""  # 如果輸入框是空的，則回傳空字串

# --- 3. 視覺樣式優化 (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 4.5rem !important; max-width: 1100px; } /* 設定網頁上邊距與內容最大寬度 */
    header { visibility: hidden; } /* 隱藏 Streamlit 預設的頂部裝飾條，避免擋住標題 */
    .main-title { font-size: 30px; font-weight: 800; color: #1E1E1E; text-align: center; line-height: 1.5; } /* 設定主標題樣式 */
    .step-text { font-size: 22px; font-weight: 700; color: #1E1E1E; margin: 15px 0 10px 0; display: flex; align-items: center; line-height: 1.5; } /* 設定步驟標題樣式 */
    .step-num { background: #4285F4; color: white; border-radius: 50%; min-width: 32px; height: 32px; display: inline-flex; justify-content: center; align-items: center; margin-right: 12px; font-size: 18px; } /* 設定步驟圓圈編號樣式 */
    .field-label { font-size: 16px; color: #333; display: block; margin: 12px 0 5px 0; font-weight: 700; line-height: 1.4; } /* 設定欄位中英對照標籤樣式 */
    .stLinkButton > a { background: linear-gradient(135deg, #4285F4 0%, #3367D6 100%) !important; color: white !important; border-radius: 12px !important; font-size: 22px !important; font-weight: 800 !important; padding: 0.8rem !important; text-align: center !important; display: block !important; border: none !important; box-shadow: 0 5px 15px rgba(66,133,244,0.3); } /* 設定搜尋按鈕的漸層色與陰影 */
    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; } /* 縮小網頁元件之間的垂直間距 */
    .stAlert { padding: 0.8rem 1rem !important; border-radius: 10px !important; } /* 調整摘要資訊框的內距與圓角 */
    </style>
    <div class="main-title">🚀 全球專利進階搜尋產生器</div>
    """, unsafe_allow_html=True)  # 透過 Markdown 注入 CSS 樣式並顯示主標題

# --- 4. 步驟 1: 填寫檢索條件 ---
st.markdown('<div class="step-text"><span class="step-num">1</span> 填寫條件 Fill Conditions</div>', unsafe_allow_html=True)  # 顯示步驟 1 標題

with st.container(border=True):  # 建立一個具有外框的容器，包裹所有輸入欄位
    c1, c2 = st.columns(2, gap="large")  # 建立左右兩欄，並設定較大的水平間距
    
    with c1:  # 處理左側欄位內容
        st.markdown('<span class="field-label">技術關鍵字 Technology Keywords</span>', unsafe_allow_html=True)  # 顯示關鍵字區塊標籤
        sk1, sk2 = st.columns(2)  # 將關鍵字輸入區再分為左右兩格
        kw1 = sk1.text_input("主", placeholder="例如: bipolar", key="k1", label_visibility="collapsed")  # 主要關鍵字輸入框，隱藏預設標籤
        kw2 = sk2.text_input("次", placeholder="例如: irrigation", key="k2", label_visibility="collapsed")  # 次要關鍵字輸入框，隱藏預設標籤
        ex_kw = st.checkbox("關鍵字精準比對 Exact Match", key="ek")  # 關鍵字是否加上雙引號的勾選框
        
        st.markdown('<span class="field-label">專利權人 (公司) Assignee / Company</span>', unsafe_allow_html=True)  # 顯示公司區塊標籤
        asg = st.text_input("公司", placeholder="例如: Medtronic", key="k3", label_visibility="collapsed")  # 公司名稱輸入框
        ex_as = st.checkbox("公司精準比對 Exact Assignee", value=True, key="ea")  # 公司名稱是否精準比對的勾選框
    
    with c2:  # 處理右側欄位內容
        st.markdown('<span class="field-label">發明人與分類 Inventor & CPC</span>', unsafe_allow_html=True)  # 顯示發明人與分類號標籤
        si1, si2 = st.columns(2)  # 分為左右兩格顯示發明人與 CPC
        inv = si1.text_input("人", placeholder="例如: MALIS", key="k5", label_visibility="collapsed")  # 發明人姓名輸入框
        cpc = si2.text_input("C", placeholder="例如: A61B18", key="k4", label_visibility="collapsed")  # CPC 分類號輸入框
        ex_iv = st.checkbox("發明人精準比對 Exact Inventor", value=True, key="ei")  # 發明人是否精準比對的勾選框
        
        st.markdown('<span class="field-label">每頁顯示筆數 Results Per Page</span>', unsafe_allow_html=True)  # 顯示設定筆數標籤
        limit = st.selectbox("筆", [10, 20, 50, 100], index=1, label_visibility="collapsed")  # 下拉選單選擇搜尋結果顯示筆數

# --- 5. 邏輯運算與網址組裝 ---
p = {}  # 建立一個字典，用於存放最終要傳送給 Google 的所有參數
k = []  # 建立一個列表，用於暫存清理後的關鍵字
ck1, ck2 = clean(kw1), clean(kw2)  # 呼叫清理函式處理兩組關鍵字
if ck1: k.append(f'"{ck1}"' if ex_kw else ck1)  # 如果有填寫主關鍵字，根據勾選決定是否包覆雙引號
if ck2: k.append(f'"{ck2}"' if ex_kw else ck2)  # 如果有填寫次關鍵字，根據勾選決定是否包覆雙引號
if k: p['q'] = " ".join(k)  # 如果關鍵字列表不為空，用空格合併後放入參數 q

if asg: p['assignee'] = f'"{clean(asg)}"' if ex_as else clean(asg)  # 清理公司名稱，並根據勾選決定是否包覆雙引號
if inv: p['inventor'] = f'"{clean(inv)}"' if ex_iv else clean(inv)  # 清理發明人，並根據勾選決定是否包覆雙引號
if cpc: p['cpc'] = clean(cpc)  # 如果有填寫 CPC 分類號，清理後存入參數字典
p['num'] = limit  # 將顯示筆數存入參數字典

# --- 6. 步驟 2: 確認摘要與開啟檢索 ---
if p:  # 如果參數字典內有任何填寫的內容
    st.markdown('<div class="step-text"><span class="step-num">2</span> 確認並搜尋 Confirm & Search</div>', unsafe_allow_html=True)  # 顯示步驟 2 標題
    
    info = []  # 建立摘要顯示用的文字列表
    if 'q' in p: info.append(f"🔍 **{p['q']}**")  # 加入關鍵字摘要
    if 'assignee' in p: info.append(f"🏢 **{p['assignee']}**")  # 加入公司名稱摘要
    if 'inventor' in p: info.append(f"👤 **{p['inventor']}**")  # 加入發明人摘要
    if 'cpc' in p: info.append(f"📂 **{p['cpc']}**")  # 加入分類號摘要
    
    st.info(" | ".join(info))  # 在網頁上顯示藍色背景的檢索條件摘要框

    url = f"https://patents.google.com/?{urllib.parse.urlencode(p)}"  # 將參數字典編碼為 URL 格式並串接成完整 Google Patents 網址
    st.link_button("🚀 確認條件並前往 Google Patents", url, use_container_width=True)  # 顯示寬版搜尋按鈕，點擊後開啟新分頁
else:  # 如果使用者尚未填寫任何欄位
    st.info("💡 請填寫上方欄位以產生檢索連結。")  # 顯示提示訊息引導填寫條件

# --- 7. 頁尾資訊 ---
st.markdown("<div style='text-align: center; color: #bbb; font-size: 11px; margin-top: 30px;'>全球專利進階搜尋產生器 v6.0 | Optimized Code Layout</div>", unsafe_allow_html=True)  # 顯示灰色的微型頁尾文字
