import streamlit as st
import sys
import os
import random
import time

# ===========================
# 0. 基础设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = set()

# ===========================
# 1. 核心 CSS：实现自动换行的瀑布流
# ===========================
st.markdown("""
<style>
    /* 1. 强制列容器允许换行 (关键) */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        align-items: flex-start !important; /* 顶部对齐，形成瀑布流错落感 */
    }

    /* 2. 设定列的“底线”宽度 */
    [data-testid="column"] {
        min-width: 140px !important;  /* 手机上正好放下2列 */
        flex: 1 1 auto !important;    /* 允许拉伸填满空隙 */
        max-width: 100% !important;   /* 解除最大宽度限制 */
    }

    /* 3. 卡片样式：紧凑、黑底 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0px !important;
        background-color: #0a0a0a;
        border: 1px solid #222;
        overflow: hidden;
        margin-bottom: 12px; /* 卡片之间的垂直间距 */
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #666;
    }

    /* 4. 图片：无缝 */
    div[data-testid="stImage"] {
        margin-bottom: 0px !important;
    }
    div[data-testid="stImage"] img {
        border-radius: 0px !important;
        width: 100%;
        display: block;
    }

    /* 5. 标题(文件名)优化 */
    div[data-testid="stTextInput"] {
        padding: 4px 0px;
        background-color: #0e0e0e;
    }
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        color: #eee !important;
        font-size: 13px !important; /* 字体加大 */
        font-weight: 600 !important; /* 加粗 */
        text-align: center;
        height: 28px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        background-color: #222 !important;
    }

    /* 6. 按钮组：无缝拼接 */
    button {
        border-radius: 0px !important;
        border: none !important;
        margin: 0px !important;
        width: 100%;
        white-space: nowrap !important; /* 禁止文字换行 */
    }
    
    /* 选中按钮 (左) */
    button[kind="primary"] {
        background-color: #1b3a1b !important;
        color: #4CAF50 !important;
        font-weight: 700 !important;
        height: 38px !important;
    }
    button[kind="primary"]:hover {
        background-color: #2e6b2e !important;
        color: #fff !important;
    }
    
    button[kind="secondary"] {
        background-color: #111 !important;
        color: #888 !important;
        height: 38px !important;
        border-top: 1px solid #222 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #222 !important;
        color: #ddd !important;
    }

    /* 删除按钮 (右) */
    div[data-testid="column"]:nth-of-type(2) button[kind="secondary"] {
        border-left: 1px solid #222 !important;
    }
    div[data-testid="column"]:nth-of-type(2) button[kind="secondary"]:hover {
        background-color: #330000 !important;
        color: #ff4444 !important;
    }
    
    /* 隐藏全屏按钮 */
    button[title="View fullscreen"] { display: none; }

</style>
""", unsafe_allow_html=True)

# ===========================
# 2. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
raw_keys = list(db.keys())
available_langs = [k for k in raw_keys if k.startswith("Text_")]
if not available_langs: available_langs = ["Text_English"]

# ===========================
# 3. 顶部上传
# ===========================
st.markdown("## Text Studio")

