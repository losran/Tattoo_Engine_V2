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

        /* Header 透明且不阻挡鼠标，但保持可见以承载按钮 */
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
           2. 恢复官方原生侧边栏按钮 (Native Sidebar Toggle)
           =========================== */
        
        /* 1. 选中侧边栏开关按钮 */
        [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarExpandedControl"] {{
            /* 关键：恢复点击 */
            pointer-events: auto !important; 
            cursor: pointer !important;
            
            /* 固定位置 (防止乱跑) */
            position: fixed !important; 
            left: 1rem !important; 
            top: 0.8rem !important;
            z-index: 999999 !important;
            
            /* 样式微调：适配黑背景 */
            background-color: transparent !important; /* 透明背景 */
            border: none !important; /* 去掉边框 */
            color: #d0d0d0 !important; /* 图标颜色改为浅灰 */
        }}
        
        /* 2. 鼠标悬停时给一点反应 */
        [data-testid="stSidebarCollapsedControl"]:hover, [data-testid="stSidebarExpandedControl"]:hover {{
            color: #fff !important;
            background-color: rgba(255,255,255,0.1) !important; /* 微微发亮 */
            border-radius: 4px !important;
        }}

        /* 3. 确保原生 SVG 图标显示出来 (之前被我隐藏了) */
        [data-testid="stSidebarCollapsedControl"] svg, [data-testid="stSidebarExpandedControl"] svg {{
            display: block !important;
            width: 24px !important;
            height: 24px !important;
        }}
        
        /* 4. 删除所有伪元素 (删除之前画箭头的代码) */
        [data-testid="stHeader"] button::after {{ content: none !important; }}

        /* ============================
           3. 侧边栏背景
           =========================== */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }}

        /* ============================
           4. 下拉菜单纯黑化
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
           5. 输入框 & 数字框 (纯黑+浅灰聚焦)
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
           6. 工业风按钮
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

    </style>
    """, unsafe_allow_html=True)
