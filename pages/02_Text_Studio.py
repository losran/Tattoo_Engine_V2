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
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
ref_map = {k: v for k, v in raw_map.items() if v}

BLIND_BOX_OPTION = "🎲 Blind Box (Random)"

if not ref_map:
    ref_options = ["(No Images Available)"]
else:
    ref_options = [BLIND_BOX_OPTION] + list(ref_map.keys())

# ===========================
# 3. 顶部选择区
# ===========================
st.markdown("## Text Studio")

c1, c2, c3 = st.columns(3)
with c1:
    target_lang = st.selectbox("Language Source", available_langs)
with c2:
    selected_ref_key = st.selectbox("Reference Style", ref_options)
with c3:
    selected_font = st.selectbox("Font Style", ["Random"] + font_list)

st.divider()

# ===========================
# 4. 图片预览区 (横线下方，输入框上方)
# ===========================
if selected_ref_key != BLIND_BOX_OPTION and selected_ref_key in ref_map:
    img_file = ref_map[selected_ref_key]
    img_abs_path = os.path.abspath(os.path.join("images", img_file))
    
    if os.path.exists(img_abs_path):
        st.markdown("**Style Preview:**")
        # 宽度设为 200px，既看得清又不占满屏幕
        st.image(img_abs_path, width=200)
        st.write("") 
    else:
        st.warning(f"Preview not found: {img_file}")

# ===========================
# 5. 底部操作区
# ===========================
c_input, c_qty, c_btn = st.columns([3, 0.6, 0.6])
with c_input:
    manual_word = st.text_input("Input Text", placeholder="Paste text here... (Leave empty for random words)", label_visibility="collapsed")
with c_qty:
    qty = st.number_input("Qty", min_value=1, max_value=10, value=4, label_visibility="collapsed")
with c_btn:
    run_btn = st.button("Generate", type="primary", use_container_width=True)

# ===========================
# 6. 生成逻辑
# ===========================
if run_btn:
    try:
        with st.spinner("Creating Designs..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

            for i in range(qty):
                word = manual_word if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                if selected_ref_key == BLIND_BOX_OPTION:
                    valid_vals = list(ref_map.values())
                    if valid_vals: img_val = random.choice(valid_vals)
                elif selected_ref_key in ref_map:
                    img_val = ref_map.get(selected_ref_key, "")
                
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
        st.error(f"Error: {str(e)}")

# ===========================
# 7. 结果展示 (自由排版版)
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("Generated Results")
    
    for item in st.session_state.text_solutions:
        with st.container(border=True):
            # 🔥 核心修改：列比例调整为 [1, 3]，给文字更多空间
            col_img, col_text = st.columns([1, 3])
            
            with col_img:
                if item["image_file"]:
                    full_path = os.path.abspath(os.path.join("images", item["image_file"]))
                    if os.path.exists(full_path):
                        st.image(full_path, use_container_width=True)
                    else:
                        st.caption("Img Missing")
                else:
                    st.caption("No Ref Image")
            
            with col_text:
                # 🔥 核心修改：使用 markdown 替代 code，实现自动换行，不再“委屈”
                st.markdown(f"**Prompt:**")
                st.markdown(f"{item['prompt_text']}")
                
                # 额外提供一个小小的复制块，以防需要
                with st.expander("Copy raw text", expanded=False):
                    st.code(item['prompt_text'], language=None)

    st.write("")
    
    if st.button("Import to Automation Queue (Text Only)", use_container_width=True, type="primary"):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
            
        pure_texts = [item["prompt_text"] for item in st.session_state.text_solutions]
        st.session_state.global_queue.extend(pure_texts)
        st.switch_page("pages/03_Automation.py")
