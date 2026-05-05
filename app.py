import streamlit as st  # 匯入網頁製作工具
import requests  # 匯入資料請求工具

# 設定網頁標題
st.set_page_config(page_title="全球專利搜尋工具", page_icon="💡")

# 網頁大標題
st.title("💡 全球專利 (USPTO) 快速搜尋器")
st.markdown("透過 PatentsView API 查詢美國專利資訊。輸入專利號碼或技術關鍵字。")

# 側邊欄設定
with st.sidebar:
    st.header("搜尋參數")
    # 專利號碼搜尋
    p_num_search = st.text_input("專利號碼 (例如 11500000)", "").strip()
    st.write("--- 或使用關鍵字搜尋 ---")
    # 關鍵字搜尋
    p_keyword = st.text_input("技術關鍵字 (例如 Laser)", "Semiconductor")
    # 數量選擇
    limit = st.slider("顯示筆數", 5, 50, 10)
    st.info("提示：專利資料庫極其龐大，建議關鍵字精確一點。")

# 核心搜尋功能
def run_patent_search(pn, kw, lmt):
    # 建立搜尋邏輯
    if pn:
        # 如果有號碼，精確搜尋專利號
        query = f'{{"patent_number":"{pn}"}}'
    else:
        # 如果沒號碼，搜尋專利標題中包含的關鍵字
        query = f'{{"_text_any":{{"patent_title":"{kw}"}}}}'
    
    # 設定要回傳的欄位
    fields = '["patent_number","patent_title","patent_date","assignee_organization","patent_abstract"]'
    # 組合 API 網址 (PatentsView)
    api_url = f"https://api.patentsview.org/patents/query?q={query}&f={fields}&o={{\\"matched_row_count\\":true}}"
    
    with st.spinner('正在從專利資料庫檢索中...'):
        try:
            response = requests.get(api_url)
            if response.status_code != 200:
                st.warning("找不到符合條件的專利，請確認號碼或關鍵字。")
                return
            
            data = response.json()
            results = data.get('patents')
            
            if not results:
                st.warning("查無結果。")
                return

            st.divider()
            st.success(f"搜尋完成！找到相關專利：")

            # 顯示結果卡片
            for i, p in enumerate(results, 1):
                p_id = p.get('patent_number')
                p_title = p.get('patent_title')
                p_date = p.get('patent_date')
                # 取得專利權人 (廠商)，若無則顯示個人
                assignee = p.get('assignees')[0].get('assignee_organization') if p.get('assignees') else "個人/未註明"
                p_abstract = p.get('patent_abstract', '無摘要資訊')
                
                # 建立外部連結 (Google Patents 最好用，連結最穩)
                google_patent_url = f"https://patents.google.com/patent/US{p_id}"

                # --- HTML 介面：維持 510(k) 的大字體風格 ---
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
                        <div style="margin-bottom: 10px;"><b>專利權人：</b> {assignee}</div>
                        
                        <details style="margin-bottom: 10px; cursor: pointer; font-size: 0.95em; color: #444;">
                            <summary><b>查看專利摘要 (Abstract)</b></summary>
                            <p style="background: white; padding: 10px; border-radius: 4px; margin-top: 5px; border: 1px solid #ddd;">{p_abstract}</p>
                        </details>

                        <div style="margin-top: 12px;">
                            <a href="{google_patent_url}" target="_blank" style="color: #4f46e5; font-weight: bold; text-decoration: underline;">👉 前往 Google Patents 查看全文與 PDF</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"檢索出錯: {e}")

# 按鈕啟動
if st.sidebar.button("執行搜尋"):
    run_patent_search(p_num_search, p_keyword, limit)
