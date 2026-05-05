import streamlit as st
import requests
import json  # 引入 json 工具，用來正確格式化搜尋指令

# 設定網頁標題
st.set_page_config(page_title="全球專利搜尋工具", page_icon="💡")

st.title("💡 全球專利 (USPTO) 快速搜尋器")
st.markdown("透過 PatentsView API 查詢美國專利。支援雙關鍵字聯集搜尋。")

# 側邊欄設定
with st.sidebar:
    st.header("搜尋參數")
    p_num_search = st.text_input("專利號碼 (例如 11500000)", "").strip()
    st.write("--- 或使用關鍵字搜尋 ---")
    p_keyword_1 = st.text_input("技術關鍵字 1 (必填)", "Semiconductor").strip()
    p_keyword_2 = st.text_input("技術關鍵字 2 (選填)", "").strip()
    limit = st.slider("顯示筆數", 5, 50, 10)

# 核心搜尋功能
def run_patent_search(pn, kw1, kw2, lmt):
    # 1. 建立搜尋語法 (使用字典結構，再用 json.dumps 轉成字串，最安全)
    if pn:
        query_dict = {"patent_number": pn}
    else:
        k_list = [k for k in [kw1, kw2] if k]
        if not k_list:
            st.error("請輸入專利號碼或至少一個關鍵字！")
            return
        
        if len(k_list) == 1:
            query_dict = {"_text_any": {"patent_title": k_list[0]}}
        else:
            # 雙關鍵字 AND 邏輯
            query_dict = {
                "_and": [
                    {"_text_any": {"patent_title": k_list[0]}},
                    {"_text_any": {"patent_title": k_list[1]}}
                ]
            }
    
    # 2. 設定回傳欄位
    fields_list = ["patent_number", "patent_title", "patent_date", "assignee_organization", "patent_abstract"]
    
    # 3. 準備發送請求的參數
    base_url = "https://api.patentsview.org/patents/query"
    # 使用 json.dumps 確保所有的括號與引號都符合 API 規範
    params = {
        "q": json.dumps(query_dict),
        "f": json.dumps(fields_list),
        "o": json.dumps({"matched_row_count": True})
    }
    
    with st.spinner('正在從專利資料庫檢索中...'):
        try:
            # 發送請求
            response = requests.get(base_url, params=params, timeout=10)
            
            # --- 增加除錯機制：如果不是 200，印出原因 ---
            if response.status_code != 200:
                st.error(f"API 回傳錯誤 (狀態碼: {response.status_code})")
                st.write("這可能是因為關鍵字包含特殊字元，或是 API 伺服器暫時繁忙。")
                return
            
            # 嘗試解析 JSON
            data = response.json()
            results = data.get('patents')
            
            if not results:
                st.warning("查無結果。請嘗試更換關鍵字。")
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

        except json.JSONDecodeError:
            st.error("解析 API 回傳內容失敗 (非 JSON 格式)。請稍後再試。")
        except Exception as e:
            st.error(f"檢索發生非預期錯誤: {e}")

if st.sidebar.button("執行搜尋"):
    run_patent_search(p_num_search, p_keyword_1, p_keyword_2, limit)
