import streamlit as st
import requests
import json

# 設定網頁標題
st.set_page_config(page_title="全球專利搜尋工具", page_icon="💡")

st.title("💡 全球專利 (USPTO) 快速搜尋器")
st.markdown("透過 PatentsView API 查詢美國專利。")

# 側邊欄設定
with st.sidebar:
    st.header("搜尋參數")
    p_num_search = st.text_input("專利號碼 (例如 11500000)", "").strip()
    st.write("--- 或使用關鍵字搜尋 ---")
    p_keyword_1 = st.text_input("技術關鍵字 1 (必填)", "Semiconductor").strip()
    p_keyword_2 = st.text_input("技術關鍵字 2 (選填)", "").strip()
    limit = st.slider("顯示筆數", 5, 50, 15)

def run_patent_search(pn, kw1, kw2, lmt):
    # 1. 建立搜尋語法
    if pn:
        query = {"patent_number": pn}
    else:
        k_list = [k for k in [kw1, kw2] if k]
        if not k_list:
            st.error("請輸入號碼或關鍵字！")
            return
        if len(k_list) == 1:
            query = {"_text_any": {"patent_title": k_list[0]}}
        else:
            query = {"_and": [
                {"_text_any": {"patent_title": k_list[0]}},
                {"_text_any": {"patent_title": k_list[1]}}
            ]}
    
    # 2. 設定回傳欄位
    fields = ["patent_number", "patent_title", "patent_date", "assignee_organization"]
    
    # 3. 準備參數
    params = {
        "q": json.dumps(query),
        "f": json.dumps(fields),
        "o": json.dumps({"matched_row_count": True, "per_page": lmt})
    }
    
    # --- 關鍵修正：加入強大的瀏覽器偽裝標頭 ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",  # 強制要求回傳 JSON
        "Referer": "https://patentsview.org/query" # 偽裝來源網頁
    }
    
    api_url = "https://api.patentsview.org/patents/query"
    
    with st.spinner('正在從 USPTO 獲取數據...'):
        try:
            # 發送請求，加入 headers
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            
            # 如果還是回傳 HTML (非 200)，印出狀態碼
            if response.status_code != 200:
                st.error(f"⚠️ 伺服器拒絕連線 (錯誤碼: {response.status_code})")
                if response.status_code == 429:
                    st.warning("您搜尋得太快了，請等 30 秒後再試。")
                return

            # 嘗試解析
            try:
                data = response.json()
            except:
                st.error("❌ 伺服器傳回了不正確的資料。這通常是 API 正在維修或連線被阻擋。")
                return

            results = data.get('patents')
            if not results:
                st.warning("查無結果，請更換關鍵字再試。")
                return

            st.divider()
            st.success(f"搜尋完成！")

            for i, p in enumerate(results, 1):
                p_id = p.get('patent_number')
                p_title = p.get('patent_title', '無標題')
                p_date = p.get('patent_date', '無日期')
                
                assignees = p.get('assignees', [])
                assignee_name = "個人名義/未註明"
                if assignees and isinstance(assignees, list) and assignees[0]:
                    assignee_name = assignees[0].get('assignee_organization') or "個人名義"

                google_url = f"https://patents.google.com/patent/US{p_id}"

                st.markdown(f"""
                <div style="border-left: 5px solid #6366f1; padding: 15px; margin-bottom: 20px; background-color: #f5f3ff; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);">
                    <div style="display: flex; align-items: baseline; margin-bottom: 10px;">
                        <span style="background-color: #4f46e5; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 12px; font-size: 0.9em;">#{i}</span>
                        <span style="font-size: 1.25em; font-weight: 800; color: #1a1a1a;">
                            <span style="color: #555; font-weight: 600;">Patent Number:</span> US {p_id}
                        </span>
                    </div>
                    <div style="margin-left: 42px; line-height: 1.7; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 8px;">
                        <div style="margin-bottom: 4px;"><b>專利標題：</b> <span style="color: #333;">{p_title}</span></div>
                        <div style="margin-bottom: 4px;"><b>公告日期：</b> {p_date}</div>
                        <div style="margin-bottom: 10px;"><b>專利權人：</b> {assignee_name}</div>
                        <div style="margin-top: 12px;">
                            <a href="{google_url}" target="_blank" style="color: #4f46e5; font-weight: bold; text-decoration: underline;">👉 前往 Google Patents 查看全文</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"連線失敗：{e}")

if st.sidebar.button("執行搜尋"):
    run_patent_search(p_num_search, p_keyword_1, p_keyword_2, limit)
