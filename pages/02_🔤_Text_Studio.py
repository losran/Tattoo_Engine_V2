import streamlit as st
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

# A. 语种 (从仓库读取)
lang_keys = ["Text_English", "Text_Spanish"] # 这里可以写死常用，或者动态读 keys
available_langs = [k for k in lang_keys if k in db]
if not available_langs: available_langs = ["Text_English"]

# B. 图库 (只读 gallery)
with st.spinner("正在同步图库资源..."):
    ref_map = fetch_image_refs_auto() # 调用 engine_manager 的新函数

if not ref_map:
    ref_map = {"(空) 请向 gallery 文件夹上传图片": ""}

# C. 字体 (从仓库读取)
font_list = db.get("Font_Style", [])
if not font_list: font_list = ["Gothic", "Liquid", "Chrome"]

# ===========================
# 3. 界面交互
# ===========================
st.title("🔤 Text Studio")
st.caption("Reference Driven (母本驱动) + Blind Box (盲盒模式)")


st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("1. 语种 (Language)", available_langs)

with c2:
    # 盲盒逻辑
    ref_options = ["🎲 随机抽取 (Blind Box)"] + list(ref_map.keys())
    selected_ref = st.selectbox("2. 母本风格 (Reference)", ref_options)
    
    # 预览
    if "随机" not in selected_ref:
        url = ref_map.get(selected_ref)
        if url: st.image(url, width=150)
    else:
        st.info("✨ 将为每个单词匹配不同的风格图")

with c3:
    selected_font = st.selectbox("3. 字体流派 (Font)", ["Random"] + font_list)

# ===========================
# 4. 生成逻辑
# ===========================
st.divider()
col_in, col_btn = st.columns([3, 1])

with col_in:
    manual_word = st.text_input("手动输入单词", placeholder="留空则从词库自动抽取...")

with col_btn:
    qty = st.number_input("数量", 1, 10, 4)
    st.write("")
    if st.button("🚀 立即组装", type="primary", use_container_width=True):
        
        results = []
        words_pool = db.get(target_lang, [])
        if not words_pool: words_pool = ["LOVE", "HOPE", "FAITH"]

        for i in range(qty):
            # 1. 词
            word = manual_word if manual_word else random.choice(words_pool)
            
            # 2. 图 (盲盒 vs 锁定)
            if "随机" in selected_ref and ref_map:
                img_url = random.choice(list(ref_map.values()))
            else:
                img_url = ref_map.get(selected_ref, "")
            
            # 3. 字体
            font = selected_font if selected_font != "Random" else random.choice(font_list)
            
            # 4. 组装 Prompt
            # 格式：[图片链接] Tattoo design of '[单词]', [字体] style... --iw 2
            prompt = f"{img_url} Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
            
            results.append(f"**方案{i+1}：** {prompt}")

        st.session_state.final_solutions = results
        st.rerun()

# ===========================
# 5. 结果投递
# ===========================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.success(f"已生成 {len(st.session_state.final_solutions)} 组方案")
    for res in st.session_state.final_solutions:
        st.info(res)
        
    if st.button("📦 前往自动化中心", use_container_width=True):
        st.switch_page("pages/03_🚀_Automation.py")
