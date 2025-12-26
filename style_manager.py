import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 布局修正 (彻底解决标题被遮挡)
           ============================ */
        .block-container {{
            padding-top: 5rem !important; /* 留足空间给大标题 */
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }}
        
        /* 隐藏顶部红线，保留纯黑背景 */
        header {{
            visibility: hidden !important; 
            background-color: transparent !important;
        }} 

        /* 全局深色 */
        .stApp {{ background-color: #000000; }}
        
        /* ============================
           2. 强制字体覆盖 (解决小标题字体不对)
           ============================ */
        html, body, p, div, span, button, input, textarea, label,
        h1, h2, h3, h4, h5, h6 {{ 
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0; 
        }}
        
        /* 特别针对 Selectbox 的 Label */
        .stSelectbox label p {{
            font-size: 0.9rem !important;
            color: #888 !important;
        }}

        /* ============================
           3. 组件纯黑化 (Selectbox & Input)
           =========================== */
        /* 下拉框本体 */
        div[data-baseweb="select"] > div {{
            background-color: #0a0a0a !important; /* 纯黑背景 */
            border-color: #333 !important;       /* 深灰边框 */
            color: #eee !important;
        }}
        
        /* 输入框本体 */
        .stTextArea textarea, .stTextInput input {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
        }}
        
        /* 聚焦时的颜色 (去掉蓝光，改用灰白) */
        .stTextArea textarea:focus, .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within {{
            border-color: #666 !important;
            box-shadow: none !important;
        }}

        /* ============================
           4. 工业风按钮 (纯黑)
           =========================== */
        div.stButton > button {{
            background-color: #000000 !important;
            color: #ccc !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            transition: all 0.2s;
        }}
        div.stButton > button:hover {{
            background-color: #1a1a1a !important;
            border-color: #888 !important;
            color: #fff !important;
        }}
        
        /* 删除按钮特化 */
        div.stButton > button:contains("✕") {{
            border-color: #442222 !important;
            color: #884444 !important;
        }}
        div.stButton > button:contains("✕"):hover {{
            background-color: #330000 !important;
            border-color: #ff4444 !important;
            color: #ff4444 !important;
        }}
        
        /* ============================
           5. 侧边栏修复 (保留)
           =========================== */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }}
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"] *, [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] * {{ display: none !important; }}
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"], [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] {{
            border: 1px solid #333 !important; background-color: #111 !important; border-radius: 4px !important;
            width: 36px !important; height: 36px !important; display: flex !important; align-items: center !important; justify-content: center !important;
            position: fixed !important; left: 1rem !important; top: 0.5rem !important; z-index: 999999 !important;
        }}
        [data-testid="stHeader"] button::after {{ content: "" !important; display: block !important; width: 8px !important; height: 8px !important; border-top: 2px solid #888 !important; border-right: 2px solid #888 !important; }}
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"]::after {{ transform: rotate(45deg); }}
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"]::after {{ transform: rotate(-135deg); }}

    </style>
    """, unsafe_allow_html=True)
