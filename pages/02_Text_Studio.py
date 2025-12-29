import streamlit as st
import sys
import os
import random
import time
import urllib.parse # 用于处理中文文件名的URL编码

# ===========================
# 0. 基础设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

# 尝试导入 fragment
try:
    from streamlit import fragment
except ImportError:
    try:
        from streamlit import experimental_fragment as fragment
    except ImportError:
        fragment = lambda x: x

st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
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

# ===========================
# 2. CSS 样式 (网格布局)
# ===========================
st.markdown("""
<style>
    /* 响应式核心 */
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

    /* 按钮颜色 */
    button[kind="primary"] { background-color: #1b3a1b !important; border: 1px solid #2e5c2e !important; color: #4CAF50 !important; font-weight: 600 !important; height: 36px !important; }
    button[kind="primary"]:hover { background-color: #2e6b2e !important; color: #fff !important; }
    button[kind="secondary"] { background-color: #161616 !important; color: #888 !important; height: 36px !important; border: 1px solid #222 !important; }
    button[kind="secondary"]:hover { background-color: #222 !important; color: #ccc !important; border-color: #444 !important; }
    div[data-testid="column"] button[help="Delete"]:hover { background-color: #330000 !important; color: #ff4444 !important; border-color: #ff4444 !important; }
    
    button[title="View fullscreen"] { display: none; }
    div[role="radiogroup"] { justify-content: flex-end; }
    
    /* 结果区文本框优化 */
    div[data-testid="stTextArea"] textarea {
        font-size: 12px !important;
        background-color: #111 !important;
        color: #aaa !important;
        border: 1px solid #333 !important;
        min-height: 80px !important;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 3. 顶部区域
# ===========================
st.markdown("## Text Studio")

c_up, c_view = st.columns([2, 1])
with c_up:
    uploaded_file = st.file_uploader(
        "Upload", 
        type=['jpg', 'png', 'jpeg', 'webp'],
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed"
    )

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
# 4. 局部刷新画廊
# ===========================
@fragment
def render_gallery_fragment(current_col_count):
    c_head, c_stat = st.columns([3, 1])
    with c_head:
        st.subheader("Visual Library")

    raw_map = fetch_image_refs_auto()
    if not isinstance(raw_map, dict): raw_map = {}
    all_files = [v for v in raw_map.values() if v]
    full_paths = [(f, os.path.join("images", f)) for f in all_files]
    valid_files = [x for x in full_paths if os.path.exists(x[1])]
    valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
    sorted_image_files = [x[0] for x in valid_files]

    st.session_state.selected_assets = {f for f in st.session_state.selected_assets if f in sorted_image_files}

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

    with c_stat:
        count = len(st.session_state.selected_assets)
        if count > 0:
            st.markdown(f"<div style='text-align:right; color:#4CAF50; padding-top:10px;'>✅ <b>{count}</b> Selected</div>", unsafe_allow_html=True)

render_gallery_fragment(col_count)

st.divider()

# ===========================
# 5. 生成控制区
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
available_langs = [k for k in list(db.keys()) if k.startswith("Text_")] or ["Text_English"]

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
# 6. 生成逻辑 (🔥 核心修复：GitHub Raw URL 直连 🔥)
# ===========================
if run_btn:
    try:
        with st.spinner("Processing..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]
            active_pool = list(st.session_state.selected_assets)

            # 🔥 定义 GitHub 仓库的 RAW 基础路径 (基于您提供的链接) 🔥
            # 这是 Midjourney 能直接读取的公网地址
            GITHUB_RAW_BASE = "https://raw.githubusercontent.com/losran/Tattoo_Engine_V2/main/images/"

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                full_img_url = ""
                
                if active_pool:
                    img_val = random.choice(active_pool)
                    # 🔥 处理文件名 (URL编码，防止中文/空格报错)
                    safe_filename = urllib.parse.quote(img_val)
                    # 🔥 拼接成完整的 GitHub Raw URL
                    full_img_url = f"{GITHUB_RAW_BASE}{safe_filename}"
                
                font = selected_font if selected_font != "Random" else random.choice(font_list)
                
                # 🔥 Prompt 拼接：使用公网 URL，Midjourney 此时可以读取了
                url_part = f"{full_img_url} " if full_img_url else ""
                prompt_text = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
                
                results.append({
                    "image_file": img_val,     # 用于本地预览
                    "image_url": full_img_url, # 用于 Prompt
                    "prompt_text": prompt_text # 最终指令
                })
            
            st.session_state.text_solutions = results
            time.sleep(0.3)
            st.rerun()
            
    except Exception as e:
        st.error(str(e))

# ===========================
# 7. 结果展示 (🔥 修复：网格卡片封装 🔥)
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("Results")
    
    # 🔥 使用网格布局 (复用 col_count) 🔥
    res_cols = st.columns(col_count) 
    
    for idx, item in enumerate(st.session_state.text_solutions):
        col = res_cols[idx % col_count]
        
        with col:
            # 方案封装：漂亮的卡片
            with st.container(border=True):
                # 1. 本地图片预览 (为了速度，预览还是读本地)
                if item["image_file"]:
                    full_path = os.path.abspath(os.path.join("images", item["image_file"]))
                    if os.path.exists(full_path):
                        st.image(full_path, use_container_width=True)
                
                # 2. Prompt 文本框 (封装在卡片内)
                st.text_area(
                    "Prompt",
                    value=item['prompt_text'],
                    height=100,
                    key=f"res_{idx}",
                    label_visibility="collapsed"
                )

    st.write("")
    
    # 底部导入按钮
    if st.button("Import to Automation Queue", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        
        # 🔥 确保是 List[String]，每条 Prompt 都是独立的
        pure_texts = [item["prompt_text"] for item in st.session_state.text_solutions]
        st.session_state.global_queue.extend(pure_texts)
        
        st.toast(f"✅ Imported {len(pure_texts)} tasks to Automation")
        time.sleep(1)
        st.switch_page("pages/03_Automation.py")
