import streamlit as st

def apply_pro_style():
    # 字体加载
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ===========================
           1. 全局字体与配色
           =========================== */
        html, body, [class*="css"], font, span, div, h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, label {{
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0;
        }}
        .stApp {{ background-color: #000000; }}

        /* ===========================
           2. 侧边栏 (Sidebar)
           =========================== */
        [data-testid="stSidebar"] {{ 
            background-color: #0a0a0a !important; 
            border-right: 1px solid #1a1a1a !important; 
        }}
        [data-testid="stSidebarUserContent"] {{ padding-top: 2rem !important; }}

        /* ===========================
           3. 关键修复：顶部导航栏 (Header) 🚑
           =========================== */
        
        /* A. 不要隐藏 Header 本身，而是让它变透明 & 允许鼠标穿透 */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            border-bottom: none !important;
            pointer-events: none !important; /* 让点击穿透空白区域，不挡下面内容 */
            height: 3rem !important;
        }}

        /* B. 只隐藏 Header 里的杂项 (右侧菜单、彩条、运行状态) */
        [data-testid="stDecoration"], 
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"] {{
            display: none !important;
        }}

        /* C. 复活“展开/收起”按钮！并赋予它实体 */
        header[data-testid="stHeader"] button[data-testid*="stSidebar"] {{
            pointer-events: auto !important; /* 恢复按钮可点击 */
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            border: 1px solid #333 !important;
            background-color: #111 !important;
            width: 42px !important;
            height: 42px !important;
            border-radius: 8px !important;
            position: relative !important;
            z-index: 999999 !important; /* 确保浮在最上层 */
            margin-top: 4px !important;
        }}

        /* ===========================
           4. 按钮美化 (画箭头)
           =========================== */
        
        /* 隐藏原生图标 */
        header[data-testid="stHeader"] button[data-testid*="stSidebar"] svg {{
            display: none !important;
        }}
        
        /* 用 CSS 画一个干净的箭头 */
        header[data-testid="stHeader"] button[data-testid*="stSidebar"]::after {{
            content: "" !important;
            display: block !important;
            width: 10px !important;
            height: 10px !important;
            border-right: 2px solid #888 !important;
            border-top: 2px solid #888 !important;
            transition: transform 0.2s;
        }}

        /* 收起时：箭头向右 (提示展开) */
        header[data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"]::after {{
            transform: rotate(45deg);
            margin-left: -3px;
        }}
        
        /* 展开时：箭头向左 (提示收起) */
        header[data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"]::after {{
            transform: rotate(-135deg);
            margin-left: 2px;
        }}

        /* 悬停高亮 */
        header[data-testid="stHeader"] button[data-testid*="stSidebar"]:hover {{
            border-color: #fff !important;
            background-color: #222 !important;
        }}
        header[data-testid="stHeader"] button[data-testid*="stSidebar"]:hover::after {{
            border-color: #fff !important;
        }}

        /* ===========================
           5. 其他组件样式
           =========================== */
        .stButton > button {{ border: 1px solid #333 !important; background: #111 !important; color: #888 !important; }}
        .stButton > button[kind="primary"] {{ background: #e1e1e1 !important; color: #000 !important; }}
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{ 
            background-color: #111 !important; border: 1px solid #333 !important; color: #fff !important; 
        }}

    </style>
    """, unsafe_allow_html=True)
