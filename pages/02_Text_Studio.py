import streamlit as st
import sys
import os
import random
import time

# ===========================
# 0. 路径修复与基础设置
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
# 1. 模块化 CSS (卡片式设计)
# ===========================
st.markdown("""
<style>
    /* --- 卡片容器样式微调 --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0e0e0e; /* 卡片背景微深 */
        border-color: #333;
    }

    /* --- 1. 顶部勾选框 --- */
    /* 隐藏 Label */
    div[data-testid="stCheckbox"] label span { display: none; }
    /* 让勾选框居中 */
    div[data-testid="stCheckbox"] {
        display: flex;
        justify-content: center;
        margin-bottom: 5px;
    }

    /* --- 2. 文件名输入框 (微型化) --- */
    div[data-testid="stTextInput"] input {
        font-size: 11px;
        text-align: center;
        height: 28px;
        min-height: 28px;
        background-color: #000 !important;
        border: 1px solid #222 !important;
        color: #888 !important;
        padding: 0px 5px;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #666 !important;
        color: #fff !important;
    }

    /* --- 3. 删除按钮 (全宽、红色警示) --- */
    button[kind="secondary"] {
        border: 1px dashed #331111 !important;
        background: transparent !important;
        color: #552222 !important;
        font-size: 10px !important;
        padding: 2px !important;
        height: auto !important;
        min-height: 0px !important;
        margin-top: 5px;
        width: 100%;
    }
    button[kind="secondary"]:hover {
        border-color: #ff4444 !important;
        color: #ff4444 !important;
        background-color: #220000 !important;
    }
    
    /* --- 图片圆角 --- */
    div[data-testid="stImage"] img {
        border-radius: 4px;
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
# 3. 顶部：资产入库 (Upload)
# ===========================
st.markdown("## Text Studio")

# 极简上传条
uploaded_file = st.file_uploader(
    "📤 Upload New Asset", 
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
    st.toast(f"✅ Asset Imported: {uploaded_file.name}")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 4. 核心：资产管理模块 (Image Management Module)
# ===========================
c_title, c_stat = st.columns([3, 1])
with c_title:
    st.subheader("Visual Warehouse")

# 获取并排序图片 (新图在前)
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
    # 5列布局，gap="medium" 保证卡片间距清晰
    cols = st.columns(5, gap="medium")
    
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 🔥 核心：卡片封装 🔥
            # border=True 会自动生成一个带灰色边框的盒子
            with st.container(border=True):
                
                # --- A. 顶部：选中状态 ---
                # 使用 key 绑定状态
                is_checked = st.checkbox("Select", key=f"chk_{file_name}", label_visibility="collapsed")
                if is_checked:
                    selected_images.append(file_name)
                    # 选中时给个绿色边框反馈 (CSS模拟)
                    st.markdown(
                        """<style>
                        div[data-testid="stVerticalBlockBorderWrapper"]:has(input:checked) {
                            border: 1px solid #00FF00 !important;
                            box-shadow: 0 0 5px rgba(0,255,0,0.2);
                        }
                        </style>""", 
                        unsafe_allow_html=True
                    )
                
                # --- B. 中间：图片展示 ---
                st.image(file_path, use_container_width=True)
                
                # --- C. 下方：文件名编辑 (回车重命名) ---
                name_body, ext = os.path.splitext(file_name)
                # 这个 text_input 用于显示和修改名字
                new_name_body = st.text_input(
                    "rename",
                    value=name_body,
                    key=f"rename_{file_name}",
                    label_visibility="collapsed",
                    placeholder="Rename..."
                )
                
                # 触发重命名逻辑
                if new_name_body != name_body:
                    new_full_name = new_name_body + ext
                    new_full_path = os.path.join("images", new_full_name)
                    try:
                        os.rename(file_path, new_full_path)
                        st.toast(f"♻️ Renamed to: {new_full_name}")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error("Error renaming")

                # --- D. 底部：删除按钮 ---
                if st.button("🗑 DELETE", key=f"del_{file_name}", type="secondary", use_container_width=True):
                    try:
                        os.remove(file_path)
                        st.toast("🗑 Asset Deleted")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        pass

# 选中状态统计
with c_stat:
    if selected_images:
        st.markdown(f"<div style='text-align:right; color:#00FF00; font-weight:bold;'>✅ {len(selected_images)} Active</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:right; color:#666;'>No selection</div>", unsafe_allow_html=True)

st.divider()

# ===========================
# 5. 生成控制台
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
# 6. 自动化生成逻辑
# ===========================
if run_btn:
    try:
        with st.spinner("Pipeline Running..."):
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
# 7. 结果交付区
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("Results Delivery")
    
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
