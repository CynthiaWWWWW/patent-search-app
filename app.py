import streamlit as st
import requests
import json
import urllib.parse

# 設定網頁標題
st.set_page_config(page_title="全球專利搜尋工具", page_icon="💡")

st.title("💡 全球專利 (USPTO) 搜尋儀表板")
st.markdown("當 API 繁忙時，系統將自動產生 Google Patents 快捷連結作為備援。")

# 側邊欄設定
with st.sidebar:
    st.header("搜尋參數")
    p_num_search = st.text_input("專利號碼 (例如 11500000)", "").strip()
    st.write("--- 或使用關鍵字搜尋 ---")
    p_keyword_1 = st.text_input("技術關鍵字 1", "Semiconductor").strip()
    p_keyword_2 = st.text_input("技術關鍵字 2 (選填)", "").strip()
    limit = st.slider("顯示筆數", 5, 50, 15)

def run_patent_search(pn, kw1, kw2, lmt):
    # --- 備援功能：產生 Google Patents 連結 ---
    # 如果是號碼搜尋
    if pn:
        fallback_url = f"https://patents.google.com/patent/US{pn}"
        st.info(f"📍 專利號直接連結預備完成。")
        st.markdown(f'<a href="{fallback_url}" target="_blank" style="font-size:20px; color:#4f46e5; font-weight:bold;">🚀 點此直接前往 Google Patents 查看專利 {pn}</a>', unsafe_allow_html=True)
    else:
        # 如果是關鍵字搜尋
        search_terms = f"{kw1} {kw2}".strip()
        encoded_terms = urllib.parse.quote(search_terms)
        fallback_url = f"https://patents.google.com/?q={encoded_terms}&num={lmt}"
        st.info(f"📍 備援搜尋連結已產生。")
        st.markdown(f'<a href="{fallback_url}" target="_blank" style="font-size:20px; color:#4f46e5; font-weight:bold;">🔍 點此在 Google Patents 搜尋 「{search_terms}」</a>', unsafe_allow_html=True)

    st.write("---")
    
    # --- 嘗試 API 連線 ---
    if pn:
        query = {"patent_number": pn}
    else:
        k_list = [k for k in [kw1, kw2] if k]
        if len(k_list) == 1:
            query = {"_text_any": {"patent_title": k_list[0]}}
        else:
            query = {"_and": [{"_text_any": {"patent_title": k_list[0]}}, {"_text_any": {"patent_title": k_list[1]}}]}
    
    fields = ["patent_number", "patent_title", "patent_date", "assignee_organization"]
    params = {"q": json.dumps(query), "f": json.dumps(fields), "o": json.dumps({"per_page": lmt})}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    with st.spinner('正在嘗試連線 USPTO 伺服器...'):
        try:
            # 嘗試抓取資料
            response = requests.get("https://api.patentsview.org/patents/query", params=params, headers=headers, timeout=10)
            
            # 如果成功，顯示精美卡片
            if response.status_code == 200:
                data = response.json()
                results = data.get('patents')
                if results:
                    st.success("成功從 API 抓取即時數據：")
                    for i, p in enumerate(results, 1):
                        p_id = p.get('patent_number')
                        p_title = p.get('patent_title')
                        p_date = p.get('patent_date')
                        st.markdown(f"""
                        <div style="border-left: 5px solid #6366f1; padding: 12px; margin-bottom: 10px; background-color: #f5f3ff; border-radius: 8px;">
                            <b>#{i} US {p_id}</b> | {p_date}<br>
                            <small>{p_title}</small><br>
                            <a href="https://patents.google.com/patent/US{p_id}" target="_blank">查看詳情</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("API 回傳空結果，請使用上方備援連結。")
            else:
                # 如果 API 失敗，不噴紅字，優雅地提醒
                st.warning(f"目前 USPTO 伺服器繁忙或維護中 (代碼: {response.status_code})。")
                st.write("請直接點擊上方的藍色連結，使用 Google Patents 進行查詢。")

        except Exception:
            st.warning("⚠️ API 連線暫時中斷。")
            st.write("這通常是 USPTO 的防火牆限制。別擔心，請使用上方的 **Google Patents 備援連結**。")

if st.sidebar.button("執行搜尋"):
    run_patent_search(p_num_search, p_keyword_1, p_keyword_2, limit)
