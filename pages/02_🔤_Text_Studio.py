import streamlit as st
import random
# 引入核心组件
from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

# ==========================================
# 1. 页面配置与样式
# ==========================================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

st.title("🔤 Text Studio")
st.caption("Auto-Scan & Blind Box Mode (自动扫描图库 + 随机盲盒)")

# ==========================================
# 🔥 新增：平台适配指南 (用户教育)
# ==========================================
with st.expander("📖 必读：如何让 AI 完美复刻图片风格？(平台差异说明)", expanded=False):
    st.markdown("""
    **不同的 AI 对“图片链接”的读取能力不同，请根据你的目标平台操作：**
    
    🟢 **Midjourney (推荐)**
    * **原生支持**：脚本生成的 Prompt 包含了图片直链 (URL)。
    * **操作**：直接粘贴脚本运行即可，MJ 会自动抓取链接作为垫图 (Image Prompt)。
    
    🟡 **ChatGPT / Claude / Gemini**
    * **无法直接读链**：它们通常无法仅通过 URL 读取图片风格。
    * **正确姿势 (Context Injection)**：
        1.  **手动上传**：在运行脚本前，先**手动把你的母本图发给 AI**。
        2.  **建立语境**：告诉它 *"记住这张图的风格"*。
        3.  **运行脚本**：此时再粘贴脚本，AI 就会调用刚才的记忆来生成。
    """)

# ==========================================
# 2. 数据准备 (智能扫描)
# ==========================================
db = st.session_state.get("db_all", {})

# A. 语种
lang_keys = [k for k in db.keys() if k.startswith("Text_")]
if not lang_keys: 
    lang_keys = ["Text_English (Demo)"]

# B. 图库 (自动扫描 GitHub)
with st.spinner("正在同步 GitHub 图库资源..."):
    ref_map = fetch_image_refs_auto()

if not ref_map:
    ref_map = {"(空) 请先上传图片到 images 文件夹": ""}

# C. 字体
font_list = db.get("Font_Style", [])
if not font_list:
    font_list = ["Gothic", "Liquid", "Chrome", "Typewriter"]

# ==========================================
# 3. 控制台 (UI)
# ==========================================
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("1. 选择语种 (Language)", lang_keys)

with c2:
    # 盲盒与预览逻辑
    ref_options = ["🎲 随机抽取 (Random Blind Box)"] + list(ref_map.keys())
    selected_ref = st.selectbox("2. 选择母本 (Reference)", ref_options)
    
    # 预览区域
    if "随机" in selected_ref:
        st.info("✨ 盲盒模式：每组方案将自动匹配不同的风格图")
    else:
        url = ref_map.get(selected_ref, "")
        if url:
            st.image(url, width=150, caption="已锁定风格母本")
        else:
            st.warning("无法加载图片预览")

with c3:
    selected_font = st.selectbox("3. 字体风格 (Font)", ["Random"] + font_list)

# ==========================================
# 4. 生成与执行
# ==========================================
st.divider()
col_input, col_btn = st.columns([3, 1])

with col_input:
    manual_word = st.text_input("手动输入单词 (Manual Input)", placeholder="留空则自动从词库抽取...")

with col_btn:
    qty = st.number_input("数量 (Batch Size)", 1, 10, 4)
    st.write("")
    run_btn = st.button("🚀 立即组装 (Generate)", type="primary", use_container_width=True)

# ==========================================
# 5. 核心逻辑
# ==========================================
if run_btn:
    results = []
    # 准备词池
    words_pool = db.get(target_lang, [])
    if not words_pool and "Demo" in target_lang:
        words_pool = ["LOVE", "HOPE", "FATE"]

    for i in range(qty):
        # 1. 词
        word = manual_word if manual_word else (random.choice(words_pool) if words_pool else "LOVE")
        
        # 2. 图 (盲盒 vs 锁定)
        if "随机" in selected_ref and ref_map:
            # 真正的随机：每次循环都重新抽
            img_url = random.choice(list(ref_map.values()))
        else:
            img_url = ref_map.get(selected_ref, "")
            
        # 3. 字体
        font = selected_font if selected_font != "Random" else random.choice(font_list)
        
        # 4. 组装 Prompt (MJ 格式优化)
        # 格式：[图片URL] [描述] --iw 2
        prompt = f"{img_url} Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast --iw 2"
        
        results.append(f"**方案{i+1}：** {prompt}")

    # 存入 Session 并刷新
    st.session_state.final_solutions = results
    st.rerun()

# ==========================================
# 6. 结果展示
# ==========================================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.success(f"已生成 {len(st.session_state.final_solutions)} 组方案")
    
    for res in st.session_state.final_solutions:
        st.info(res)
        
    if st.button("📦 前往自动化中心投递", use_container_width=True):
        st.switch_page("pages/03_🚀_Automation.py")