uploaded_file = st.file_uploader(
    "Upload", 
    type=['jpg', 'png', 'jpeg', 'webp'],
    key=f"uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    save_dir = "images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state.uploader_key += 1
    st.session_state.selected_assets.add(uploaded_file.name)
    st.toast(f"✅ Saved")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 4. 自动瀑布流画廊 (Masonry Gallery)
# ===========================
c_head, c_stat = st.columns([3, 1])
with c_head:
    st.subheader("Visual Library")

# 获取图片
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
all_files = [v for v in raw_map.values() if v]
full_paths = [(f, os.path.join("images", f)) for f in all_files]
valid_files = [x for x in full_paths if os.path.exists(x[1])]
valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
sorted_image_files = [x[0] for x in valid_files]

st.session_state.selected_assets = {f for f in st.session_state.selected_assets if f in sorted_image_files}

if not sorted_image_files:
    st.info("Library is empty.")
else:
    # 🔥 核心逻辑：创建 6 个固定的垂直列 🔥
    # Python 负责垂直分发 (Masonry Logic)
    # CSS 负责水平折叠 (Responsive Logic)
    
    NUM_COLS = 6
    cols = st.columns(NUM_COLS)
    
    for idx, file_name in enumerate(sorted_image_files):
        # 算法：依次把图片放入第 0, 1, 2, 3, 4, 5 列，然后循环
        # 这样每一列都会积累图片，形成垂直堆叠
        col_index = idx % NUM_COLS
        file_path = os.path.join("images", file_name)
        
        with cols[col_index]:
            # === 卡片开始 ===
            with st.container(border=True):
                # 1. 图片
                st.image(file_path, use_container_width=True)
                
                # 2. 标题 (文件名) - 可编辑
                name_body, ext = os.path.splitext(file_name)
                new_name_body = st.text_input(
                    "n",
                    value=name_body,
                    key=f"n_{file_name}",
                    label_visibility="collapsed"
                )
                if new_name_body != name_body:
                    try:
                        new_full_name = new_name_body + ext
                        os.rename(file_path, os.path.join("images", new_full_name))
                        if file_name in st.session_state.selected_assets:
                            st.session_state.selected_assets.remove(file_name)
                            st.session_state.selected_assets.add(new_full_name)
                        st.rerun()
                    except: pass
                
                # 3. 操作栏
                c_sel, c_del = st.columns([3, 1], gap="small")
                
                is_selected = file_name in st.session_state.selected_assets
                
                with c_sel:
                    # 选中按钮
                    if is_selected:
                        if st.button("✅ Active", key=f"s_{file_name}", type="primary", use_container_width=True):
                            st.session_state.selected_assets.remove(file_name)
                            st.rerun()
                    else:
                        if st.button("Select", key=f"s_{file_name}", type="secondary", use_container_width=True):
                            st.session_state.selected_assets.add(file_name)
                            st.rerun()
                
                with c_del:
                    # 删除按钮
                    if st.button("🗑", key=f"d_{file_name}", type="secondary", use_container_width=True, help="Delete"):
                        try:
                            os.remove(file_path)
                            if file_name in st.session_state.selected_assets:
                                st.session_state.selected_assets.remove(file_name)
                            st.rerun()
                        except: pass
            # === 卡片结束 ===

# 状态统计
with c_stat:
    count = len(st.session_state.selected_assets)
    if count > 0:
        st.markdown(f"<div style='text-align:right; color:#4CAF50; padding-top:10px;'>✅ <b>{count}</b> Selected</div>", unsafe_allow_html=True)

st.divider()

# ===========================
# 5. 生成控制区
# ===========================
c_lang, c_font, c_qty, c_go = st.columns([1, 1, 0.8, 1])
with c_lang:
    target_lang = st.selectbox("Lang", available_langs, label_visibility="collapsed")
with c_font:
    selected_font = st.selectbox("Font", ["Random"] + font_list, label_visibility="collapsed")
with c_qty:
    qty = st.number_input("Qty", 1, 10, 4, label_visibility="collapsed")
with c_go:
    run_btn = st.button("🚀 GENERATE", type="primary", use_container_width=True)

manual_word = st.text_input("Custom Text", placeholder="Input text here (Optional)...", label_visibility="collapsed")

# ===========================
# 6. 生成逻辑
# ===========================
if run_btn:
    try:
        with st.spinner("Processing..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]
            active_pool = list(st.session_state.selected_assets)

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                if active_pool:
                    img_val = random.choice(active_pool)
                
                font = selected_font if selected_font != "Random" else random.choice(font_list)
                url_part = f"{img_val} " if img_val else ""
                prompt_text = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
                
                results.append({
                    "image_file": img_val,
                    "prompt_text": prompt_text
                })
            
            st.session_state.text_solutions = results
            time.sleep(0.3)
            st.rerun()
            
    except Exception as e:
        st.error(str(e))

# ===========================
# 7. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("Results")
    
    for item in st.session_state.text_solutions:
        with st.container(border=True):
            col_img, col_text = st.columns([1, 4])
            
            with col_img:
                if item["image_file"]:
                    full_path = os.path.abspath(os.path.join("images", item["image_file"]))
                    if os.path.exists(full_path):
                        st.image(full_path, use_container_width=True)
            
            with col_text:
                st.markdown(f"**Prompt:** {item['prompt_text']}")

    st.write("")
    if st.button("Import to Automation", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        pure_texts = [item["prompt_text"] for item in st.session_state.text_solutions]
        st.session_state.global_queue.extend(pure_texts)
        st.switch_page("pages/03_Automation.py")
