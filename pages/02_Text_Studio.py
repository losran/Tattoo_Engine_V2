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
# 1. 初始化
# ===========================
st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ===========================
# 2. 本页专属 CSS (画廊特效)
# ===========================
# 这里的样式只在这个脚本运行时注入，刷新或切换页面后失效，不会污染全局
st.markdown("""
<style>
    /* 1. 隐藏 Checkbox 原生文字，只留点击框 */
    div[data-testid="stCheckbox"] label span { display: none; }
    
    /* 2. 将勾选框定位到图片左上角 */
    div[data-testid="stCheckbox"] {
        position: absolute;
        top: 5px;
        left: 5px;
        z-index: 100;
        background-color: rgba(0,0,0,0.4); /* 给个半透明底让框框更明显 */
        border-radius: 4px;
        padding-left: 2px;
        width: 30px;
        height: 30px;
    }
    
    /* 3. 图片容器定位基准 */
    div[data-testid="stImage"] {
        position: relative; 
    }
    
    /* 4. 删除按钮红色警示 */
    button[kind="secondary"] {
        color: #ff4444 !important;
        border-color: #ff4444 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #330000 !important;
        border-color: #ff0000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# 3. 数据准备
# ===========================
db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Gothic", "Chrome"]
available_langs = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

# ===========================
# 4. 顶部：上传区
# ===========================
st.markdown("## Text Studio")

uploaded_file = st.file_uploader(
    "📤 Upload Reference Image", 
    type=['jpg', 'png', 'jpeg', 'webp'],
    key=f"uploader_{st.session_state.uploader_key}",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    save_dir = "images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state.uploader_key += 1
    st.toast(f"✅ Saved: {uploaded_file.name}")
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===========================
# 5. 核心交互：对勾画廊
# ===========================
raw_map = fetch_image_refs_auto()
if not isinstance(raw_map, dict): raw_map = {}
all_files = [v for v in raw_map.values() if v]

# 排序：新图在前
full_paths = [(f, os.path.join("images", f)) for f in all_files]
valid_files = [x for x in full_paths if os.path.exists(x[1])]
valid_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
sorted_image_files = [x[0] for x in valid_files]

# 标题栏 + 删除按钮占位
c_head, c_del = st.columns([3, 1])
with c_head:
    st.subheader("Visual Library")
del_btn_container = c_del.empty()

selected_images = []

if not sorted_image_files:
    st.info("Gallery is empty.")
else:
    cols = st.columns(5)
    for idx, file_name in enumerate(sorted_image_files):
        file_path = os.path.join("images", file_name)
        col = cols[idx % 5]
        
        with col:
            # 1. 勾选框 (左上角)
            is_checked = st.checkbox("Select", key=f"chk_{file_name}")
            
            # 2. 选中态：覆盖大绿勾 ✅
            if is_checked:
                selected_images.append(file_name)
                # 使用 absolute 定位，把对勾直接“钉”在图片中心
                st.markdown(
                    """
                    <div style="
                        position: absolute; 
                        top: 50%; 
                        left: 50%; 
                        transform: translate(-50%, -50%); 
                        font-size: 50px; 
                        color: #00FF00; 
                        text-shadow: 0 0 10px #000; 
                        z-index: 99; 
                        pointer-events: none;
                    ">✅</div>
                    """, 
                    unsafe_allow_html=True
                )
                # 图片稍微变暗，让对勾更明显
                st.markdown(
                    f'<img src="app/static/{file_name}" style="width:100%; border-radius:8px; filter: brightness(0.7);">', 
                    unsafe_allow_html=True
                )
                # st.image(file_path) # 备用方案，如果上面 HTML 图片不显示请解开这行
            else:
                # 未选中：普通显示
                st.image(file_path, use_container_width=True)
            
            st.write("") # 垂直对齐修正

# --- 动态删除按钮 ---
if selected_images:
    if del_btn_container.button(f"🗑️ Delete ({len(selected_images)})", type="secondary", use_container_width=True):
        count = 0
        for img in selected_images:
            p = os.path.join("images", img)
            if os.path.exists(p):
                os.remove(p)
                count += 1
        st.toast(f"Deleted {count} images")
        time.sleep(1)
        st.rerun()

st.divider()

# ===========================
# 6. 生成控制
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

if selected_images:
    st.caption(f"✨ Generating from **{len(selected_images)} selected images**.")
else:
    st.caption("🎲 Mode: Text Only.")

# ===========================
# 7. 生成逻辑
# ===========================
if run_btn:
    try:
        with st.spinner("Processing..."):
            results = []
            words_pool = db.get(target_lang, []) or ["LOVE", "HOPE"]

            for i in range(qty):
                word = manual_word.strip() if manual_word.strip() else random.choice(words_pool)
                
                img_val = ""
                if selected_images:
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
# 8. 结果展示
# ===========================
if "text_solutions" in st.session_state and st.session_state.text_solutions:
    st.write("") 
    st.subheader("Results")
    
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
