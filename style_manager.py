import streamlit as st

def apply_pro_style():
    # 保持字体加载 (引入 Noto Sans SC 和 Poppins)
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* 1. 全局字体基础 */
        html, body, [class*="css"], font, span, div, h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, label {{
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0;
        }}

        /* 2. 侧边栏布局与防遮挡 */
        [data-testid="stSidebar"] {{ 
            background-color: #0a0a0a !important; 
            border-right: 1px solid #1a1a1a !important; 
            z-index: 99998 !important; 
        }}
        [data-testid="stSidebarUserContent"] {{ padding-top: 3.5rem !important; }}
        
        /* 3. 彻底隐藏 Streamlit 顶栏干扰元素 */
        [data-testid="stToolbar"], 
        [data-testid="stHeader"], 
        [data-testid="stDecoration"], 
        [data-testid="stStatusWidget"] {{
            visibility: hidden !important;
            height: 0 !important;
        }}
        
        /* 如果你想保留三条杠菜单但隐藏其他，可以用下面这个，否则上面那段会全隐藏 */
        /* header[data-testid="stHeader"] {{
            background-color: transparent !important;
            z-index: 100 !important;
        }}
        */

        /* 4. 按钮样式重绘 (Pro 风格) */
        .stButton > button {{ 
            border: 1px solid #333 !important; 
            background: #111 !important; 
            color: #888 !important; 
            border-radius: 6px !important; 
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{ 
            border-color: #FFFFFF !important; 
            color: #FFFFFF !important; 
            background: #222 !important;
        }}
        
        /* Primary 按钮 (高亮) */
        .stButton > button[kind="primary"] {{
            background: #e1e1e1 !important;
            color: #000 !important;
            border: 1px solid #fff !important;
        }}

        /* 5. 输入框黑化 */
        .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {{ 
            background-color: #111111 !important; 
            border: 1px solid #333333 !important; 
            color: #e0e0e0 !important; 
        }}
        
        /* 6. 背景全黑 */
        .stApp {{ background-color: #000000; }}
        
    </style>
    """, unsafe_allow_html=True)
