import streamlit as st
import random
from engine_manager import init_data, render_sidebar
from style_manager import apply_pro_style

# ==========================================
# 1. 页面配置
# ==========================================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

st.title("🔤 Text Studio")
st.caption("Reference Driven Lettering Generator (母本驱动模式)")

# ==========================================
# 2. 数据准备 (含防崩溃兜底)
# ==========================================
db = st.session_state.get("db_all", {})

# A. 获取语种库
# 逻辑：自动扫描所有以 "Text_" 开头的分类
lang_keys = [k for k in db.keys() if k.startswith("Text_")]
if not lang_keys:
    # ⚠️ 兜底：如果仓库没数据，强行给一个选项，防止页面空白
    lang_keys = ["Text_English (Demo)", "Text_Spanish (Demo)"]
    demo_words = ["LOVE", "HOPE", "KARMA", "CHAOS"] # 假数据

# B. 获取母本图
# 逻辑：解析 "名称 | URL" 格式
ref_list = db.get("Ref_Images", [])
ref_map = {}

if ref_list:
    for item in ref_list:
        if "|" in item:
            name, url = item.split("|", 1)
            ref_map[name.strip()] = url.strip()
else:
    # ⚠️ 兜底：假母本
    ref_map = {
        "Liquid Chrome (Demo)": "https://s.mj.run/demo_liquid",
        "Gothic Black (Demo)": "https://s.mj.run/demo_gothic"
    }

# C. 获取字体风格
font_list = db.get("Font_Style", [])
if not font_list:
    font_list = ["Gothic", "Liquid", "Typewriter"]

# ==========================================
# 3. 控制台 (UI)
# ==========================================
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("1. 选择语种 (Language)", lang_keys)
    
with c2:
    selected_ref_name = st.selectbox("2. 选择母本风格 (Reference)", list(ref_map.keys()))
    # 预览图片 (如果有真实链接的话)
    ref_url = ref_map.get(selected_ref_name, "")
    if ref_url.startswith("http"):
        # 这里只是展示链接，为了不占版面就不渲染大图了，或者可以用 st.image 渲染
        st.caption(f"🔗 Reference Loaded: {selected_ref_name}")
    
with c3:
    selected_font = st.selectbox("3. 字体风格 (Font)", ["Random"] + font_list)

st.markdown("---")

# ==========================================
# 4. 输入与生成
# ==========================================
col_input, col_btn = st.columns([3, 1])

with col_input:
    manual_word = st.text_input("手动输入单词 (Manual Input)", placeholder="留空则从词库随机抽取...")

with col_btn:
    qty = st.number_input("数量", 1, 10, 4)
    st.write("") # 占位对齐
    run_btn = st.button("🚀 立即组装", type="primary", use_container_width=True)

# ==========================================
# 5. 核心逻辑 (图+词 组装)
# ==========================================
if run_btn:
    results = []
    
    for i in range(qty):
        # 1. 确定单词
        if manual_word:
            word = manual_word
        else:
            # 尝试从仓库取词
            if "Demo" in target_lang:
                word = random.choice(demo_words)
            else:
                real_words = db.get(target_lang, [])
                word = random.choice(real_words) if real_words else "EMPTY_REPO"
        
        # 2. 确定风格
        style = selected_font
        if style == "Random":
            style = random.choice(font_list)
            
        # 3. 组装 Prompt (Prompt Engineering)
        # 格式: [URL] [Subject] [Style] --iw 2
        
        prompt = f"{ref_url} Tattoo design of the word '{word}', {style} style typography, clean white background, high contrast, ink lines --iw 2"
        
        # 包装成自动化脚本能识别的格式
        results.append(f"**方案{i+1}：** {prompt}")

    # 存入 Session
    st.session_state.final_solutions = results
    st.rerun()

# ==========================================
# 6. 结果交付
# ==========================================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.success(f"已生成 {len(st.session_state.final_solutions)} 组方案")
    
    # 简单的卡片展示
    for res in st.session_state.final_solutions:
        st.info(res)
        
    # 跳转按钮
    if st.button("📦 前往自动化中心投递 (Go to Automation)", use_container_width=True):
        st.switch_page("pages/03_🚀_Automation.py")
