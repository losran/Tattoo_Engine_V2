import streamlit as st
import random
# ⚠️ 注意：这里必须引入 fetch_image_refs_auto
from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

st.title("🔤 Text Studio")
# 👇看这里，如果你的页面没显示这句话，说明代码没更新成功
st.caption("Auto-Scan & Blind Box Mode (自动扫描图库 + 随机盲盒)")

# --- 数据准备 ---
db = st.session_state.get("db_all", {})
lang_keys = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English (Demo)"]
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# --- 核心：自动获取 GitHub 图片 ---
with st.spinner("正在扫描 GitHub 图库..."):
    ref_map = fetch_image_refs_auto()

if not ref_map:
    ref_map = {"(空) 请检查 images 文件夹": ""}

# --- UI ---
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("1. 选择语种", lang_keys)

with c2:
    # ✨ 这里增加了随机选项
    ref_options = ["🎲 随机抽取 (Random Blind Box)"] + list(ref_map.keys())
    selected_ref = st.selectbox("2. 选择母本", ref_options)
    
    # 预览逻辑
    if "随机" not in selected_ref:
        url = ref_map.get(selected_ref)
        if url: st.image(url, width=150)
    else:
        st.info("✨ 将为每个方案随机匹配不同风格")

with c3:
    selected_font = st.selectbox("3. 字体风格", ["Random"] + font_list)

# --- 生成逻辑 ---
st.divider()
col_input, col_btn = st.columns([3, 1])
with col_input:
    manual_word = st.text_input("手动输入单词", placeholder="留空则自动抽取...")
with col_btn:
    qty = st.number_input("数量", 1, 10, 4)
    st.write("")
    if st.button("🚀 立即组装", type="primary", use_container_width=True):
        results = []
        words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]
        
        for i in range(qty):
            # 1. 词
            word = manual_word if manual_word else random.choice(words_pool)
            
            # 2. 图 (随机逻辑)
            if "随机" in selected_ref and ref_map:
                img_url = random.choice(list(ref_map.values()))
            else:
                img_url = ref_map.get(selected_ref, "")
                
            # 3. 字体
            font = random.choice(font_list) if selected_font == "Random" else selected_font
            
            # 4. Prompt
            prompt = f"{img_url} Tattoo design of '{word}', {font} style typography --iw 2"
            results.append(f"**方案{i+1}：** {prompt}")
            
        st.session_state.final_solutions = results
        st.rerun()

# --- 结果 ---
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.success("已生成方案")
    for res in st.session_state.final_solutions:
        st.info(res)
    if st.button("📦 前往自动化中心"):
        st.switch_page("pages/03_🚀_Automation.py")
