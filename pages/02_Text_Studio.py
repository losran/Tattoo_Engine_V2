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

# ===========================
# 1. 纯装饰性 CSS (不影响点击)
# ===========================
st.markdown("""
<style>
    /* 1. 文件名输入框：去边框，扁平化，像文字一样 */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: 1px solid #222 !important;
        border-radius: 4px;
        color: #888 !important;
        font-size: 12px !important;
        padding: 4px 8px !important;
        height: 30px !important;
        text-align: center;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #555 !important;
        color: #fff !important;
        background-color: #111 !important;
    }

    /* 2. 删除按钮：红色边框，警示感 */
    button[kind="secondary"] {
        border: 1px solid #331111 !important;
        color: #662222 !important;
        background: transparent !important;
        font-size: 12px !important;
        height: 30px !important;
        margin-top: 5px !important;
    }
    button[kind="secondary"]:hover {
        border-color: #ff4444 !important;
        color: #ff4444 !important;
        background-color: #220505 !important;
    }
    
    /* 3. 复选框容器微调 */
    div[data-testid="stCheckbox"] {
        padding-top: 2px;
    }
    
    /* 4. 卡片容器边框微调 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #222;
        background-color: #050505;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 2. 数据准备 (修复 NameError)
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# 修复逻辑：先获取 keys，再做列表推导，最后兜底
raw_keys = list(db.keys())
available_langs = [k for k in raw_keys if k.startswith("Text_")]
if not available_langs:
    available_langs = ["Text_English"] # 绝对兜底

# ===========================
# 3. 顶部上传
# ===========================
st.markdown("## Text Studio")

uploaded_file = st.file_uploader(
    "📤 Upload Reference", 
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
    st.toast(f"✅ Saved")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 4. 核心：原生布局画廊
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

selected_images = []

if not sorted_image_files:
    st.info("Library is empty.")
else:
    # 5列布局
    cols = st.columns(5)
    
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 🔥 每一张图一个独立的卡片容器 🔥
            with st.container(border=True):
                
                # --- Layer 1: 选择区 (Row 1) ---
                # 使用 columns 将复选框和状态分开
                c_chk, c_lbl = st.columns([1, 2])
                with c_chk:
                    # 原生复选框，绝对能点
                    is_checked = st.checkbox("sel", key=f"chk_{file_name}", label_visibility="collapsed")
                with c_lbl:
                    if is_checked:
                        st.markdown(":white_check_mark: **Active**")
                    else:
                        st.caption("Select") # 占位，保持对齐
                
                if is_checked:
                    selected_images.append(file_name)

                # --- Layer 2: 图片 (Row 2) ---
                st.image(file_path, use_container_width=True)

                # --- Layer 3: 文件名 (Row 3) ---
                name_body, ext = os.path.splitext(file_name)
                new_name_body = st.text_input(
                    "name",
                    value=name_body,
                    key=f"n_{file_name}",
                    label_visibility="collapsed",
                    placeholder="filename"
                )
                
                if new_name_body != name_body:
                    try:
                        os.rename(file_path, os.path.join("images", new_name_body + ext))
                        st.rerun()
                    except: pass

                # --- Layer 4: 删除 (Row 4) ---
                if st.button("🗑️ Delete", key=f"d_{file_name}", type="secondary", use_container_width=True):
                    try:
                        os.remove(file_path)
                        st.rerun()
                    except: pass

# 状态统计
with c_stat:
    if selected_images:
        st.markdown(f"<div style='text-align:right; color:#4CAF50;'><b>{len(selected_images)}</b> Selected</div>", unsafe_allow_html=True)

st.divider()

# ===========================
# 5. 生成控制
# ===========================
c_lang, c_font, c_qty, c_go = st.columns([1, 1, 0.8, 1])
with c_lang:
    # 修复了 available_langs 可能为空导致的报错
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

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                if selected_images:
                    img_val = random.choice(selected_images)
                
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
