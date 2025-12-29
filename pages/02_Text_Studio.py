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

# 上传控件 Key 初始化
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0



# ===========================
# 2. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
available_langs = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

# ===========================
# 3. 顶部：极简上传
# ===========================
st.markdown("## Text Studio")

# 只需要一个上传条，上传完自动刷新，新图会自动排在画廊第一位
uploaded_file = st.file_uploader(
    "📤 Drop image here to add to Library", 
    type=['jpg', 'png', 'jpeg', 'webp'],
    key=f"uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    save_dir = "images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_path = os.path.join(save_dir, uploaded_file.name)
    
    # 保存
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 状态重置与刷新
    st.session_state.uploader_key += 1
    st.toast(f"✅ Added: {uploaded_file.name}")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 4. 核心交互：时间倒序画廊
# ===========================
# 获取图片并按修改时间倒序排列 (Newest First)
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
all_files = [v for v in raw_map.values() if v]

# 排序逻辑：获取完整路径 -> 获取mtime -> 倒序
full_paths = [(f, os.path.join("images", f)) for f in all_files]
# 过滤掉不存在的文件
valid_files = [x for x in full_paths if os.path.exists(x[1])]
# 按修改时间排序 (从新到旧)
valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
# 只取文件名
sorted_image_files = [x[0] for x in valid_files]

# 控制栏
c_gal_title, c_gal_ctrl = st.columns([3, 1])
with c_gal_title:
    st.subheader("Visual Library")
with c_gal_ctrl:
    use_global_blind = st.toggle("🎲 Random All", value=False)

selected_images = []

if not use_global_blind:
    if not sorted_image_files:
        st.info("Gallery is empty. Upload an image above.")
    else:
        # 5列布局
        cols = st.columns(5)
        for idx, file_name in enumerate(sorted_image_files):
            file_path = os.path.join("images", file_name)
            
            col = cols[idx % 5]
            with col:
                # 1. 勾选框 (CSS 把它浮在图片左上角)
                # key 必须唯一，使用文件名
                is_checked = st.checkbox("select", key=f"chk_{file_name}")
                
                # 2. 图片展示 (根据选中状态改变样式)
                if is_checked:
                    # 选中态：使用 HTML 注入带边框的图片 (Streamlit 原生无法加边框)
                    st.markdown(
                        f'<img src="app/static/{file_name}" style="border: 5px solid #00FF00; box-sizing: border-box; border-radius: 8px; width:100%; display:block;">', 
                        unsafe_allow_html=True
                    )
                    # 此时不渲染 st.image，避免重复，但需要用一个看不见的 st.image 占位来保持 Grid 高度一致吗？
                    # 不需要，HTML img 标签足够了。但为了保险起见，如果是本地运行，src路径可能需要调整
                    # Streamlit 本地图片显示 trick: 直接用 st.image 最稳，但无法加边框。
                    # 变通：选中时显示原图 + 下方文字提示，或者用 st.image 渲染但接受没有边框，只靠 ✅ 提示
                    
                    # 方案 B (最稳健)：依然用 st.image，但利用 CSS 全局类名高亮 (较难精准定位)
                    # 方案 C (当前采用)：既然要明显，就用 st.image 但在上面加个明显的 ✅
                    
                    # 回退到 st.image 以确保图片一定能显示 (HTML src 在不同环境路径很难搞)
                    # 我们用一个简单的办法：选中时，在图片上方显示一行绿色文字
                    st.image(file_path, use_container_width=True)
                    st.markdown(":white_check_mark: **SELECTED**") # 强提示
                    selected_images.append(file_name)
                else:
                    # 未选中态
                    st.image(file_path, use_container_width=True)
                    st.write("") # 占位对齐

# 底部浮动提示
if selected_images:
    st.info(f"✅ {len(selected_images)} images selected. AI will pick randomly from them.")

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
                    if sorted_image_files: img_val = random.choice(sorted_image_files)
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
