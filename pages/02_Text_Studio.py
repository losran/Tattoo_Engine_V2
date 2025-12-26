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
# 2. 数据准备 (后台逻辑)
# ===========================
db = st.session_state.get("db_all", {})
lang_keys = ["Text_English", "Text_Spanish"]
available_langs = [k for k in lang_keys if k in db] or ["Text_English"]

# 自动获取图库引用 (不显示在界面上，只在后台跑)
ref_map = fetch_image_refs_auto()
if not ref_map: ref_map = {"Default": ""}
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]

# ===========================
# 3. 顶部控制台 (3列对齐)
# ===========================
st.markdown("## Text Studio")

# 第一排：三个核心选择器 (Language | Reference | Font)
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("Language", available_langs)
with c2:
    # 选项处理
    ref_options = ["🎲 Blind Box"] + list(ref_map.keys())
    selected_ref = st.selectbox("Reference", ref_options)
with c3:
    selected_font = st.selectbox("Font", ["Random"] + font_list)

# 分割线 (现在与上下完美对齐)
st.divider()

# ===========================
# 4. 底部操作区 (输入 + 执行)
# ===========================
# 布局比例：输入框占大头(3)，数量(0.5)，按钮(0.5)
c_input, c_qty, c_btn = st.columns([3, 0.5, 0.5])

with c_input:
    manual_word = st.text_input(
        "Input", 
        placeholder="Type text or leave empty for auto...", 
        label_visibility="collapsed"
    )

with c_qty:
    qty = st.number_input(
        "Qty", 
        min_value=1, max_value=10, value=4, 
        label_visibility="collapsed"
    )

with c_btn:
    # 按钮高度自动填满
    run_btn = st.button("Generate", type="primary", use_container_width=True)

# ===========================
# 5. 生成逻辑与展示
# ===========================
if run_btn:
    results = []
    words_pool = db.get(target_lang, []) or ["LOVE", "HOPE", "CHAOS", "KARMA"]

    for i in range(qty):
        # 1. 确定单词
        word = manual_word if manual_word else random.choice(words_pool)
        
        # 2. 确定风格引用 (URL)
        if "Blind Box" in selected_ref and ref_map:
            # 盲盒模式：随机抽一张图作为参考
            img_url = random.choice(list(ref_map.values()))
        else:
            img_url = ref_map.get(selected_ref, "")
        
        # 3. 确定字体
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        # 4. 组装 Prompt
        # 格式：[图片URL] Tattoo design of 'WORD', [Font] style...
        prompt = f"{img_url} Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
        results.append(f"**Option {i+1}:** {prompt}")

    st.session_state.text_solutions = results

# ===========================
# 6. 结果展示 (深色卡片)
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") # 空一行
    
    # 遍历展示
    for res in st.session_state.text_solutions:
        # 使用原生容器，自带深色背景和边框
        with st.container(border=True):
            st.markdown(res)

    # 底部叠加发送按钮
    st.write("")
    if st.button("Add to Automation Queue", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
            
        st.session_state.global_queue.extend(st.session_state.text_solutions)
        
        st.toast(f"Added {len(st.session_state.text_solutions)} items to queue!")
        time.sleep(0.5)
        st.switch_page("pages/03_🚀_Automation.py")
