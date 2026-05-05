# --- 核心邏輯：強效清理版 ---
query_parts = []

# 清理函式 (確保完全沒有括號)
def super_clean(text):
    if text:
        return str(text).replace("(", "").replace(")", "").strip()
    return ""

if g_kw: 
    query_parts.append(super_clean(g_kw))
if g_kw2: 
    query_parts.append(super_clean(g_kw2))
if g_assignee: 
    query_parts.append(f'assignee:"{super_clean(g_assignee)}"')
if g_inventor: 
    query_parts.append(f'inventor:"{super_clean(g_inventor)}"')
if g_cpc: 
    query_parts.append(f'cpc:{super_clean(g_cpc)}')
if g_after: 
    query_parts.append(f'after:{g_after.strftime("%Y%m%d")}')
if g_before: 
    query_parts.append(f'before:{g_before.strftime("%Y%m%d")}')

# 【關鍵修正】確保最後合成的是純字串，且再次執行全局括號清理
final_query = " ".join(query_parts).replace("(", "").replace(")", "").strip()

# --- 顯示與跳轉按鈕 ---
if final_query:
    st.markdown("---")
    st.markdown("#### 🛠️ 生成的指令 (已強制移除括號):")
    st.code(final_query, language="bash")
    
    # 建立跳轉連結
    # 使用 safe='' 確保連 URL 編碼都不會出現括號的轉義字元
    encoded_query = urllib.parse.quote(final_query)
    google_url = f"https://patents.google.com/?q={encoded_query}&num={p_limit}"
    
    # HTML 按鈕
    st.markdown(f"""
        <a href="{google_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #4285F4; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; border: 2px solid #3367d6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                🔍 點此前往 Google Patents 搜尋
            </div>
        </a>
    """, unsafe_allow_html=True)
else:
    st.info("💡 請填寫欄位以生成指令。")
