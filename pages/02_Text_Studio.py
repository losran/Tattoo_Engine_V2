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

# 🌟 核心：初始化选中集合 (Set) 来记录选中的文件名 🌟
if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = set()

# ===========================
# 1. 样式微调
# ===========================
st.markdown("""
<style>
    /* 1. 文件名输入框：极简风格 */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: 1px solid #222 !important;
        color: #888 !important;
        font-size: 11px !important;
        text-align: center;
        height: 28px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #555 !important;
        color: #fff !important;
        background-color: #111 !important;
    }

    /* 2. 按钮样式优化 */
    /* Primary 按钮 (选中态) -> 绿色 */
    button[kind="primary"] {
        background-color: #1a331a !important;
        border-color: #2e5c2e !important;
        color: #4CAF50 !important;
        font-weight: bold !important;
    }
    button[kind="primary"]:hover {
        background-color: #2e5c2e !important;
        color: #fff !important;
    }

    /* Secondary 按钮 (删除) -> 红色微光 */
    button[kind="secondary"] {
        border-color: #331111 !important;
        color: #552222 !important;
        font-size: 11px !important;
    }
    button[kind="secondary"]:hover {
        border-color: #ff4444 !important;
        color: #ff4444 !important;
        background-color: #220000 !important;
    }
    
    /* 3. 卡片容器 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #222;
        background-color: #080808;
    }
    
    /* 4. 图片贴合 */
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
raw_keys = list(db.keys())
available_langs = [k for k in raw_keys if k.startswith("Text_")]
if not available_langs: available_langs = ["Text_English"]

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
    # 新上传的图默认选中
    st.session_state.selected_assets.add(uploaded_file.name)
    st.toast(f"✅ Saved")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 4. 核心：全宽按钮交互画廊
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

# 清理：移除不存在于当前文件夹的选中项 (防止Bug)
st.session_state.selected_assets = {f for f in st.session_state.selected_assets if f in sorted_image_files}

if not sorted_image_files:
    st.info("Library is empty.")
else:
    cols = st.columns(5)
    
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            with st.container(border=True):
                # --- A. 图片展示 ---
                st.image(file_path, use_container_width=True)

                # --- B. 核心：全宽切换按钮 (替代复选框) ---
                is_selected = file_name in st.session_state.selected_assets
                
                if is_selected:
                    # 选中状态：绿色按钮，点击取消
                    if st.button("✅ SELECTED", key=f"btn_{file_name}", type="primary", use_container_width=True):
                        st.session_state.selected_assets.remove(file_name)
                        st.rerun()
                else:
                    # 未选状态：普通按钮，点击选中
                    if st.button("⚪ Select", key=f"btn_{file_name}", type="secondary", use_container_width=True):
                        st.session_state.selected_assets.add(file_name)
                        st.rerun()

                # --- C. 文件名编辑 ---
                name_body, ext = os.path.splitext(file_name)
                new_name_body = st.text_input(
                    "name",
                    value=name_body,
                    key=f"n_{file_name}",
                    label_visibility="collapsed"
                )
                
                if new_name_body != name_body:
                    try:
                        new_full_name = new_name_body + ext
                        os.rename(file_path, os.path.join("images", new_full_name))
                        # 重命名后更新选中状态里的名字，防止丢失选中
                        if file_name in st.session_state.selected_assets:
                            st.session_state.selected_assets.remove(file_name)
                            st.session_state.selected_assets.add(new_full_name)
                        st.rerun()
                    except: pass

                # --- D. 删除按钮 ---
                if st.button("🗑️ Delete", key=f"d_{file_name}", type="secondary", use_container_width=True):
                    try:
                        os.remove(file_path)
                        # 删除后从选中集合移除
                        if file_name in st.session_state.selected_assets:
                            st.session_state.selected_assets.remove(file_name)
                        st.rerun()
                    except: pass

# 状态统计
with c_stat:
    count = len(st.session_state.selected_assets)
    if count > 0:
        st.markdown(f"<div style='text-align:right; color:#4CAF50;'>✅ <b>{count}</b> Selected</div>", unsafe_allow_html=True)

st.divider()

# ===========================
# 5. 生成控制
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
            
            # 将选中集合转为列表供随机抽取
            active_pool = list(st.session_state.selected_assets)

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                # 只有当有选中的图时，才从中抽取
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
