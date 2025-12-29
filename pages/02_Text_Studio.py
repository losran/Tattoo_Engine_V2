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

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ===========================
# 2. 页面专属 CSS (微调卡片样式)
# ===========================
st.markdown("""
<style>
    /* 1. 隐藏 Checkbox 的 Label，让布局更紧凑 */
    div[data-testid="stCheckbox"] label span { display: none; }
    
    /* 2. 调整输入框样式 (文件名编辑) */
    div[data-testid="stTextInput"] input {
        font-size: 12px;
        padding: 5px;
        height: 30px;
        text-align: center;
        background-color: transparent !important;
        border: 1px solid #333 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #666 !important;
        background-color: #111 !important;
    }

    /* 3. 红色删除小按钮 */
    button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        color: #666 !important;
        padding: 0px !important;
        font-size: 12px !important;
    }
    button[kind="secondary"]:hover {
        color: #ff4444 !important;
        background: transparent !important;
    }
    
    /* 4. 优化卡片内的图片显示 */
    div[data-testid="stImage"] img {
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 3. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
available_langs = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

# ===========================
# 4. 顶部：上传区
# ===========================
st.markdown("## Text Studio")

uploaded_file = st.file_uploader(
    "📤 Upload Reference Image", 
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
# 5. 核心交互：卡片式画廊
# ===========================
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
all_files = [v for v in raw_map.values() if v]

full_paths = [(f, os.path.join("images", f)) for f in all_files]
valid_files = [x for x in full_paths if os.path.exists(x[1])]
valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
sorted_image_files = [x[0] for x in valid_files]

c_head, c_info = st.columns([3, 1])
with c_head:
    st.subheader("Visual Library")

selected_images = []

if not sorted_image_files:
    st.info("Gallery is empty.")
else:
    # gap="medium" 增加图片之间的黑缝间距
    cols = st.columns(5, gap="medium")
    
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 🔥 核心修改：使用 Container 封装成卡片，自带边框 🔥
            with st.container(border=True):
                # 1. 顶部：勾选框
                # 使用 columns 让 checkbox 居中或靠左
                c_chk, c_spacer = st.columns([1, 4])
                with c_chk:
                    is_checked = st.checkbox("sel", key=f"chk_{file_name}", label_visibility="collapsed")
                
                if is_checked:
                    selected_images.append(file_name)
                
                # 2. 中间：图片
                st.image(file_path, use_container_width=True)
                
                # 3. 下方：文件名编辑 (回车重命名)
                # 去掉扩展名显示，看起来更干净，但重命名时要加回去
                name_body, ext = os.path.splitext(file_name)
                new_name_body = st.text_input(
                    "rename", 
                    value=name_body, 
                    key=f"name_{file_name}",
                    label_visibility="collapsed",
                    help="Press Enter to rename"
                )
                
                # 重命名逻辑
                if new_name_body != name_body:
                    new_full_name = new_name_body + ext
                    new_full_path = os.path.join("images", new_full_name)
                    try:
                        os.rename(file_path, new_full_path)
                        st.toast(f"Renamed to: {new_full_name}")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error("Rename failed")

                # 4. 底部：删除按钮
                if st.button("🗑️ Delete", key=f"del_{file_name}", type="secondary", use_container_width=True):
                    try:
                        os.remove(file_path)
                        st.rerun()
                    except:
                        pass

# 状态提示
if selected_images:
    st.info(f"✅ Selected **{len(selected_images)}** images for generation.")

st.divider()

# ===========================
# 6. 生成控制
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
# 7. 生成逻辑
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
# 8. 结果展示
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
