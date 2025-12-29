import streamlit as st
import sys
import os
import random
import time
from PIL import Image

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
# 1. 初始化
# ===========================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# 2. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
# 字体库
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
# 语言库
available_langs = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

# ===========================
# 3. 顶部：上传与管理
# ===========================
st.markdown("## Text Studio")

# --- 上传功能 ---
with st.expander("📤 Upload New Reference Image (Save to Local)", expanded=False):
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg', 'webp'])
    if uploaded_file is not None:
        # 保存逻辑
        save_dir = "images"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        file_path = os.path.join(save_dir, uploaded_file.name)
        
        # 写入文件
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.toast(f"✅ Image saved: {uploaded_file.name}")
        time.sleep(1)
        st.rerun() # 刷新页面以显示新图

st.divider()

# ===========================
# 4. 核心交互：可视化画廊
# ===========================
# 获取最新图片列表
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
# 过滤掉无效项
image_files = [v for v in raw_map.values() if v]

st.subheader("1. Select Visual Reference")

# 控制选项
c_ctrl_1, c_ctrl_2 = st.columns([1, 4])
with c_ctrl_1:
    # 全局盲盒开关
    use_global_blind = st.toggle("🎲 Global Blind Box", value=False, help="Ignore selection below, pick random from ALL images.")

selected_images = []

# 如果没开全局盲盒，显示画廊供选择
if not use_global_blind:
    if not image_files:
        st.info("No images found in 'images/' folder. Please upload one above.")
    else:
        # 画廊网格布局 (5列)
        cols = st.columns(5)
        for idx, file_name in enumerate(image_files):
            file_path = os.path.join("images", file_name)
            if os.path.exists(file_path):
                with cols[idx % 5]:
                    # 显示图片
                    st.image(file_path, use_container_width=True)
                    # 复选框 (Key必须唯一)
                    if st.checkbox(f"Select", key=f"chk_{file_name}"):
                        selected_images.append(file_name)
        
        # 状态提示
        if selected_images:
            st.caption(f"✅ Selected {len(selected_images)} images (Randomly picked for each prompt).")
        else:
            st.caption("⚠️ No image selected. (Will generate text only)")

st.divider()

# ===========================
# 5. 底部操作区
# ===========================
st.subheader("2. Configure & Generate")

c_lang, c_font, c_qty = st.columns([1, 1, 1])
with c_lang:
    target_lang = st.selectbox("Language Source", available_langs)
with c_font:
    selected_font = st.selectbox("Font Style", ["Random"] + font_list)
with c_qty:
    qty = st.number_input("Batch Qty", 1, 10, 4)

manual_word = st.text_input("Custom Text (Optional)", placeholder="Leave empty to use random words from Language Source...")

if st.button("🚀 Generate Designs", type="primary", use_container_width=True):
    try:
        with st.spinner("Designing..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

            for i in range(qty):
                # 1. 词汇逻辑
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                # 2. 图片逻辑 (核心修改)
                img_val = ""
                if use_global_blind:
                    # 全局盲盒：从所有图片里抽
                    if image_files: img_val = random.choice(image_files)
                elif selected_images:
                    # 自定义选择：从勾选的图片里抽 (实现"勾选多个=自定义盲盒")
                    img_val = random.choice(selected_images)
                
                # 3. 字体逻辑
                font = selected_font if selected_font != "Random" else random.choice(font_list)
                
                # 4. 组装
                url_part = f"{img_val} " if img_val else ""
                prompt_text = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
                
                results.append({
                    "image_file": img_val,
                    "prompt_text": prompt_text
                })
            
            st.session_state.text_solutions = results
            time.sleep(0.5) # 视觉反馈
            st.rerun()
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ===========================
# 6. 结果展示 (图文并茂)
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
                    st.caption("No Image Ref")
            
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
