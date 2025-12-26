import streamlit as st

def apply_pro_style():
    st.markdown("""
        <style>
        /* =============================================
           1. 布局重构 (Layout Reset)
           ============================================= */
        /* 消灭顶部巨大留白，让内容顶天立地 */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }
        
        /* 隐藏 Header 和 Footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* =============================================
           2. 按钮纯黑化 (Pure Black Buttons)
           ============================================= */
        div.stButton > button {
            background-color: #000000 !important; /* 纯黑 */
            color: #e0e0e0 !important;           /* 灰白字 */
            border: 1px solid #333333 !important; /* 深灰边框 */
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        div.stButton > button:hover {
            background-color: #1a1a1a !important; /* 悬停微亮 */
            border-color: #666666 !important;
            color: #ffffff !important;
        }
        
        div.stButton > button:active {
            background-color: #333333 !important; /* 点击反馈 */
        }
        
        /* =============================================
           3. 瀑布流标签云 (Multiselect Hacks)
           ============================================= */
        
        /* 核心：隐藏右侧那个危险的 "Clear all" (X) 按钮 */
        /* 防止用户手滑一键清空仓库 */
        button[title="Clear all"], div[role="button"][aria-label="Clear all"] {
            display: none !important;
        }
        
        /* 强制拉伸标签显示区域的高度 (80vh) */
        /* 让它变成一个巨大的落地窗 */
        div[data-baseweb="select"] > div:nth-child(2) {
             max-height: 82vh !important;
             overflow-y: auto !important;
             background-color: #000000 !important; /* 背景纯黑 */
             border: 1px solid #222 !important;
        }

        /* 标签(Tag)样式微调 */
        span[data-baseweb="tag"] {
            background-color: #161616 !important; /* 深灰标签 */
            border: 1px solid #333 !important;
            margin-top: 4px !important;
            margin-bottom: 4px !important;
        }
        
        /* 移除标签内的文字删除线效果，让它看起来更像实体 */
        span[data-baseweb="tag"] span {
            color: #ccc !important;
        }

        /* 隐藏输入框上方的 label 占位 */
        div[data-testid="stMultiSelect"] label {
            display: none;
        }
        
        /* =============================================
           4. 输入框 (Text Area) 极简风
           ============================================= */
        textarea {
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #eee !important;
        }
        textarea:focus {
            border-color: #555 !important;
            box-shadow: none !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
