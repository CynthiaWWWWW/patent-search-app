import streamlit as st
import requests
import json

# 設定網頁標題
st.set_page_config(page_title="全球專利搜尋工具", page_icon="💡")

st.title("💡 全球專利 (USPTO) 快速搜尋器")
st.markdown("透過 PatentsView API 查詢美國專利。支援雙關鍵字篩選。")

# 側邊欄設定
with st.sidebar:
    st.header("搜尋參數")
    p_num_search = st.text_input("專利號碼 (例如 11500000)", "").strip()
    st.write("--- 或使用關鍵字搜尋 ---")
    p_keyword_1 = st.text_input("技術關鍵字 1 (必填)", "Semiconductor").strip()
    p_keyword_2 = st.text_input("技術關鍵字 2 (選填)", "").strip()
    limit = st.slider("顯示筆數", 5, 50, 15)

# 核心搜尋功能
def run_patent_search(pn, kw1, kw2, lmt):
    # 1. 建立搜尋邏輯 (Query Dictionary)
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
    fields = ["patent_number", "patent_title", "patent_date", "assignee_organization", "patent_abstract"]
    
    # 3. 準備 POST 請求的資料 (Payload)
    # 我們改用 POST 方式，這對複雜的 JSON 查詢更友善
    payload = {
        "q": query,
        "f": fields,
        "o": {"matched_row_count": True, "page": 1, "per_page": lmt}
    }
    
    api_url = "https://api.patentsview.org/patents/query"
    
    with st.spinner('正在與 USPTO 伺服器同步中...'):
        try:
            # 改用 POST 並直接傳送 json=payload
            response = requests.post(api_url, json=payload, timeout=20)
            
            # 如果伺服器掛了或繁忙，會傳回 500 或 503
            if response.status_code != 200:
                st.error(f"伺服器回應異常 (錯誤代碼: {response.status_code})")
                st.info("💡 提示：PatentsView 伺服器有時會暫時繁忙，請稍等 10 秒後再試一次。")
                return
            
            # 取得 JSON 結果
            data = response.json()
            results = data.get('patents')
            
            if not results:
                st.warning("查無結果，請嘗試簡化關鍵字。")
                return

            st.divider()
            st.success(f"搜尋完成！")

            for i, p in enumerate(results, 1):
                p_id = p.get('patent_number')
                p_title = p.get('patent_title')
                p_date = p.get('patent_date')
                assignees = p.get('assignees')
                assignee_name = assignees[0].get('assignee_organization') if assignees and assignees[0] else "個人/未註明組織"
                p_abstract = p.get('patent_abstract', '無摘要資訊')
                
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
                        <details style="margin-bottom: 10px; cursor: pointer; font-size: 0.95em; color: #444;">
                            <summary><b>查看專利摘要 (Abstract)</b></summary>
                            <p style="background: white; padding: 10px; border-radius: 4px; margin-top: 5px; border: 1px solid #ddd;">{p_abstract}</p>
                        </details>
                        <div style="margin-top: 12px;">
                            <a href="{google_url}" target="_blank" style="color: #4f46e5; font-weight: bold; text-decoration: underline;">👉 前往 Google Patents 查看全文</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"檢索出錯：{e}")
            st.write("這通常是伺服器暫時斷線，請過幾秒後重新點擊搜尋。")

if st.sidebar.button("執行搜尋"):
    run_patent_search(p_num_search, p_keyword_1, p_keyword_2, limit)
