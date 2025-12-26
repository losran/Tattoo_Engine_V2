import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 布局修正 (修复按钮点不到的问题)
           ============================ */
        .block-container {{
            padding-top: 4rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }}
        
        /* 🔴 关键修复：不要隐藏 Header，而是让它透明且“穿透” */
        header {{ 
            background-color: transparent !important;
            pointer-events: none !important; /* 让鼠标点击穿透 Header 背景 */
        }}
        
        /* 隐藏汉堡菜单和页脚，但不隐藏 Header 容器 */
        #MainMenu, footer, [data-testid="stDecoration"] {{ 
            visibility: hidden !important; 
            display: none !important;
        }} 

        /* 全局深色 */
        .stApp {{ background-color: #000000; }}
        html, body, p, div, span, button, input, textarea, label, h1, h2, h3, h4, h5, h6 {{ 
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0; 
        }}

        /* ============================
           2. 侧边栏按钮 (钉死在左上角)
           =========================== */
        /* 恢复按钮的鼠标响应 */
        [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarExpandedControl"] {{
            pointer-events: auto !important; /* 恢复点击 */
            cursor: pointer !important;
            visibility: visible !important;
            display: flex !important;
            
            /* 强制固定定位：永远浮在最上层 */
            position: fixed !important;
            top: 1.2rem !important;
            left: 1.2rem !important;
            z-index: 9999999 !important;
            
            /* 样式 */
            background-color: #000 !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            width: 36px !important;
            height: 36px !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* 隐藏按钮内部原本的 SVG 图标 */
        [data-testid="stSidebarCollapsedControl"] svg, [data-testid="stSidebarExpandedControl"] svg {{
            display: none !important;
        }}

        /* 纯 CSS 绘制箭头 (你的经典逻辑) */
        [data-testid="stSidebarCollapsedControl"]::after, [data-testid="stSidebarExpandedControl"]::after {{
            content: "" !important;
            display: block !important;
            width: 8px !important;
            height: 8px !important;
            border-top: 2px solid #888 !important;
            border-right: 2px solid #888 !important;
            transition: transform 0.2s;
        }}
        /* 箭头方向 */
        [data-testid="stSidebarCollapsedControl"]::after {{ transform: rotate(45deg); margin-left: -2px; }}
        [data-testid="stSidebarExpandedControl"]::after {{ transform: rotate(-135deg); margin-right: -2px; }}

        /* Hover 高亮 */
        [data-testid="stSidebarCollapsedControl"]:hover, [data-testid="stSidebarExpandedControl"]:hover {{
            border-color: #fff !important;
            background-color: #1a1a1a !important;
        }}
        [data-testid="stSidebarCollapsedControl"]:hover::after, [data-testid="stSidebarExpandedControl"]:hover::after {{
            border-color: #fff !important;
        }}

        /* ============================
           3. 下拉菜单纯黑化
           ============================ */
        div[data-baseweb="select"] > div {{
            background-color: #0a0a0a !important;
            border-color: #333 !important;
            color: #eee !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
        }}
        li[role="option"] {{ color: #ccc !important; }}
        li[role="option"]:hover {{ background-color: #1a1a1a !important; }}
        li[aria-selected="true"] {{ background-color: #222 !important; color: #fff !important; }}
        .stSelectbox label {{ display: none !important; }}

        /* ============================
           4. 输入框 & 数字框 (纯黑+浅灰聚焦)
           =========================== */
        .stTextArea textarea, .stTextInput input {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
            caret-color: #fff !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
        }}
        
        /* 聚焦状态：浅灰色边框，无红色阴影 */
        .stTextArea textarea:focus, .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within, div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
            border-color: #777 !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        /* ============================
           5. 工业风按钮
           =========================== */
        div.stButton > button {{
            background-color: #000000 !important;
            color: #ccc !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            transition: all 0.2s;
        }}
        div.stButton > button[kind="primary"] {{
            background-color: #000000 !important;
            border-color: #555 !important;
            color: #fff !important;
        }}
        div.stButton > button:hover, div.stButton > button[kind="primary"]:hover {{
            background-color: #1a1a1a !important;
            border-color: #888 !important;
            color: #fff !important;
        }}
        div.stButton > button:contains("✕") {{
            border-color: #331111 !important;
            color: #663333 !important;
            line-height: 1 !important;
        }}
        div.stButton > button:contains("✕"):hover {{
            background-color: #330000 !important;
            border-color: #ff4444 !important;
            color: #ff4444 !important;
        }}
        
        /* 侧边栏背景 */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }}

    </style>
    """, unsafe_allow_html=True)
