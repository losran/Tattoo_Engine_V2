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
# 1. 仅保留极简的辅助 CSS
# ===========================
# 这里的 CSS 仅仅是为了让输入框居中和删除按钮变红，
# 绝不触碰 Checkbox 的核心渲染逻辑，确保稳健。
st.markdown("""
<style>
    /* 让文件名输入框文字居中，看起来像标题 */
    div[data-testid="stTextInput"] input {
        text-align: center;
        font-size: 12px;
        color: #888;
    }
    div[data-testid="stTextInput"] input:focus {
        color: #fff;
    }
    
    /* 简单的红色文字修饰删除按钮 (不破坏结构) */
    button[kind="secondary"] p {
        color: #ff4444;
    }
    button[kind="secondary"] {
        border-color: #331111;
    }
    button[kind="secondary"]:hover {
        border-color: #ff0000;
        background-color: #220000;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 2. 上传区
# ===========================
st.markdown("## Text Studio")

uploaded_file = st.file_uploader(
    "📤 Upload Asset", 
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
    st.toast(f"✅ Saved: {uploaded_file.name}")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 3. 核心：原生卡片画廊
# ===========================
c_head, c_info = st.columns([3, 1])
with c_head:
    st.subheader("Visual Warehouse")

# 获取图片并排序
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
all_files = [v for v in raw_map.values() if v]
full_paths = [(f, os.path.join("images", f)) for f in all_files]
valid_files = [x for x in full_paths if os.path.exists(x[1])]
valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
sorted_image_files = [x[0] for x in valid_files]

selected_images = []

if not sorted_image_files:
    st.info("Warehouse is empty.")
else:
    # 使用 5 列布局，gap="medium" 拉开间距
    cols = st.columns(5, gap="medium")
    
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 🔥 核心：原生 Container 卡片 🔥
            with st.container(border=True):
                
                # --- A. 顶部选择栏 (Columns 布局) ---
                # 左边放勾选框，右边放状态文字
                c_check, c_state = st.columns([1, 3])
                
                with c_check:
                    # 原生 Checkbox，不加 label 避免冗余
                    is_checked = st.checkbox("sel", key=f"chk_{file_name}", label_visibility="collapsed")
                
                with c_state:
                    if is_checked:
                        # 选中时显示绿色文字
                        st.markdown(":white_check_mark: **Active**")
                    else:
                        # 未选中显示灰色
                        st.caption("Select")

                if is_checked:
                    selected_images.append(file_name)

                # --- B. 图片展示 ---
                st.image(file_path, use_container_width=True)

                # --- C. 文件名编辑 ---
                name_body, ext = os.path.splitext(file_name)
                new_name_body = st.text_input(
                    "rename",
                    value=name_body,
                    key=f"name_{file_name}",
                    label_visibility="collapsed",
                    help="Edit and press Enter to rename"
                )
                
                # 重命名逻辑
                if new_name_body != name_body:
                    new_full_name = new_name_body + ext
                    new_full_path = os.path.join("images", new_full_name)
                    try:
                        os.rename(file_path, new_full_path)
                        st.toast(f"Renamed: {new_full_name}")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Error")

                # --- D. 删除按钮 ---
                # 使用 secondary 样式，配合上面的微量 CSS 变红
                if st.button("🗑️ Delete", key=f"del_{file_name}", type="secondary", use_container_width=True):
                    try:
                        os.remove(file_path)
                        st.rerun()
                    except:
                        pass

# 状态统计
with c_info:
    if selected_images:
        st.markdown(f"<div style='text-align:right; color:#4CAF50;'><b>{len(selected_images)}</b> Selected</div>", unsafe_allow_html=True)

st.divider()

# ===========================
# 4. 生成控制
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
# 5. 生成逻辑
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
# 6. 结果展示
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
