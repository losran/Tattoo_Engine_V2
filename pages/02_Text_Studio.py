import streamlit as st
import random
import time
from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style
from lang_manager import T, init_lang

# ===========================
# 1. 初始化
# ===========================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
init_lang()
render_sidebar()
init_data()

# ===========================
# 2. 数据准备 (修复版)
# ===========================
db = st.session_state.get("db_all", {})
lang_keys = ["Text_English", "Text_Spanish"]
available_langs = [k for k in lang_keys if k in db] or ["Text_English"]
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# 🔥 核心修复：更严谨的图片引用获取 🔥
raw_map = fetch_image_refs_auto()
# 1. 确保它是个字典
if not isinstance(raw_map, dict):
    raw_map = {}
# 2. 数据清洗：只保留 value (链接) 不为空的项
ref_map = {k: v for k, v in raw_map.items() if v and isinstance(v, str) and v.startswith("http")}

# 3. 定义盲盒选项的名称
BLIND_BOX_OPTION = "🎲 Blind Box (Random)"

# 4. 构建下拉菜单选项
if not ref_map:
    # 如果清洗后没数据了，就只显示一个占位符
    ref_options = ["(No Images Available)"]
else:
    # 如果有数据，加上盲盒选项和具体的风格选项
    ref_options = [BLIND_BOX_OPTION] + list(ref_map.keys())

# ===========================
# 3. 顶部控制台
# ===========================
st.markdown(f"## {T('sb_text')}")

c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("Language", available_langs)
with c2:
    selected_ref = st.selectbox("Reference", ref_options)
with c3:
    selected_font = st.selectbox("Font", ["Random"] + font_list)

st.divider()

# ===========================
# 4. 底部操作区
# ===========================
c_input, c_qty, c_btn = st.columns([3, 0.6, 0.6])

with c_input:
    manual_word = st.text_input("Input", placeholder="Input text...", label_visibility="collapsed")
with c_qty:
    qty = st.number_input("Qty", min_value=1, max_value=10, value=4, label_visibility="collapsed")
with c_btn:
    run_btn = st.button("Generate", type="primary", use_container_width=True)

# ===========================
# 5. 生成逻辑 (修复版)
# ===========================
if run_btn:
    results = []
    words_pool = db.get(target_lang, []) or ["LOVE", "HOPE", "CHAOS", "KARMA"]

    for i in range(qty):
        # A. 确定单词
        word = manual_word if manual_word else random.choice(words_pool)
        
        # B. 确定风格引用 URL (🔥 核心修复点 🔥)
        img_url = "" # 默认为空
        
        if selected_ref == BLIND_BOX_OPTION:
            # 盲盒模式：从清洗过的 ref_map 中提取所有有效的 URL
            valid_urls = list(ref_map.values())
            if valid_urls:
                # 只有当池子里有东西时，才进行抽取
                img_url = random.choice(valid_urls)
            else:
                # 如果池子是空的，img_url 保持为空，避免报错
                img_url = "" 
        elif selected_ref in ref_map:
            # 精确选择模式
            img_url = ref_map.get(selected_ref, "")
        
        # C. 确定字体
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        # D. 组装 Prompt (确保 img_url 前后有空格)
        url_part = f"{img_url} " if img_url else ""
        prompt = f"{url_part}Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
        results.append(prompt)

    st.session_state.text_solutions = results

# ===========================
# 6. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    
    # (可选) 调试模式：看看图库里到底有没有数据
    # st.caption(f"Debug: Loaded {len(ref_map)} valid image references.")

    for i, res in enumerate(st.session_state.text_solutions):
        with st.container(border=True):
            # 使用代码块展示，方便复制，也更清晰
            st.code(res, language="markdown")

    st.write("")
    if st.button(T("import_btn"), use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        st.session_state.global_queue.extend(st.session_state.text_solutions)
        st.switch_page("pages/03_🚀_Automation.py")
