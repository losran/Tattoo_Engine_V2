import streamlit as st
import sys
import os
import random
import time
import urllib.parse # 用于URL编码

# ===========================
# 0. 基础设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

try:
    from streamlit import fragment
except ImportError:
    fragment = lambda x: x

st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()

# 🔥 核心修复：确保数据加载 🔥
# 如果还没加载过，或者用户点击了刷新，就重新加载
if "db_all" not in st.session_state:
    init_data()

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = set()

# ===========================
# 1. 核心回调 (Callbacks)
# ===========================
def toggle_selection(file_name):
    if file_name in st.session_state.selected_assets:
        st.session_state.selected_assets.remove(file_name)
    else:
        st.session_state.selected_assets.add(file_name)

def delete_asset(file_path, file_name):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        if file_name in st.session_state.selected_assets:
            st.session_state.selected_assets.remove(file_name)
    except Exception as e:
        print(f"Delete Error: {e}")

def toggle_all_selection(all_files_list):
    if len(st.session_state.selected_assets) == len(all_files_list) and len(all_files_list) > 0:
        st.session_state.selected_assets = set()
    else:
        st.session_state.selected_assets = set(all_files_list)

# ===========================
# 2. CSS 样式 (无框 + 蓝色链接)
# ===========================
st.markdown("""
<style>
    /* 上方画廊响应式核心 */
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 12px !important; }
    [data-testid="column"] { min-width: 160px !important; flex: 1 1 160px !important; width: auto !important; max-width: 100% !important; }

    /* 卡片容器 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 2px !important; 
        background-color: #0a0a0a;
        border: 1px solid #222;
        border-radius: 8px;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #555; }

    /* 图片 */
    div[data-testid="stImage"] { margin-bottom: 2px !important; }
    div[data-testid="stImage"] img { border-radius: 6px !important; width: 100%; display: block; }

    /* 按钮基础 */
    button { width: 100%; border-radius: 6px !important; border: none !important; white-space: nowrap !important; }
    button[kind="primary"] { background-color: #1b3a1b !important; border: 1px solid #2e5c2e !important; color: #4CAF50 !important; font-weight: 600 !important; height: 36px !important; }
    button[kind="primary"]:hover { background-color: #2e6b2e !important; color: #fff !important; }
    button[kind="secondary"] { background-color: #161616 !important; color: #888 !important; height: 36px !important; border: 1px solid #222 !important; }
    button[kind="secondary"]:hover { background-color: #222 !important; color: #ccc !important; border-color: #444 !important; }
    div[data-testid="column"] button[help="Delete"]:hover { background-color: #330000 !important; color: #ff4444 !important; border-color: #ff4444 !important; }
    
    button[title="View fullscreen"] { display: none; }
    div[role="radiogroup"] { justify-content: flex-end; }
    
    /* 链接样式优化 */
    .stMarkdown a {
        color: #4da6ff !important; /* 亮蓝色 */
        text-decoration: underline !important; /* 下划线 */
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 3. 顶部区域
# ===========================
st.markdown("## Text Studio")

c_up, c_view = st.columns([2, 1])
with c_up:
    uploaded_file = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg', 'webp'], key=f"uploader_{st.session_state.uploader_key}", label_visibility="collapsed")

with c_view:
    layout_mode = st.radio("Layout", ["PC", "Tablet", "Mobile"], horizontal=True, label_visibility="collapsed")
    col_map = {"PC": 5, "Tablet": 3, "Mobile": 2}
    col_count = col_map[layout_mode]

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
# 4. 局部刷新画廊 (Fragment)
# ===========================
@fragment
def render_gallery_fragment(current_col_count):
    c_head, c_ctrl = st.columns([3, 1])
    
    raw_map = fetch_image_refs_auto()
    if not isinstance(raw_map, dict): raw_map = {}
    all_files = [v for v in raw_map.values() if v]
    full_paths = [(f, os.path.join("images", f)) for f in all_files]
    valid_files = [x for x in full_paths if os.path.exists(x[1])]
    valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
    sorted_image_files = [x[0] for x in valid_files]

    st.session_state.selected_assets = {f for f in st.session_state.selected_assets if f in sorted_image_files}

    with c_head:
        st.subheader("Visual Library")
        
    with c_ctrl:
        if sorted_image_files:
            is_all_selected = (len(st.session_state.selected_assets) == len(sorted_image_files)) and (len(sorted_image_files) > 0)
            btn_label = "❌ Uncheck All" if is_all_selected else "✅ Select All"
            st.button(btn_label, key="btn_toggle_all", type="secondary", use_container_width=True, on_click=toggle_all_selection, args=(sorted_image_files,))

    if not sorted_image_files:
        st.info("Library is empty.")
    else:
        cols = st.columns(current_col_count)
        for idx, file_name in enumerate(sorted_image_files):
            file_path = os.path.join("images", file_name)
            col = cols[idx % current_col_count]
            
            with col:
                with st.container(border=True):
                    st.image(file_path, use_container_width=True)
                    c_sel, c_del = st.columns([3, 1], gap="small")
                    is_selected = file_name in st.session_state.selected_assets
                    
                    with c_sel:
                        if is_selected:
                            st.button("✅ Active", key=f"s_{file_name}", type="primary", use_container_width=True, on_click=toggle_selection, args=(file_name,))
                        else:
                            st.button("Select", key=f"s_{file_name}", type="secondary", use_container_width=True, on_click=toggle_selection, args=(file_name,))
                    with c_del:
                        st.button("🗑", key=f"d_{file_name}", type="secondary", use_container_width=True, help="Delete", on_click=delete_asset, args=(file_path, file_name))

    if st.session_state.selected_assets:
        st.markdown(f"<div style='text-align:right; color:#4CAF50; padding-top:10px;'>✅ <b>{len(st.session_state.selected_assets)}</b> Selected</div>", unsafe_allow_html=True)

render_gallery_fragment(col_count)

st.divider()

# ===========================
# 5. 生成控制区 (🔥 增加刷新按钮，解决新文件不识别问题 🔥)
# ===========================

# 布局：增加一个小的刷新按钮列
c_lang, c_refresh, c_word, c_qty, c_go = st.columns([1, 0.3, 1, 0.5, 0.8])

# 1. 刷新按钮逻辑 (Force Reload)
with c_refresh:
    # 垂直居中一点
    st.write("")
    st.write("") 
    if st.button("🔄", help="Refresh Library (Reload files from disk)"):
        # 强制清除缓存
        if "db_all" in st.session_state:
            del st.session_state["db_all"]
        # 重新加载
        init_data()
        st.toast("✅ Library Refreshed!")
        time.sleep(0.5)
        st.rerun()

# 获取最新数据
db = st.session_state.get("db_all", {})

# 2. 语种选择
with c_lang:
    # 只要文件名里有 "text_" 就算，不管后缀
    raw_keys = list(db.keys())
    available_langs = sorted([k for k in raw_keys if "text_" in k])
    if not available_langs: available_langs = ["text_en"]
    
    target_lang = st.selectbox("Language Bank", available_langs, label_visibility="collapsed")

# 3. 单词选择
with c_word:
    # 获取单词列表，如果文件是空的，就给个默认提示，不然下拉框会报错
    current_words_pool = db.get(target_lang, [])
    if not current_words_pool:
        current_words_pool = ["(Empty File)"]
        
    word_options = ["🎲 Random (随机词)"] + current_words_pool
    selected_word_opt = st.selectbox("Pick Word", word_options, label_visibility="collapsed")

# 4. 数量与生成
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
            active_pool = list(st.session_state.selected_assets)
            
            GITHUB_RAW_BASE = "https://raw.githubusercontent.com/losran/Tattoo_Engine_V2/main/images/"

            for i in range(qty):
                # 单词逻辑
                if manual_word.strip():
                    final_word = manual_word.strip()
                elif selected_word_opt == "🎲 Random (随机词)":
                    # 从当前池子里过滤掉 "(Empty File)" 这种占位符
                    valid_pool = [w for w in current_words_pool if w != "(Empty File)"]
                    if valid_pool:
                        final_word = random.choice(valid_pool)
                    else:
                        final_word = "LOVE" # 最后的兜底
                else:
                    final_word = selected_word_opt

                # 图片逻辑
                img_val = random.choice(active_pool) if active_pool else ""
                full_img_url = ""
                if img_val:
                    safe_filename = urllib.parse.quote(img_val)
                    full_img_url = f"{GITHUB_RAW_BASE}{safe_filename}"
                
                # Prompt 构造
                url_part = f"{full_img_url} " if full_img_url else ""
                prefix = f"**方案{i+1}：** "
                
                prompt_text = f"{prefix}{url_part}Tattoo design of the word '{final_word}', clean white background, high contrast --iw 2 **"
                
                results.append({"image_file": img_val, "prompt_text": prompt_text})
            
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
    
    for idx, item in enumerate(st.session_state.text_solutions):
        with st.container(border=True):
            col_img, col_text = st.columns([1, 4])
            
            with col_img:
                if item["image_file"]:
                    full_path = os.path.abspath(os.path.join("images", item["image_file"]))
                    if os.path.exists(full_path):
                        st.image(full_path, use_container_width=True)
            
            with col_text:
                st.markdown(item['prompt_text'])

    st.write("")
    if st.button("Import to Automation Queue", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        
        pure_texts = [item["prompt_text"] + "\n" for item in st.session_state.text_solutions]
        st.session_state.global_queue.extend(pure_texts)
        
        st.toast(f"✅ Imported {len(pure_texts)} tasks to Automation")
        time.sleep(1)
        st.switch_page("pages/03_Automation.py")
