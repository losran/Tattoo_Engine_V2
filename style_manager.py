import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* 1. 基础全局样式 */
        html, body, [class*="css"], font, span, div, h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, label {{
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0;
        }}
        .stApp {{ background-color: #000000; }}

        /* 2. 侧边栏与头部纯净化 */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; z-index: 99998 !important; }}
        [data-testid="stSidebarUserContent"] {{ padding-top: 3.5rem !important; }}
        [data-testid="stToolbarActions"], [data-testid="stStatusWidget"], [data-testid="stDecoration"] {{ display: none !important; }}
        header[data-testid="stHeader"] {{ background-color: rgba(0,0,0,0.8) !important; border-bottom: 1px solid #1a1a1a !important; height: 3.5rem !important; }}

        /* 3. 清除顶部幽灵文字并重绘箭头 */
        [data-testid="stHeader"] button[data-testid*="Sidebar"] * {{ display: none !important; }}
        [data-testid="stHeader"] button[data-testid*="Sidebar"] {{
            border: 1px solid #333 !important;
            background-color: #111 !important;
            width: 36px !important;
            height: 36px !important;
            position: relative !important;
        }}
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

        /* 4. 核心对齐锁死 (42px 绝对对齐) */
        [data-testid="column"] {{
            display: flex !important;
            align-items: flex-end !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stButton"] button {{
            height: 42px !important;
            min-height: 42px !important;
            box-sizing: border-box !important;
        }}
        div[data-testid="stNumberInput"] label {{ display: none !important; }}
        div[data-testid="stNumberInput"] input {{ height: 42px !important; }}
        div[data-testid="stButton"] button p {{ line-height: 42px !important; margin: 0 !important; }}

        /* =======================================================
           5. 响应式适配：解决平板与手机的重叠与换行
           ======================================================= */
        
        /* 平板端适配 (屏幕宽度小于 1024px) */
        @media (max-width: 1024px) {{
            /* 解决重叠：允许列自动换行，不再硬挤 */
            [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
                gap: 10px !important;
            }}
            /* 调节列宽度，防止按钮文字被挤爆 */
            [data-testid="column"] {{
                flex: 1 1 auto !important;
                min-width: 120px !important;
            }}
            div[data-testid="stButton"] button p {{
                font-size: 13px !important;
                white-space: nowrap !important;
            }}
        }}

        /* 手机端适配 (屏幕宽度小于 768px) */
        @media (max-width: 768px) {{
            /* 强制变成上下排列，解决一切水平对不齐的问题 */
            [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            [data-testid="column"], div[data-testid="stNumberInput"], div[data-testid="stButton"] {{
                width: 100% !important;
                max-width: 100% !important;
            }}
            /* 手机端按钮加一点间距 */
            div[data-testid="stButton"] {{
                margin-top: 5px !important;
            }}
        }}

        /* 基础组件配色 */
        :root {{ --primary-color: #C0C0C0 !important; }}
        .stButton > button {{ border: 1px solid #333 !important; background: #111 !important; color: #888 !important; }}
        .stButton > button:hover {{ border-color: #FFFFFF !important; color: #FFFFFF !important; }}
        .stTextArea textarea, .stTextInput input {{ background-color: #111111 !important; border: 1px solid #333333 !important; color: #e0e0e0 !important; }}
    </style>
