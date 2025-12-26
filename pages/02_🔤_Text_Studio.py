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

with st.spinner("Syncing Gallery..."):
    ref_map = fetch_image_refs_auto()

if not ref_map:
    ref_map = {"(Empty) Please upload to gallery": ""}

font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# ===========================
# 3. 界面交互
# ===========================
st.title("Text Studio")
st.caption("Reference Driven + Blind Box Mode")

with st.expander("📖 Guide: How to use with MJ/ChatGPT"):
    st.markdown("""
    * **Midjourney**: Simply run. MJ reads the image URL directly.
    * **ChatGPT**: Manually upload a reference image first to establish context.
    """)

c1, c2, c3 = st.columns(3)
with c1:
    target_lang = st.selectbox("1. Language", available_langs)
with c2:
    ref_options = ["🎲 Blind Box (Random)"] + list(ref_map.keys())
    selected_ref = st.selectbox("2. Reference Style", ref_options)
    if "Blind Box" not in selected_ref:
        url = ref_map.get(selected_ref)
        if url: st.image(url, width=150)
    else:
        st.info("✨ Auto-match distinct styles")
with c3:
    selected_font = st.selectbox("3. Font Style", ["Random"] + font_list)

# ===========================
# 4. 生成逻辑
# ===========================
st.divider()
col_in, col_btn = st.columns([3, 1])
with col_in:
    manual_word = st.text_input("Manual Input", placeholder="Leave empty for auto-draw...")
with col_btn:
    qty = st.number_input("Batch Size", 1, 10, 4)
    st.write("")
    if st.button("Generate", type="primary", use_container_width=True):
        
        results = []
        words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

        for i in range(qty):
            word = manual_word if manual_word else random.choice(words_pool)
            
            if "Blind Box" in selected_ref and ref_map:
                img_url = random.choice(list(ref_map.values()))
            else:
                img_url = ref_map.get(selected_ref, "")
            
            font = selected_font if selected_font != "Random" else random.choice(font_list)
            
            # 组装
            prompt = f"{img_url} Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
            results.append(f"**Option {i+1}:** {prompt}")

        st.session_state.text_solutions = results # 改名：text专用
        st.rerun()

# ===========================
# 5. 结果展示与叠加发送
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.success(f"Generated {len(st.session_state.text_solutions)} options")
    
    # 统一视觉风格：使用深色容器
    for res in st.session_state.text_solutions:
        with st.container(border=True):
            st.markdown(res)
        
    if st.button("Add to Automation Queue (叠加发送)", type="primary", use_container_width=True):
        # 🟢 核心修改：叠加逻辑 🟢
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
            
        st.session_state.global_queue.extend(st.session_state.text_solutions)
        
        st.toast(f"已添加 {len(st.session_state.text_solutions)} 个文本方案到队列！")
        time.sleep(0.5)
        st.switch_page("pages/03_🚀_Automation.py")
