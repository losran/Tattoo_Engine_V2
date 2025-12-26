import streamlit as st
import os
import requests

# ==========================================
# 1. 仓库配置
# ==========================================
REPO = "losran/Tattoo_Engine_V2"
BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# 映射表
WAREHOUSE = {
    # --- Graphic (图形类) ---
    "Subject":       "data/graphic/subjects.txt",
    "StyleSystem":   "data/graphic/styles_system.txt",
    "Technique":     "data/graphic/styles_technique.txt",
    "Color":         "data/graphic/styles_color.txt",
    "Texture":       "data/graphic/styles_texture.txt",
    "Composition":   "data/graphic/styles_composition.txt",
    "Accent":        "data/graphic/styles_accent.txt",
    "Action":        "data/graphic/actions.txt",
    
    # --- Common (通用类) ---
    "Mood":          "data/common/moods.txt",
    "Usage":         "data/common/usage.txt",
    
    # --- Text (文字类) ---
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
            return [line.strip() for line in r.text.split('\n') if line.strip()]
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
    """更新数据"""
    logic_key = [k for k, v in WAREHOUSE.items() if v == file_key]
    if logic_key:
        st.session_state.db_all[logic_key[0]] = new_list

# ==========================================
# 4. 侧边栏 (Sidebar) - 极致精简版
# ==========================================
def render_sidebar():
    with st.sidebar:
        # 1. Logo
        st.logo("images/logo.png", icon_image="images/logo.png")
        
        st.subheader("Engine V2 Console")
        st.markdown("---")
        
        # 2. 库存监控 (改用纯文本，防止被折叠)
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # 直接显示统计数字，不花里胡哨
            c_sub = len(db.get("Subject", []))
            c_sty = len(db.get("StyleSystem", []))
            c_ref = len(db.get("Ref_Images", []))
            
            st.caption("📦 Inventory Status")
            st.markdown(f"**Graphic**: {c_sub}")
            st.markdown(f"**Styles**: {c_sty}")
            st.markdown(f"**Refs**: {c_ref}")
        
        st.markdown("---")
        # 3. 刷新按钮已永久移除
        st.caption("Data auto-loaded on startup.")

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
