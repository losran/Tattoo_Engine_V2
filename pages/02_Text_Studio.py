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
# 1. 初始化
# ===========================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

# 上传控件 Key 初始化
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- CSS 优化：让选中状态更明显，同时保证勾选框可点 ---
st.markdown("""
<style>
    /* 1. 隐藏 checkbox 的 label 文字 */
    div[data-testid="stCheckbox"] label span { display: none; }
    
    /* 2. 勾选框样式微调 - 保证在图片上方可见 */
    div[data-testid="stCheckbox"] {
        margin-bottom: 2px; /* 稍微留点空隙 */
    }
    
    /* 3. 选中图片的容器样式 (配合下方的 HTML 注入) */
    .selected-card {
        border: 4px solid #00FF00;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* 4. 删除按钮样式 */
    button[kind="secondary"] {
        border-color: #ff4444 !important;
        color: #ff4444 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #330000 !important;
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
# 3. 顶部：上传区
# ===========================
st.markdown("## Text Studio")

# 上传控件
uploaded_file = st.file_uploader(
    "📤 Upload to Library (Newest appears first)", 
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
# 4. 核心交互：画廊与管理
# ===========================
# 获取图片并按时间倒序
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
all_files = [v for v in raw_map.values() if v]

full_paths = [(f, os.path.join("images", f)) for f in all_files]
valid_files = [x for x in full_paths if os.path.exists(x[1])]
valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
sorted_image_files = [x[0] for x in valid_files]

# --- 画廊控制条 ---
c_title, c_actions = st.columns([2, 2])
with c_title:
    st.subheader("Visual Library")
with c_actions:
    # 这里的占位符用于后面放置删除按钮
    delete_placeholder = st.empty()

# 收集选中的图片
selected_images = []

if not sorted_image_files:
    st.info("Gallery is empty.")
else:
    # 5列瀑布流
    cols = st.columns(5)
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 1. 勾选框 (放在图片正上方，保证100%可点击)
            # 使用 key 保持状态
            is_checked = st.checkbox("Select", key=f"chk_{file_name}")
            
            # 2. 图片展示
            if is_checked:
                selected_images.append(file_name)
                # 选中态：用 CSS border 框住
                st.markdown(
                    f'<div style="border: 4px solid #4CAF50; border-radius: 8px; overflow: hidden; box-shadow: 0 0 10px #4CAF50;">'
                    f'<img src="app/static/{file_name}" style="width:100%; display:block;">'
                    f'</div>', 
                    unsafe_allow_html=True
                )
                # 兼容性兜底：如果上面HTML图片没出来(路径问题)，显示原生图片
                # st.image(file_path, use_container_width=True) 
            else:
                # 未选中态：普通图片
                st.image(file_path, use_container_width=True)
            
            st.write("") # 间距

# --- 批量删除逻辑 ---
if selected_images:
    # 在右上角显示删除按钮
    with delete_placeholder:
        # 使用 cols 让按钮靠右对齐
        dc1, dc2 = st.columns([1, 1])
        with dc2:
            if st.button(f"🗑️ Delete ({len(selected_images)})", type="secondary", use_container_width=True):
                # 执行删除
                success_count = 0
                for img_name in selected_images:
                    full_p = os.path.join("images", img_name)
                    try:
                        if os.path.exists(full_p):
                            os.remove(full_p)
                            success_count += 1
