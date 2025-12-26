import streamlit as st
import os
import requests

# ==========================================
# 1. 仓库配置
# ==========================================
REPO = "losran/Tattoo_Engine_V2"
BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# 映射表 (必须与你 GitHub 的实际文件名完全一致)
WAREHOUSE = {
    # --- Graphic Core (图形核心) ---
    "Subject":       "data/graphic/subjects.txt",
    "Action":        "data/graphic/actions.txt",
    
    # --- Style Matrix (风格矩阵) ---
    "StyleSystem":   "data/graphic/styles_system.txt",
    "Technique":     "data/graphic/styles_technique.txt",
    "Color":         "data/graphic/styles_color.txt",
    "Texture":       "data/graphic/styles_texture.txt",
    "Composition":   "data/graphic/styles_composition.txt",
    "Accent":        "data/graphic/styles_accent.txt",
    
    # --- Atmosphere (氛围) ---
    "Mood":          "data/common/moods.txt",
    "Usage":         "data/common/usage.txt",
    
    # --- Text Asset (文字资产) ---
    "Text_English":  "data/text/text_en.txt",
    "Text_Spanish":  "data/text/text_es.txt",
    "Font_Style":    "data/text/fonts.txt",
    "Ref_Images":    "data/text/ref_images.txt"
}

# ==========================================
# 2. 数据初始化 (Init)
# ==========================================
def fetch_repo_file(filepath):
    """从 GitHub 读取文件内容"""
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{filepath}"
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            lines = [line.strip() for line in r.text.split('\n') if line.strip()]
            return lines
        return []
    except:
        return []

def init_data():
    """初始化所有数据到 Session State"""
    if "db_all" not in st.session_state:
        st.session_state.db_all = {}
        
    for key, path in WAREHOUSE.items():
        if key not in st.session_state.db_all:
            st.session_state.db_all[key] = fetch_repo_file(path)

# ==========================================
# 3. 数据保存 (Write)
# ==========================================
def save_data(file_key, new_list):
    logic_key = [k for k, v in WAREHOUSE.items() if v == file_key]
    if logic_key:
        st.session_state.db_all[logic_key[0]] = new_list

# ==========================================
# 4. 侧边栏 (Sidebar) - 全景仪表盘版 📊
# ==========================================
def render_sidebar():
    with st.sidebar:
        # Logo
        st.logo("images/logo.png", icon_image="images/logo.png")
        
        st.subheader("Engine Console")
        st.markdown("---")
        
        # 库存监控 (全维度展示)
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # 1. 核心 (Core)
            c_sub = len(db.get("Subject", []))
            c_act = len(db.get("Action", []))
            
            # 2. 风格细节 (Details)
            c_sys  = len(db.get("StyleSystem", []))
            c_tech = len(db.get("Technique", []))
            c_col  = len(db.get("Color", []))
            c_tex  = len(db.get("Texture", []))
            c_comp = len(db.get("Composition", []))
            c_acc  = len(db.get("Accent", []))
            
            # 3. 氛围与文字 (Atmosphere & Text)
            c_mood = len(db.get("Mood", []))
            c_txt  = len(db.get("Text_English", []))
            c_ref  = len(db.get("Ref_Images", []))
            
            # === 渲染面板 ===
            st.caption("📦 Warehouse Status")
            
            # 分组 1: 图形基础
            with st.expander("🎨 Graphic Core", expanded=True):
                st.markdown(f"Subject: **{c_sub}**")
                st.markdown(f"Action: **{c_act}**")
            
            # 分组 2: 风格矩阵 (重点展示)
            with st.expander("💅 Style Matrix", expanded=True):
                # 使用紧凑的两列布局
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"Sys: **{c_sys}**")
                    st.markdown(f"Col: **{c_col}**")
                    st.markdown(f"Tex: **{c_tex}**")
                with c2:
                    st.markdown(f"Tech: **{c_tech}**")
                    st.markdown(f"Comp: **{c_comp}**")
                    st.markdown(f"Acc: **{c_acc}**")
            
            # 分组 3: 其他资产
            with st.expander("🔤 Text & Mood", expanded=False):
                st.markdown(f"Mood: **{c_mood}**")
                st.markdown(f"Words (En): **{c_txt}**")
                st.markdown(f"Ref Images: **{c_ref}**")
        
        st.markdown("---")
        st.caption("✅ System Online")

# ==========================================
# 5. 图库扫描
# ==========================================
@st.cache_data(ttl=600)
def fetch_image_refs_auto():
    image_refs = {}
    url = f"https://api.github.com/repos/{REPO}/contents/gallery"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            files = r.json()
            for f in files:
                fname = f["name"]
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    raw_url = f.get("download_url")
                    if raw_url:
                        image_refs[fname] = raw_url
    except:
        pass
    return image_refs
