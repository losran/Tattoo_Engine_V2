import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* =======================================================
           1. 基础全局样式 (Global)
           ======================================================= */
        html, body, [class*="css"], font, span, div, h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, label {{
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0;
        }}
        .stApp {{ background-color: #000000; }}
        
        /* 布局容器修正 */
        .block-container {{
            padding-top: 3.5rem !important; /* 留出顶部空间 */
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }}

        /* =======================================================
           2. 侧边栏与头部纯净化 (Header & Sidebar)
           ======================================================= */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; z-index: 99998 !important; }}
        [data-testid="stSidebarUserContent"] {{ padding-top: 3.5rem !important; }}
        
        /* 隐藏顶部红线和多余组件 */
        [data-testid="stToolbarActions"], [data-testid="stStatusWidget"], [data-testid="stDecoration"] {{ display: none !important; }}
        footer {{ display: none !important; }}
        
        /* 头部背景透明，但允许点击穿透 */
        header[data-testid="stHeader"] {{ 
            background-color: transparent !important; 
            border-bottom: none !important; 
            height: 3.5rem !important; 
            pointer-events: none !important; /* 关键：让鼠标穿透Header空白处 */
        }}

        /* =======================================================
           3. 侧边栏按钮修复 (你的核心代码 + 点击恢复)
           ======================================================= */
        /* 清除顶部幽灵文字 */
        [data-testid="stHeader"] button[data-testid*="Sidebar"] * {{ display: none !important; }}
        
        /* 重绘按钮容器 */
        [data-testid="stHeader"] button[data-testid*="Sidebar"] {{
            border: 1px solid #333 !important;
            background-color: #000 !important; /* 纯黑 */
            width: 36px !important;
            height: 36px !important;
            position: relative !important;
            pointer-events: auto !important; /* 关键：恢复按钮点击 */
            z-index: 999999 !important;
        }}
        
        /* 鼠标悬停效果 */
        [data-testid="stHeader"] button[data-testid*="Sidebar"]:hover {{
            background-color: #1a1a1a !important;
            border-color: #fff !important;
        }}

        /* 纯CSS绘制箭头 */
        [data-testid="stHeader"] button[data-testid*="Sidebar"]::after {{
            content: "" !important;
            display: block !important;
            position: absolute !important;
            top: 50% !important; left: 50% !important;
            width: 8px !important; height: 8px !important;
            border-top: 2px solid #888 !important;
            border-right: 2px solid #888 !important;
        }}
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"]::after {{ transform: translate(-65%, -50%) rotate(45deg) !important; }}
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"]::after {{ transform: translate(-35%, -50%) rotate(-135deg) !important; }}

        /* =======================================================
           4. 核心对齐锁死 (42px 绝对对齐) - 保留你的逻辑
           ======================================================= */
        [data-testid="column"] {{
            display: flex !important;
            align-items: flex-end !important; /* 底部对齐 */
        }}
        
        /* 强制所有输入框和按钮高度一致 */
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stButton"] button,
        .stTextInput input, 
        div[data-baseweb="select"] > div {{
            height: 42px !important;
            min-height: 42px !important;
            box-sizing: border-box !important;
        }}
        
        /* 隐藏 Label 占位 */
        div[data-testid="stNumberInput"] label {{ display: none !important; }}
        div[data-testid="stNumberInput"] input {{ height: 42px !important; }}
        div[data-testid="stButton"] button p {{ line-height: 42px !important; margin: 0 !important; }}

        /* =======================================================
           5. 纯黑工业配色注入 (Black Theme Injection)
           ======================================================= */
        
        /* 输入框 & 文本域 */
        .stTextArea textarea, .stTextInput input, div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
        }}
        
        /* 下拉框 (静态+弹窗) */
        div[data-baseweb="select"] > div {{
            background-color: #0a0a0a !important;
            border-color: #333 !important;
            color: #eee !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
        }}
        li[role="option"]:hover {{ background-color: #1a1a1a !important; }}
        li[aria-selected="true"] {{ background-color: #222 !important; color: #fff !important; }}
        
        /* 聚焦去红光 (改为浅灰) */
        .stTextArea textarea:focus, .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within, div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
            border-color: #777 !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        /* 按钮样式 */
        div.stButton > button {{
            background-color: #000000 !important;
            color: #ccc !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
        }}
        div.stButton > button:hover {{
            background-color: #1a1a1a !important;
            border-color: #fff !important;
            color: #fff !important;
        }}
        /* Primary 按钮也变黑 */
        div.stButton > button[kind="primary"] {{
            background-color: #000000 !important;
            border-color: #555 !important;
            color: #fff !important;
        }}

        /* =======================================================
           6. 响应式适配 (Tablet & Mobile) - 保留你的逻辑
           ======================================================= */
        @media (max-width: 1024px) {{
            [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
                gap: 10px !important;
            }}
            [data-testid="column"] {{
                flex: 1 1 auto !important;
                min-width: 120px !important;
            }}
        }}

        @media (max-width: 768px) {{
            [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            [data-testid="column"], div[data-testid="stNumberInput"], div[data-testid="stButton"] {{
                width: 100% !important;
                max-width: 100% !important;
            }}
            div[data-testid="stButton"] {{
                margin-top: 5px !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)
