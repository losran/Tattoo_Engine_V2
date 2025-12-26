import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 布局修正
           ============================ */
        .block-container {{
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }}
        
        #MainMenu, footer {{ visibility: hidden !important; }} 

        /* Header 透明且不阻挡鼠标 */
        header {{ 
            visibility: visible !important;
            background-color: transparent !important;
            pointer-events: none !important;
        }}

        .stApp {{ background-color: #000000; }}
        
        /* 全局字体强制为 Poppins */
        html, body, p, div, span, button, input, textarea, label, h1, h2, h3, h4, h5, h6 {{ 
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0; 
        }}

        /* ============================
           2. 侧边栏按钮 (局部字体回滚)
           =========================== */
        
        /* 1. 选中侧边栏开关按钮 */
        [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarExpandedControl"] {{
            /* 关键：恢复点击 */
            pointer-events: auto !important; 
            cursor: pointer !important;
            
            /* 固定位置 */
            position: fixed !important; 
            left: 1rem !important; 
            top: 0.8rem !important;
            z-index: 999999 !important;
            
            /* 外观适配黑背景 */
            background-color: transparent !important;
            border: none !important;
            color: #999 !important; /* 默认浅灰 */
            
            /* 🔥 核心修复：局部恢复图标字体 🔥 */
            /* 告诉浏览器：这个按钮里的字，不是英文，是图标！ */
            font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        }}
        
        /* 2. 确保按钮内部的所有元素也继承这个图标字体 */
        [data-testid="stSidebarCollapsedControl"] *, [data-testid="stSidebarExpandedControl"] * {{
            font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        }}

        /* 3. 鼠标悬停效果 */
        [data-testid="stSidebarCollapsedControl"]:hover, [data-testid="stSidebarExpandedControl"]:hover {{
            color: #fff !important; /* 悬停变白 */
            background-color: rgba(255,255,255,0.1) !important;
            border-radius: 4px !important;
        }}

        /* ============================
           3. 侧边栏背景
           =========================== */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }}

        /* ============================
           4. 核心对齐锁死 (42px)
           =========================== */
        [data-testid="column"] {{ display: flex !important; align-items: flex-end !important; }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stButton"] button,
        .stTextInput input, 
        div[data-baseweb="select"] > div {{
            height: 42px !important; min-height: 42px !important; box-sizing: border-box !important;
        }}
        div[data-testid="stNumberInput"] label {{ display: none !important; }}
        div[data-testid="stNumberInput"] input {{ height: 42px !important; }}
        div[data-testid="stButton"] button p {{ line-height: 42px !important; margin: 0 !important; }}

        /* ============================
           5. 纯黑配色 (Inputs)
           =========================== */
        .stTextArea textarea, .stTextInput input, div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
            background-color: #0a0a0a !important; border: 1px solid #333 !important; color: #e0e0e0 !important;
        }}
        div[data-baseweb="select"] > div, ul[data-testid="stSelectboxVirtualDropdown"] {{
            background-color: #0a0a0a !important; border-color: #333 !important; color: #eee !important;
        }}
        li[role="option"]:hover {{ background-color: #1a1a1a !important; }}
        li[aria-selected="true"] {{ background-color: #222 !important; color: #fff !important; }}
        
        .stTextArea textarea:focus, .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within, div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
            border-color: #777 !important; box-shadow: none !important; outline: none !important;
        }}

        /* ============================
           6. 工业风按钮
           =========================== */
        div.stButton > button {{
            background-color: #000000 !important; color: #ccc !important; border: 1px solid #333 !important; border-radius: 4px !important; transition: all 0.2s;
        }}
        div.stButton > button:hover {{
            background-color: #1a1a1a !important; border-color: #fff !important; color: #fff !important;
        }}
        div.stButton > button[kind="primary"] {{
            background-color: #000000 !important; border-color: #555 !important; color: #fff !important;
        }}
        div.stButton > button:contains("✕") {{
            border-color: #331111 !important; color: #663333 !important; line-height: 1 !important;
        }}
        div.stButton > button:contains("✕"):hover {{
            background-color: #330000 !important; border-color: #ff4444 !important; color: #ff4444 !important;
        }}

        /* ============================
           7. 响应式适配
           =========================== */
        @media (max-width: 1024px) {{
            [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; gap: 10px !important; }}
            [data-testid="column"] {{ flex: 1 1 auto !important; min-width: 120px !important; }}
        }}
        @media (max-width: 768px) {{
            [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; }}
            [data-testid="column"], div[data-testid="stNumberInput"], div[data-testid="stButton"] {{ width: 100% !important; max-width: 100% !important; }}
            div[data-testid="stButton"] {{ margin-top: 5px !important; }}
        }}

    </style>
    """, unsafe_allow_html=True)
