import streamlit as st
import sys
import os

# ===========================
# 0. 路径修复 (必须保留，否则找不到 engine_manager)
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import random
# 导入核心模块 (无翻译模块)
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
available_langs = []
for k in db.keys():
    if k.startswith("Text_"):
        available_langs.append(k)
if not available_langs: available_langs = ["Text_English"]

font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# 🔥 核心功能修复：图片引用清洗 (确保Blind Box有效)
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
ref_map = {k: v for k, v in raw_map.items() if v and isinstance(v, str) and v.startswith("http")}
BLIND_BOX_OPTION = "🎲 Blind Box (Random)"

if not ref_map:
    ref_options = ["(No Images Available)"]
else:
    ref_options = [BLIND_BOX_OPTION] + list(ref_map.keys())

# ===========================
# 3. 顶部控制台
# ===========================
st.markdown("## Text Studio")

c1, c2, c3 = st.columns(3)
with c1:
    target_lang = st.selectbox("Language Source", available_langs)
with c2:
    selected_ref = st.selectbox("Reference Style", ref_options)
with c3:
    selected_font = st.selectbox("Font Style", ["Random"] + font_list)

st.divider()

# ===========================
# 4. 底部操作区
# ===========================
c_input, c_qty, c_btn = st.columns([3, 0.6, 0.6])
with c_input:
    manual_word = st.text_input("Input", placeholder="Paste text here...", label_visibility="collapsed")
with c_qty:
    qty = st.number_input("Qty", min_value=1, max_value=10, value=4, label_visibility="collapsed")
with c_btn:
    run_btn = st.button("Generate", type="primary", use_container_width=True)

# ===========================
# 5. 生成逻辑
# ===========================
if run_btn:
    results = []
    words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

    for i in range(qty):
        word = manual_word if manual_word else random.choice(words_pool)
        
        img_url = ""
        # 🔥 核心功能修复：Blind Box 逻辑
        if selected_ref == BLIND_BOX_OPTION:
            valid_urls = list(ref_map.values())
            if valid_urls: img_url = random.choice(valid_urls)
        elif selected_ref in ref_map:
            img_url = ref_map.get(selected_ref, "")
        
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        url_part = f"{img_url} " if img_url else ""
        prompt = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
        results.append(prompt)

    st.session_state.text_solutions = results

# ===========================
# 6. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    for res in st.session_state.text_solutions:
        with st.container(border=True):
            st.code(res, language="markdown")

    st.write("")
    if st.button("Import to Automation Queue", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        st.session_state.global_queue.extend(st.session_state.text_solutions)
        st.switch_page("pages/03_Automation.py") # 请确保你的文件名是 03_Automation.py 还是 03_🚀_Automation.py，这里写的是精简版
