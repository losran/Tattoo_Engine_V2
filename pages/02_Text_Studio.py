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
# 1. 初始化与 CSS 魔法
# ===========================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

# 初始化上传器状态 Key，用于重置控件解决闪屏问题
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "last_uploaded_img" not in st.session_state:
    st.session_state.last_uploaded_img = None

# --- CSS: 极简画廊样式 ---
st.markdown("""
<style>
    /* 1. 隐藏 Checkbox 的 Label，只留框框 */
    div[data-testid="stCheckbox"] label { display: none; }
    
    /* 2. 调整 Checkbox 位置，让它看起来像在图片上 */
    div[data-testid="stCheckbox"] {
        margin-bottom: -20px; /* 负边距，让框框贴近图片 */
        margin-left: 5px;
        z-index: 10;
        position: relative;
    }
    
    /* 3. 图片容器基础样式 */
    div[data-testid="stImage"] img {
        border-radius: 8px;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 2. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
available_langs = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

# ===========================
# 3. 顶部：极简上传与预览
# ===========================
st.markdown("## Text Studio")

col_upload, col_preview_new = st.columns([2, 1])

with col_upload:
    # 使用动态 Key，上传完自动 +1 重置，解决闪屏死循环
    uploaded_file = st.file_uploader(
        "📤 Import Reference (Drag & Drop)", 
        type=['jpg', 'png', 'jpeg', 'webp'],
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        save_dir = "images"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        file_path = os.path.join(save_dir, uploaded_file.name)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 更新状态
        st.session_state.last_uploaded_img = file_path
        st.session_state.uploader_key += 1 # 关键：重置上传控件
        st.toast(f"✅ Saved: {uploaded_file.name}")
        st.rerun() # 刷新页面显示新图

with col_preview_new:
    # 显示刚刚上传的那张图 (实时预览)
    if st.session_state.last_uploaded_img and os.path.exists(st.session_state.last_uploaded_img):
        st.caption("Newest Upload:")
        st.image(st.session_state.last_uploaded_img, width=150)

st.divider()

# ===========================
# 4. 核心交互：无缝画廊
# ===========================
# 获取图片列表
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
image_files = [v for v in raw_map.values() if v]

# 控制栏
c_gal_title, c_gal_ctrl = st.columns([3, 1])
with c_gal_title:
    st.subheader("Visual Library")
with c_gal_ctrl:
    use_global_blind = st.toggle("🎲 Random All (Ignore Select)", value=False)

selected_images = []

if not use_global_blind:
    if not image_files:
        st.info("Gallery is empty.")
    else:
        # 5列布局，视觉更加紧凑
        cols = st.columns(5)
        for idx, file_name in enumerate(image_files):
            file_path = os.path.join("images", file_name)
            
            if os.path.exists(file_path):
                col = cols[idx % 5]
                with col:
                    # 1. 勾选框 (无Label，紧贴图片)
                    is_checked = st.checkbox("select", key=f"chk_{file_name}")
                    
                    # 2. 图片展示 (根据选中状态改变样式)
                    if is_checked:
                        # 选中态：加粗绿色边框
                        st.markdown(
                            f'<img src="app/static/{file_name}" style="border: 4px solid #4CAF50; border-radius: 8px; width:100%;">', 
                            unsafe_allow_html=True
                        )
                        # 注意：Streamlit 原生 st.image 无法直接加 border，
                        # 这里依然用 st.image 保证兼容性，但通过上方的 checkbox 视觉关联
                        st.image(file_path, use_container_width=True)
                        selected_images.append(file_name)
                    else:
                        # 未选中态：普通显示
                        st.image(file_path, use_container_width=True)

st.write("")
# 如果有选中，在底部显示一个浮动提示条
if selected_images:
    st.markdown(f"""
    <div style="background:#1e1e1e; color:#4CAF50; padding:10px; border-radius:5px; text-align:center; margin-bottom:20px;">
       ✅ <b>{len(selected_images)}</b> images selected for random generation
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===========================
# 5. 底部操作区 (极简)
# ===========================
c_lang, c_font, c_qty, c_go = st.columns([1, 1, 0.8, 1])
with c_lang:
    target_lang = st.selectbox("Lang", available_langs, label_visibility="collapsed")
with c_font:
    selected_font = st.selectbox("Font", ["Random"] + font_list, label_visibility="collapsed")
with c_qty:
    qty = st.number_input("Qty", 1, 10, 4, label_visibility="collapsed")
with c_go:
    run_btn = st.button("🚀 GENERATE", type="primary", use_container_width=True)

manual_word = st.text_input("Custom Text", placeholder="Input text here (Optional)...", label_visibility="collapsed")

# ===========================
# 6. 生成逻辑
# ===========================
if run_btn:
    try:
        with st.spinner("Processing..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                if use_global_blind:
                    if image_files: img_val = random.choice(image_files)
                elif selected_images:
                    img_val = random.choice(selected_images)
                
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
        st.error(str(e))

# ===========================
# 7. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("Gallery Results")
    
    for item in st.session_state.text_solutions:
        with st.container(border=True):
            col_img, col_text = st.columns([1, 4])
            
            with col_img:
                if item["image_file"]:
                    full_path = os.path.abspath(os.path.join("images", item["image_file"]))
                    if os.path.exists(full_path):
                        st.image(full_path, use_container_width=True)
            
            with col_text:
                st.markdown(f"**Prompt:** {item['prompt_text']}")

    st.write("")
    if st.button("Import to Automation", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state:
            st.session_state.global_queue = []
        pure_texts = [item["prompt_text"] for item in st.session_state.text_solutions]
        st.session_state.global_queue.extend(pure_texts)
        st.switch_page("pages/03_Automation.py")
