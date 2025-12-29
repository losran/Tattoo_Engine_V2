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

# 获取图片数据
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
# 只要有值就保留 (本地图片文件名)
ref_map = {k: v for k, v in raw_map.items() if v}

BLIND_BOX_OPTION = "🎲 Blind Box (Random)"

if not ref_map:
    ref_options = ["(No Images Available)"]
else:
    ref_options = [BLIND_BOX_OPTION] + list(ref_map.keys())

# ===========================
# 3. 顶部控制台 (带略缩图预览)
# ===========================
st.markdown("## Text Studio")

# 使用 columns 来放置选择框和预览图
c1, c2_select, c2_preview, c3 = st.columns([3, 2, 1, 3])

with c1:
    target_lang = st.selectbox("Language Source", available_langs)

with c2_select:
    selected_ref_key = st.selectbox("Reference Style", ref_options)

# 🔥 新增：略缩图预览区域 🔥
with c2_preview:
    # 如果选中的不是盲盒，且在映射表中存在，就显示预览图
    if selected_ref_key != BLIND_BOX_OPTION and selected_ref_key in ref_map:
        img_filename = ref_map[selected_ref_key]
        # 拼接完整的本地路径
        img_path = os.path.join("images", img_filename)
        if os.path.exists(img_path):
            # 显示一个小略缩图 (width控制大小)
            st.image(img_path, width=80, caption="Preview")
    else:
        # 盲盒或无图时显示占位
        st.write("")

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
# 5. 生成逻辑 (数据结构升级)
# ===========================
if run_btn:
    # 🔥 重要修改：results 不再是纯字符串列表，而是字典列表，存储图片和咒语的对应关系
    results = []
    words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

    for i in range(qty):
        word = manual_word if manual_word else random.choice(words_pool)
        
        img_val = "" 
        
        # 确定使用的图片文件名
        if selected_ref_key == BLIND_BOX_OPTION:
            valid_vals = list(ref_map.values())
            if valid_vals: img_val = random.choice(valid_vals)
        elif selected_ref_key in ref_map:
            img_val = ref_map.get(selected_ref_key, "")
        
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        # 组装 Prompt
        url_part = f"{img_val} " if img_val else ""
        prompt_text = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
        
        # 🔥 将图片文件名和生成的文本一起存入结果中 🔥
        results.append({
            "image_file": img_val, # 用于在 Text Studio 展示
            "prompt_text": prompt_text # 用于发送给自动化
        })

    st.session_state.text_solutions = results

# ===========================
# 6. 结果展示 (图文并茂)
