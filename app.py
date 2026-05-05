import streamlit as st
import urllib.parse

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="Patent Search Dashboard", page_icon="💡", layout="wide")

# --- 2. 清理函式 (定義在最前面) ---
def super_clean(text):
    if text:
        # 移除括號、分號，並修剪空格
        return str(text).replace("(", "").replace(")", "").replace(";", "").strip()
    return ""

# --- 3. CSS 美化 ---
st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 700; color: #1E1E1E; margin-bottom: 15px; }
    .label-en { font-size: 12px; color: #666; display: block; margin-bottom: -5px; }
    </style>
    <div class="main-title">💡 全球專利進階搜尋儀表板</div>
    """, unsafe_allow_html=True)

# --- 4. 介面輸入區 (先定義變數) ---
st.markdown("### 🚀 Google Patents 指令產生器")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="label-en">Primary Keywords</span>', unsafe_allow_html=True)
        g_kw = st.text_input("主要技術關鍵字", placeholder="例如: Bipolar", key="g1")
        
        st.markdown('<span class="label-en">Secondary Keywords</span>', unsafe_allow_html=True)
        g_kw2 = st.text_input("次要技術/應用關鍵字", placeholder="例如: Electrosurgical", key="g1_2")
        
        st.markdown('<span class="label-en">Assignee / Company</span>', unsafe_allow_html=True)
        g_assignee = st.text_input("專利權人 (公司)", placeholder="例如: Medtronic", key="g2")
    
    with col2:
        st.markdown('<span class="label-en">CPC Classification</span>', unsafe_allow_html=True)
        g_cpc = st.text_input("CPC 分類號", placeholder="例如: A61B18/14", key="g3")

        st.markdown('<span class="label-en">Inventor Name</span>', unsafe_allow_html=True)
        g_inventor = st.text_input("發明人", placeholder="例如: Smith", key="g6")
        
        p_limit = st.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=1)

# --- 5. 邏輯處理區 (在變數定義之後才執行) ---
query_parts = []

# 使用 super_clean 確保每個欄位都沒括號
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

# 再次強制清理最終字串，確保萬無一失
final_query = " ".join(query_parts).replace("(", "").replace(")", "").strip()

# --- 6. 顯示與輸出 ---
if final_query:
    st.markdown("---")
    st.markdown("#### 🛠️ 生成的指令 (不含括號):")
    st.code(final_query, language="bash")
    
    encoded_query = urllib.parse.quote(final_query)
    google_url = f"https://patents.google.com/?q={encoded_query}&num={p_limit}"
    
    st.markdown(f"""
        <a href="{google_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #4285F4; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; border: 2px solid #3367d6;">
                🔍 點此前往 Google Patents 搜尋
            </div>
        </a>
    """, unsafe_allow_html=True)
else:
    st.info("💡 請填寫欄位以生成指令。")
