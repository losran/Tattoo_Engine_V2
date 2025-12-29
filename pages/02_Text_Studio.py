import streamlit as st
import sys
import os

# ===========================
# 0. 路径修复 (必须保留)
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import random
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

# 🔥 核心修复点：允许本地图片通过 🔥
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}

# ❌ 之前的错误：ref_map = {k: v for k, v in raw_map.items() if ... and v.startswith("http")}
# ✅ 现在的正确写法：只要有值(v)就可以，不需要必须是 http 开头
ref_map = {k: v for k, v in raw_map.items() if v}

BLIND_BOX_OPTION = "🎲 Blind Box (Random)"

if not ref_map:
    ref_options = ["(No Images Available)"]
else:
    # 将字典的 key (也就是带文件夹图标的名字) 转为列表
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
        
        img_val = "" # 这里存的是具体的文件名或URL
        
        # 逻辑：从 ref_map 中取值
        if selected_ref == BLIND_BOX_OPTION:
            # 盲盒：随机抽一个 value
            valid_vals = list(ref_map.values())
            if valid_vals: img_val = random.choice(valid_vals)
        elif selected_ref in ref_map:
            # 指定：直接取 value
            img_val = ref_map.get(selected_ref, "")
        
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        # 组装 Prompt
        # 如果 img_val 是本地文件名 (不含http)，我们只作为文本参考放进去，或者需要你手动上传
        # 这里直接拼接到 Prompt 前面
        url_part = f"{img_val} " if img_val else ""
        
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
        st.switch_page("pages/03_Automation.py")
