import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 布局修正 (不再飞天，也不消失)
           ============================ */
        .block-container {{
            padding-top: 3rem !important; /* 留出标题空间 */
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }}
        
        /* 隐藏 Streamlit 自带的汉堡菜单和红条，但不隐藏我们自己的 st.title */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}} /* 隐藏顶部那条白线区域 */

        /* 全局深色 */
        .stApp {{ background-color: #000000; }}
        html, body, p, div, span {{ color: #d0d0d0; font-family: 'Poppins', 'Noto Sans SC', sans-serif; }}

        /* ============================
           2. 工业风按钮 (纯黑)
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
            border-color: #666 !important;
            color: #fff !important;
        }}
        
        /* 🔴 专门针对“删除(X)”按钮的特化样式 */
        /* 让它变成红色高亮，更像一个危险操作 */
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
           3. 输入框优化
           =========================== */
        .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
        }}
        
        /* ============================
           4. 侧边栏修复 (你的核心逻辑)
           =========================== */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }}
        
        /* 隐藏Ghost Text */
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"] *,
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] * {{
            display: none !important;
        }}
        
        /* 绘制箭头容器 */
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"],
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] {{
            border: 1px solid #333 !important;
            background-color: #111 !important;
            border-radius: 4px !important;
            width: 36px !important;
            height: 36px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            position: fixed !important; /* 固定位置，防止跑飞 */
            left: 1rem !important;
            top: 0.5rem !important;
            z-index: 999999 !important;
        }}

        /* 绘制箭头 */
        [data-testid="stHeader"] button::after {{
            content: "" !important;
            display: block !important;
            width: 8px !important;
            height: 8px !important;
            border-top: 2px solid #888 !important;
            border-right: 2px solid #888 !important;
        }}
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"]::after {{ transform: rotate(45deg); }}
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"]::after {{ transform: rotate(-135deg); }}

    </style>
    """, unsafe_allow_html=True)
