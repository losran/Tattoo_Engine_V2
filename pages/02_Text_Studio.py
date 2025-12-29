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
# 1. CSS 强制响应式补丁
# ===========================
st.markdown("""
<style>
    /* --- 核心：强制列宽和换行 (解决手机端挤压问题) --- */
    
    /* 1. 找到所有列的父容器，强制允许换行 */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 12px !important; /* 列与列的间距 */
    }

    /* 2. 找到每一个单独的列，锁死最小宽度 */
    [data-testid="column"] {
        /* 关键：每个列至少要占 160px，否则就换行 */
        min-width: 160px !important;
        /* 让列自动填满剩余空间，但不小于 160px */
        flex: 1 1 160px !important; 
        /* 覆盖 Streamlit 默认的百分比宽度 */
        width: auto !important;
        max-width: 100% !important;
    }

    /* --- 卡片美化 --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 6px !important; /* 卡片内边距：让图片不贴边 */
        background-color: #0e0e0e;
        border: 1px solid #222;
        border-radius: 6px;
        margin-bottom: 8px; /* 卡片垂直间距 */
    }

    /* --- 图片 --- */
    div[data-testid="stImage"] {
        margin-bottom: 6px !important; /* 图片和下方元素的距离 */
    }
    div[data-testid="stImage"] img {
        border-radius: 4px !important;
        width: 100%;
        display: block;
    }

    /* --- 按钮组 (无缝拼接风格) --- */
    button {
        border: none !important;
        margin: 0px !important;
        width: 100%;
        white-space: nowrap !important;
    }
    
    /* 选中按钮 (左) */
    button[kind="primary"] {
        background-color: #1b3a1b !important;
        border: 1px solid #2e5c2e !important;
        color: #4CAF50 !important;
        font-weight: 700 !important;
        height: 34px !important;
        border-radius: 4px !important;
    }
    button[kind="primary"]:hover {
        background-color: #2e6b2e !important;
        color: #fff !important;
    }
    
    /* 未选/删除按钮 (灰) */
    button[kind="secondary"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
        color: #888 !important;
        height: 34px !important;
        border-radius: 4px !important;
    }
    button[kind="secondary"]:hover {
        border-color: #666 !important;
        color: #ccc !important;
    }

    /* 删除按钮特定样式 */
    div[data-testid="column"] button[help="Delete"]:hover {
        background-color: #330000 !important;
        color: #ff4444 !important;
        border-color: #ff4444 !important;
    }
    
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
# 4. 自动响应式画廊
# ===========================
c_head, c_stat = st.columns([3, 1])
with c_head:
    st.subheader("Visual Library")

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
    # 🔥 核心布局：依然使用 6 列 🔥
    # 但由于上面的 CSS 强制了 min-width: 160px，
    # 在手机上这 6 列会自动折叠成 3 行 (每行2列)，实现自动响应。
    NUM_COLS = 6
    cols = st.columns(NUM_COLS)
    
    for idx, file_name in enumerate(sorted_image_files):
        # 瀑布流逻辑：垂直分发
        col_index = idx % NUM_COLS
        file_path = os.path.join("images", file_name)
        
        with cols[col_index]:
            with st.container(border=True):
                # 1. 图片
                st.image(file_path, use_container_width=True)
                
                # 2. 按钮区 (Grid Layout)
                c_sel, c_del = st.columns([3, 1], gap="small")
                
                is_selected = file_name in st.session_state.selected_assets
                
                with c_sel:
                    if is_selected:
                        # 选中态：绿色 Active
                        if st.button("✅ Active", key=f"s_{file_name}", type="primary", use_container_width=True):
                            st.session_state.selected_assets.remove(file_name)
                            st.rerun()
                    else:
                        # 未选态：灰色 Select
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
