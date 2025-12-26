import streamlit as st
import random
import time
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
lang_keys = ["Text_English", "Text_Spanish"]
available_langs = [k for k in lang_keys if k in db] or ["Text_English"]
ref_map = fetch_image_refs_auto()
if not ref_map: ref_map = {"Default": ""}
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# ===========================
# 3. 顶部控制台
# ===========================
st.markdown("## Text Studio")

# 3列选择器，完美对齐
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("Language", available_langs)
with c2:
    ref_options = ["🎲 Blind Box"] + list(ref_map.keys())
    selected_ref = st.selectbox("Reference", ref_options)
with c3:
    selected_font = st.selectbox("Font", ["Random"] + font_list)

st.divider()

# ===========================
# 4. 底部操作区 (Input | Qty | Button)
# ===========================
# 调整比例，确保对齐感
c_input, c_qty, c_btn = st.columns([3, 0.6, 0.6])

with c_input:
    manual_word = st.text_input(
        "Input", 
        placeholder="Input text...", 
        label_visibility="collapsed"
    )

with c_qty:
    qty = st.number_input(
        "Qty", 
        min_value=1, max_value=10, value=4, 
        label_visibility="collapsed"
    )

with c_btn:
    # 这个按钮现在是纯黑色的 (见 style_manager)
    run_btn = st.button("Generate", type="primary", use_container_width=True)

# ===========================
# 5. 生成逻辑
# ===========================
if run_btn:
    results = []
    words_pool = db.get(target_lang, []) or ["LOVE", "HOPE", "CHAOS", "KARMA"]

    for i in range(qty):
        word = manual_word if manual_word else random.choice(words_pool)
        
        if "Blind Box" in selected_ref and ref_map:
            img_url = random.choice(list(ref_map.values()))
        else:
            img_url = ref_map.get(selected_ref, "")
        
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        prompt = f"{img_url} Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
        results.append(f"**Option {i+1}:** {prompt}")

    st.session_state.text_solutions = results

# ===========================
# 6. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    
    for res in st.session_state.text_solutions:
        with st.container(border=True):
            st.markdown(res)

    st.write("")
    if st.button("Add to Automation Queue", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        st.session_state.global_queue.extend(st.session_state.text_solutions)
        st.switch_page("pages/03_🚀_Automation.py")
