import streamlit as st
import random
# 注意这里增加了 fetch_image_refs_auto 的引用
from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

# ==========================================
# 1. 页面配置与初始化
# ==========================================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

st.title("🔤 Text Studio")
st.caption("Auto-Scan & Blind Box Mode (自动扫描图库 + 随机盲盒)")

# ==========================================
# 2. 智能数据准备
# ==========================================
db = st.session_state.get("db_all", {})

# --- A. 准备语种 (Language) ---
lang_keys = [k for k in db.keys() if k.startswith("Text_")]
if not lang_keys: 
    # 如果没数据，给个演示选项
    lang_keys = ["Text_English (Demo)"]

# --- B. 准备图库 (Reference) [核心升级] ---
# 这里调用我们在 engine_manager 里新写的函数，自动去 images 文件夹抓图
with st.spinner("正在扫描 GitHub 图库..."):
    # 这一步会自动获取所有上传的图片链接
    ref_map = fetch_image_refs_auto()

# 如果一张图都没扫到，给个提示
if not ref_map:
    ref_map = {"(空) 请先上传图片到 images 文件夹": ""}
    # 也可以给个假图兜底
    # ref_map["Demo Image"] = "https://via.placeholder.com/150"

# --- C. 准备字体 (Fonts) ---
font_list = db.get("Font_Style", [])
if not font_list:
    font_list = ["Gothic", "Liquid", "Chrome", "Typewriter"]

# ==========================================
# 3. 控制台 (UI Control)
# ==========================================
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    target_lang = st.selectbox("1. 选择语种 (Language)", lang_keys)

with c2:
    # 核心玩法：增加【🎲 随机抽取】选项
    # 把“随机”放在第一个，作为默认
    ref_options = ["🎲 随机抽取 (Random Blind Box)"] + list(ref_map.keys())
    selected_ref_name = st.selectbox("2. 选择母本 (Reference)", ref_options)

    # 逻辑：如果是随机，就什么都不显示(或显示个问号)；如果是选中某张，就预览
    current_ref_url = ""
    if "随机" in selected_ref_name:
        st.caption("✨ 每一张方案将自动匹配不同的风格图")
    else:
        current_ref_url = ref_map.get(selected_ref_name, "")
        if current_ref_url:
            st.image(current_ref_url, width=150, caption="已锁定风格")

with c3:
    selected_font = st.selectbox("3. 字体风格 (Font)", ["Random"] + font_list)

# ==========================================
# 4. 生成配置与执行
# ==========================================
st.divider()
col_input, col_btn = st.columns([3, 1])

with col_input:
    manual_word = st.text_input("手动输入单词 (Manual Input)", placeholder="留空则从词库自动抽取...")

with col_btn:
    qty = st.number_input("生成数量 (Batch Size)", 1, 10, 4)
    st.write("") 
    run_btn = st.button("🚀 立即组装 (Generate)", type="primary", use_container_width=True)

# ==========================================
# 5. 核心组装逻辑 (Pipeline)
# ==========================================
if run_btn:
    results = []
    
    # 获取词库列表 (如果需要随机抽词)
    words_pool = []
    if not manual_word:
        if "Demo" in target_lang:
            words_pool = ["LOVE", "HOPE", "FATE", "SOUL"]
        else:
            words_pool = db.get(target_lang, [])

    for i in range(qty):
        # --- Step 1: 确定单词 ---
        if manual_word:
            word = manual_word
        else:
            word = random.choice(words_pool) if words_pool else "LOVE"

        # --- Step 2: 确定图片 (关键逻辑) ---
        img_url = ""
        if "随机" in selected_ref_name and ref_map:
            # 真正的盲盒：每一次循环都重新随机抽一张图
            random_key = random.choice(list(ref_map.keys()))
            img_url = ref_map[random_key]
        else:
            # 锁定模式：用选定的那张
            img_url = current_ref_url
        
        # --- Step 3: 确定字体 ---
        font = selected_font
        if font == "Random":
            font = random.choice(font_list)

        # --- Step 4: 组装 Prompt ---
        # 格式: [URL] Tattoo design of '[Word]', [Font] style... --iw 2
        
        if img_url:
            prompt = f"{img_url} Tattoo design of the word '{word}', {font} style typography, clean white background, high contrast, ink lines --iw 2"
        else:
            # 万一没图的兜底
            prompt = f"Tattoo design of the word '{word}', {font} style typography, clean white background"

        # 封装
        results.append(f"**方案{i+1}：** {prompt}")

    # 存入 Session
    st.session_state.final_solutions = results
    st.rerun()

# ==========================================
# 6. 结果展示
# ==========================================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.success(f"已生成 {len(st.session_state.final_solutions)} 组盲盒方案")
    
    for res in st.session_state.final_solutions:
        # 这里只显示文本，实际 URL 已经在里面了
        st.info(res)
        
    if st.button("📦 前往自动化中心投递", use_container_width=True):
        st.switch_page("pages/03_🚀_Automation.py")
