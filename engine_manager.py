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
    # --- Graphic Core ---
    "Subject":       "data/graphic/subjects.txt",
    "Action":        "data/graphic/actions.txt",
    
    # --- Style Matrix ---
    "StyleSystem":   "data/graphic/styles_system.txt",
    "Technique":     "data/graphic/styles_technique.txt",
    "Color":         "data/graphic/styles_color.txt",
    "Texture":       "data/graphic/styles_texture.txt",
    "Composition":   "data/graphic/styles_composition.txt",
    "Accent":        "data/graphic/styles_accent.txt",
    
    # --- Atmosphere ---
    "Mood":          "data/common/moods.txt",
    "Usage":         "data/common/usage.txt",
    
    # --- Text Asset ---
    "Text_English":  "data/text/text_en.txt",
    "Text_Spanish":  "data/text/text_es.txt",
    "Font_Style":    "data/text/fonts.txt",
    "Ref_Images":    "data/text/ref_images.txt"
}

# ==========================================
# 2. 数据初始化
# ==========================================
def fetch_repo_file(filepath):
    """读取文件内容"""
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
    """初始化数据"""
    if "db_all" not in st.session_state:
        st.session_state.db_all = {}
        
    for key, path in WAREHOUSE.items():
        if key not in st.session_state.db_all:
            st.session_state.db_all[key] = fetch_repo_file(path)

# ==========================================
# 3. 数据保存
# ==========================================
def save_data(file_key, new_list):
    logic_key = [k for k, v in WAREHOUSE.items() if v == file_key]
    if logic_key:
        st.session_state.db_all[logic_key[0]] = new_list

# ==========================================
# 4. 侧边栏 (Sidebar) - 垂直清单版 (Vertical List)
# ==========================================
def render_sidebar():
    with st.sidebar:
        # Logo
        st.logo("images/logo.png", icon_image="images/logo.png")
        
        st.subheader("Console")
        st.markdown("---")
        
        # 库存监控 (垂直排列，不分栏，最稳)
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # --- Part 1: Graphic ---
            st.markdown("### Graphic Core")
            st.markdown(f"**Subject:** {len(db.get('Subject', []))}")
            st.markdown(f"**Action:** {len(db.get('Action', []))}")
            
            st.markdown("---")
            
            # --- Part 2: Style ---
            st.markdown("### Style Matrix")
            st.markdown(f"**System:** {len(db.get('StyleSystem', []))}")
            st.markdown(f"**Technique:** {len(db.get('Technique', []))}")
            st.markdown(f"**Color:** {len(db.get('Color', []))}")
            st.markdown(f"**Texture:** {len(db.get('Texture', []))}")
            st.markdown(f"**Composition:** {len(db.get('Composition', []))}")
            st.markdown(f"**Accent:** {len(db.get('Accent', []))}")
            
            st.markdown("---")
            
            # --- Part 3: Assets ---
            st.markdown("### Assets")
            st.markdown(f"**Mood:** {len(db.get('Mood', []))}")
            st.markdown(f"**Words:** {len(db.get('Text_English', []))}")
            st.markdown(f"**Refs:** {len(db.get('Ref_Images', []))}")

# ==========================================
# 5. 图库扫描
# ==========================================
@st.cache_data(ttl=600)
def fetch_image_refs_auto():
    refs = {}
    
    # 1. 扫描本地 'images' 文件夹
    local_img_dir = "images"
    
    if os.path.exists(local_img_dir):
        try:
            files = os.listdir(local_img_dir)
            # 过滤图片后缀
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
            
            for file in files:
                if file.lower().endswith(valid_exts):
                    # 获取文件名作为选项名
                    key_name = os.path.splitext(file)[0]
                    # 将文件名存入，供 Prompt 生成
                    refs[f"📂 {key_name}"] = file 
        except Exception as e:
            print(f"Error: {e}")
            
    # 2. 如果文件夹是空的，给两个保底链接，防止列表报错
    if not refs:
        refs["Old School"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Sailor_Jerry_Flash.jpg/640px-Sailor_Jerry_Flash.jpg"
        
    return refs
