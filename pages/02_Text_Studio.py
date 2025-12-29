import streamlit as st
import sys
import os
import random
import time

# ===========================
# 0. 基础设置与防错
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
# 1. 极简主义 CSS (Invisible Design)
# ===========================
st.markdown("""
<style>
    /* 1. 卡片容器：降低存在感，深色背景 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #080808;
        border: 1px solid #1a1a1a;
        border-radius: 8px;
        padding: 0px !important;
        overflow: hidden; /* 图片圆角对其 */
    }
    
    /* 2. 图片：铺满，无缝 */
    div[data-testid="stImage"] {
        margin-bottom: -10px; /* 拉近与下方工具栏的距离 */
    }
    div[data-testid="stImage"] img {
        border-radius: 8px 8px 0 0; /* 上方圆角 */
        width: 100%;
        object-fit: cover;
    }

    /* 3. 文件名输入框：平时隐形，点击出现下划线 */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid transparent !important;
        color: #888 !important;
        font-size: 11px !important;
        padding: 0px !important;
        height: 24px !important;
        text-align: center; 
    }
    div[data-testid="stTextInput"] input:focus {
        border-bottom: 1px solid #444 !important;
        color: #fff !important;
    }

    /* 4. 删除按钮：变成一个小小的 "✕" 符号 */
    button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        color: #444 !important;
        padding: 0px !important;
        font-size: 14px !important;
        line-height: 1 !important;
        height: 24px !important;
        width: 24px !important;
    }
    button[kind="secondary"]:hover {
        color: #ff4444 !important;
        background: rgba(255, 0, 0, 0.1) !important;
        border-radius: 50%;
    }

    /* 5. 复选框：微调位置 */
    div[data-testid="stCheckbox"] {
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div[data-testid="stCheckbox"] label span { display: none; }
    
    /* 工具栏布局微调 */
    .toolbar-container {
        padding: 5px 8px;
        background-color: #0e0e0e;
        border-top: 1px solid #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 2. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
# 修复报错：确保 available_langs 一定有定义
available_langs = [k for k in db.keys() if k.startswith("Text_")] 
if not available_langs: 
    available_langs = ["Text_English"] # 兜底默认值

# ===========================
# 3. 顶部：隐形上传区
# ===========================
st.markdown("## Text Studio")

# 极简上传条
uploaded_file = st.file_uploader(
    "📤 Drop to Upload", 
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
# 4. 核心：精致版卡片画廊
# ===========================
c_head, c_info = st.columns([3, 1])
with c_head:
    st.subheader("Visual Library")

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
    st.info("Gallery is empty.")
else:
    # 5列布局，保持间距
    cols = st.columns(5, gap="medium")
    
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 🔥 极简卡片容器 🔥
            with st.container(border=True):
                # 1. 图片 (撑满顶部)
                st.image(file_path, use_container_width=True)
                
                # 2. 底部极简工具栏 (一行搞定所有)
                # 比例：[复选框] [文件名.........] [删除]
                c_tool_chk, c_tool_name, c_tool_del = st.columns([1, 4, 1])
                
                with c_tool_chk:
                    is_checked = st.checkbox("sel", key=f"chk_{file_name}", label_visibility="collapsed")
                    if is_checked:
                        selected_images.append(file_name)
                
                with c_tool_name:
                    # 文件名编辑：去掉了边框，看起来像 caption
                    name_body, ext = os.path.splitext(file_name)
                    new_name_body = st.text_input(
                        "name",
                        value=name_body,
                        key=f"n_{file_name}",
                        label_visibility="collapsed",
                        placeholder="name"
                    )
                    # 重命名逻辑
                    if new_name_body != name_body:
                        try:
                            os.rename(file_path, os.path.join("images", new_name_body + ext))
                            st.rerun()
                        except: pass

                with c_tool_del:
                    # 删除按钮：仅显示一个小 ✕
                    if st.button("✕", key=f"d_{file_name}", type="secondary", use_container_width=True):
                        try:
                            os.remove(file_path)
                            st.rerun()
                        except: pass

# 状态统计
with c_info:
    if selected_images:
        st.markdown(f"<div style='text-align:right; color:#4CAF50; font-size:14px;'>● {len(selected_images)} Selected</div>", unsafe_allow_html=True)

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
