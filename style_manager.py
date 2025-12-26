import streamlit as st

def apply_pro_style():
    # 保持字体加载
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* =======================================================
           1. 全局布局修正 (Layout Fix) - 修复“飞天”问题
           ======================================================= */
        /* 之前是 1rem 太挤了，现在改为 3.5rem，正好给顶部留出呼吸空间 */
        .block-container {{
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }}
        
        /* 全局字体与深色背景 */
        html, body, [class*="css"], font, span, div, h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, label {{
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0;
        }}
        
        /* 侧边栏布局与防遮挡 (保留你的原版逻辑) */
        [data-testid="stSidebar"] {{ background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; z-index: 99998 !important; }}
        [data-testid="stSidebarUserContent"] {{ padding-top: 3.5rem !important; }}
        [data-testid="stLogo"] {{ height: auto !important; z-index: 99999 !important; }}

        /* =======================================================
           2. 侧边栏按钮核心修复 (你的核心逻辑 - 完整保留)
           ======================================================= */
        /* 抹除 ghost text */
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"] *,
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] * {{
            display: none !important;
            font-size: 0 !important;
            color: transparent !important;
            width: 0 !important;
            height: 0 !important;
        }}

        /* 按钮容器重绘 */
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"],
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"] {{
            border: 1px solid #333 !important;
            background-color: #111 !important;
            border-radius: 4px !important;
            width: 36px !important;
            height: 36px !important;
            position: relative !important;
            z-index: 100000 !important;
            margin-top: 0px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* 纯 CSS 箭头绘制 */
        [data-testid="stHeader"] button::after {{
            content: "" !important;
            display: block !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            width: 8px !important;
            height: 8px !important;
            border-top: 2px solid #888 !important;
            border-right: 2px solid #888 !important;
            transition: all 0.2s ease !important;
        }}

        /* 箭头旋转逻辑 */
        [data-testid="stHeader"] button[data-testid="stSidebarCollapsedControl"]::after {{
            transform: translate(-65%, -50%) rotate(45deg) !important; 
        }}
        [data-testid="stHeader"] button[data-testid="stSidebarExpandedControl"]::after {{
            transform: translate(-35%, -50%) rotate(-135deg) !important;
        }}

        /* Hover 反馈 */
        [data-testid="stHeader"] button:hover {{ border-color: #fff !important; background-color: #222 !important; }}
        [data-testid="stHeader"] button:hover::after {{ border-color: #fff !important; }}
        
        /* Header 背景半透明化，防止遮挡内容 */
        header[data-testid="stHeader"] {{ 
            background-color: rgba(0,0,0,0.8) !important; 
            border-bottom: 1px solid #1a1a1a !important; 
            height: 3.5rem !important; 
        }}
        
        /* 隐藏无用的系统组件 */
        [data-testid="stToolbarActions"], [data-testid="stStatusWidget"], [data-testid="stDecoration"] {{ display: none !important; }}

        /* =======================================================
           3. 工业风组件升级 (新增：纯黑按钮 + 输入框)
           ======================================================= */
        .stApp {{ background-color: #000000; }}

        /* 纯黑按钮 */
        div.stButton > button {{
            background-color: #000000 !important;
            color: #e0e0e0 !important;
            border: 1px solid #333333 !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        div.stButton > button:hover {{
            background-color: #1a1a1a !important;
            border-color: #666666 !important;
            color: #ffffff !important;
        }}
        div.stButton > button:active {{
            background-color: #333333 !important;
        }}

        /* 输入框极简风 */
        .stTextArea textarea, .stTextInput input {{
            background-color: #0a0a0a !important; 
            border: 1px solid #333 !important; 
            color: #e0e0e0 !important;
        }}
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: #555 !important;
            box-shadow: none !important;
        }}

        /* =======================================================
           4. 瀑布流标签云特化 (新增：防止误删 + 视觉优化)
           ======================================================= */
        
        /* 🔴 核心：隐藏右侧那个危险的 "Clear all" (X) 按钮 */
        button[title="Clear all"], div[role="button"][aria-label="Clear all"] {{
            display: none !important;
        }}
        
        /* 强制拉伸标签区域高度 (80vh)，利用屏幕垂直空间 */
        div[data-baseweb="select"] > div:nth-child(2) {{
             max-height: 80vh !important;
             min-height: 400px !important;
             overflow-y: auto !important;
             background-color: #0a0a0a !important;
             border: 1px solid #222 !important;
        }}

        /* 标签(Tag)样式微调 */
        span[data-baseweb="tag"] {{
            background-color: #161616 !important;
            border: 1px solid #333 !important;
            margin-top: 4px !important;
            margin-bottom: 4px !important;
        }}
        
        /* 隐藏输入框上方的 label 占位 */
        div[data-testid="stMultiSelect"] label {{
            display: none;
        }}
    </style>
    """, unsafe_allow_html=True)
