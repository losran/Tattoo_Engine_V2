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
            padding-top: 4rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }}
        
        #MainMenu, footer {{ visibility: hidden !important; }} 

        header {{ 
            visibility: visible !important;
            background-color: transparent !important;
            pointer-events: none !important;
        }}

        .stApp {{ background-color: #000000; }}
        html, body, p, div, span, button, input, textarea, label, h1, h2, h3, h4, h5, h6 {{ 
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0; 
        }}

        /* ============================
           2. 下拉菜单纯黑化
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
           3. 输入框 & 数字框 (去红修正)
           =========================== */
        .stTextArea textarea, .stTextInput input {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
            caret-color: #fff !important; 
        }}
        
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: #777 !important; 
            box-shadow: none !important;    
            outline: none !important;
        }}

        div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
            border-color: #777 !important; 
            box-shadow: none !important;
            caret-color: #fff !important;
        }}

        div[data-baseweb="select"] > div:focus-within {{
            border-color: #777 !important;
            box-shadow: none !important;
        }}

        /* ============================
           4. 工业风按钮
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

        /* ============================
           5. 侧边栏修复
           =========================== */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }}
        
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"] *, [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] * {{ display: none !important; }}
        
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"], [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] {{
            border: 1px solid #333 !important; 
            background-color: #111 !important; 
            border-radius: 4px !important;
            width: 36px !important; 
            height: 36px !important; 
            display: flex !important; 
            align-items: center !important; 
            justify-content: center !important;
            
            pointer-events: auto !important; 
            cursor: pointer !important;
            
            position: fixed !important; 
            left: 1rem !important; 
            top: 0.8rem !important; 
            z-index: 999999 !important;
        }}
        
        [data-testid="stHeader"] button::after {{ content: "" !important; display: block !important; width: 8px !important; height: 8px !important; border-top: 2px solid #888 !important; border-right: 2px solid #888 !important; }}
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"]::after {{ transform: rotate(45deg); }}
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"]::after {{ transform: rotate(-135deg); }}

        /* ============================
           6. Text Studio 画廊特调 (Gallery CSS)
           ============================ */
        /* 隐藏 Checkbox 的文字标签 (仅留框) */
        div[data-testid="stCheckbox"] label {{ display: none !important; }}
        
        /* 让勾选框“浮”在图片左上角 */
        div[data-testid="stCheckbox"] {{
            margin-bottom: -40px !important; /* 负边距上移 */
            margin-left: 5px !important;     /* 左边距 */
            padding-top: 5px !important;
            z-index: 99 !important;          /* 确保在顶层 */
            position: relative;
            width: 30px !important;          /* 限制点击热区 */
        }}
        
        /* 图片容器优化 */
        div[data-testid="stImage"] {{
            padding-top: 0px !important;
        }}
        div[data-testid="stImage"] img {{
            border-radius: 8px !important;
            transition: transform 0.2s !important;
        }}
        /* 鼠标悬停放大特效 */
        div[data-testid="stImage"] img:hover {{
            transform: scale(1.02) !important;
            z-index: 10 !important;
        }}

    </style>
    """, unsafe_allow_html=True)
