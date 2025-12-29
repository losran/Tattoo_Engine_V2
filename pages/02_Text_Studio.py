import streamlit as st
import sys
import os
import random
import time

# ===========================
# 0. 路径修复
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

# ===========================
# 1. 初始化与样式增强
# ===========================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

# --- CSS 魔法：让选中的图片有视觉反馈 ---
st.markdown("""
<style>
    /* 隐藏部分不需要的 Label 空间 */
    div[data-testid="stCheckbox"] label { min-height: 0px; }
    
    /* 选中的图片容器样式微调 (Streamlit 限制，只能做辅助提示) */
    .selected-img {
        border: 3px solid #00ff00;
        border-radius: 8px;
        opacity: 1.0;
    }
    .unselected-img {
        opacity: 0.7;
        filter: grayscale(30%);
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 2. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
available_langs = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

# ===========================
# 3. 顶部：上传与直接预览
# ===========================
st.markdown("## Text Studio")

# 布局：左边上传，右边显示刚上传的图
col_up, col_prev = st.columns([1, 1])

with col_up:
    st.subheader("1. Import Reference")
    # 直接展示上传控件，去掉折叠框
    uploaded_file = st.file_uploader("Upload Image to Warehouse", type=['jpg', 'png', 'jpeg', 'webp'])
    
    if uploaded_file is not None:
        save_dir = "images"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        file_path = os.path.join(save_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Saved: {uploaded_file.name}")
        # 强制刷新以更新画廊
        time.sleep(0.5)
        st.rerun()

with col_prev:
    if uploaded_file:
        st.subheader("Preview")
        st.image(uploaded_file, width=200, caption="Newly Added")
    else:
        # 占位符，保持布局不塌陷
        st.write("") 

st.divider()

# ===========================
# 4. 核心交互：沉浸式画廊
# ===========================
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
image_files = [v for v in raw_map.values() if v]

c_gal_title, c_gal_ctrl = st.columns([2, 1])
with c_gal_title:
    st.subheader("2. Select Visual Style")
with c_gal_ctrl:
    use_global_blind = st.toggle("🎲 Global Blind Box (Random All)", value=False)

selected_images = []

if not use_global_blind:
    if not image_files:
        st.info("No images in warehouse. Upload one above.")
    else:
        # 网格布局
        cols = st.columns(5)
        for idx, file_name in enumerate(image_files):
            file_path = os.path.join("images", file_name)
            
            if os.path.exists(file_path):
                with cols[idx % 5]:
                    # 状态管理：检查当前是否被选中
                    is_checked = st.checkbox(f"{file_name}", key=f"chk_{file_name}", label_visibility="collapsed")
                    
                    # 视觉反馈逻辑
                    if is_checked:
                        st.markdown("✅ **ACTIVE**") # 选中标记
                        st.image(file_path, use_container_width=True) # 原图
                        selected_images.append(file_name)
                    else:
                        st.image(file_path, use_container_width=True) # 普通图
                        # 这是一个极小的“Select”文字，辅助点击
                        st.caption("Select")

        if selected_images:
            st.success(f"Selected {len(selected_images)} references.")

st.divider()

# ===========================
# 5. 底部操作区
# ===========================
st.subheader("3. Configuration")

c_lang, c_font, c_qty = st.columns([1, 1, 1])
with c_lang:
    target_lang = st.selectbox("Language Source", available_langs)
with c_font:
    selected_font = st.selectbox("Font Style", ["Random"] + font_list)
with c_qty:
    qty = st.number_input("Batch Qty", 1, 10, 4)

manual_word = st.text_input("Custom Text (Optional)", placeholder="Leave empty for random words...")

if st.button("🚀 Generate Designs", type="primary", use_container_width=True):
    try:
        with st.spinner("Designing..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                # 图片逻辑
                img_val = ""
                if use_global_blind:
                    if image_files: img_val = random.choice(image_files)
                elif selected_images:
                    img_val = random.choice(selected_images)
                
                font = selected_font if selected_font != "Random" else random.choice(font_list)
                
                url_part = f"{img_val} " if img_val else ""
                prompt_text = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
                
                results.append({
                    "image_file": img_val,
                    "prompt_text": prompt_text
                })
            
            st.session_state.text_solutions = results
            time.sleep(0.5)
            st.rerun()
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ===========================
# 6. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("📦 Result Gallery")
    
    for item in st.session_state.text_solutions:
        with st.container(border=True):
            col_img, col_text = st.columns([1, 4])
            
            with col_img:
                if item["image_file"]:
                    full_path = os.path.abspath(os.path.join("images", item["image_file"]))
                    if os.path.exists(full_path):
                        st.image(full_path, use_container_width=True)
                    else:
                        st.caption("Img Missing")
                else:
                    st.caption("No Ref")
            
            with col_text:
                st.markdown("**Prompt:**")
                st.markdown(f"{item['prompt_text']}")

    st.write("")
    if st.button("Import All to Automation Queue", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        pure_texts = [item["prompt_text"] for item in st.session_state.text_solutions]
        st.session_state.global_queue.extend(pure_texts)
        st.switch_page("pages/03_Automation.py")
