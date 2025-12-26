import streamlit as st
import os
import requests

# ==========================================
# 1. 仓库配置 (精准映射你的目录结构)
# ==========================================
REPO = "losran/Tattoo_Engine_V2"  # 请确认这是你的仓库名
BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# ⚠️ 核心映射表：左边是代码逻辑用的名字，右边是实际文件路径
WAREHOUSE = {
    # --- Graphic (图形类) ---
    "Subject":       "data/graphic/subjects.txt",
    "StyleSystem":   "data/graphic/styles_system.txt",      # 对应 styles_system.txt
    "Technique":     "data/graphic/styles_technique.txt",   # 对应 styles_technique.txt
    "Color":         "data/graphic/styles_color.txt",       # 对应 styles_color.txt
    "Texture":       "data/graphic/styles_texture.txt",     # 对应 styles_texture.txt
    "Composition":   "data/graphic/styles_composition.txt", # 对应 styles_composition.txt
    "Accent":        "data/graphic/styles_accent.txt",      # 对应 styles_accent.txt
    "Action":        "data/graphic/actions.txt",            # 对应 actions.txt
    
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
        
    # 遍历上面的 WAREHOUSE 自动加载
    for key, path in WAREHOUSE.items():
        if key not in st.session_state.db_all:
            st.session_state.db_all[key] = fetch_repo_file(path)

# ==========================================
# 3. 数据保存 (Write)
# ==========================================
def update_repo_file(filepath, content_list):
    """(高级功能) 写回 GitHub，需要完整 API 调用逻辑，此处简化为 Session 更新"""
    # 实际生产环境这里需要调用 GitHub API 的 PUT 接口
    # 为了保证演示稳定性，我们暂时只更新 Session 和 Cache
    pass

def save_data(file_key, new_list):
    """更新数据"""
    # 1. 更新内存
    # 反向查找 key 对应的逻辑名
    logic_key = [k for k, v in WAREHOUSE.items() if v == file_key]
    if logic_key:
        st.session_state.db_all[logic_key[0]] = new_list
    
    # 2. 这里的实际写回逻辑比较复杂，建议作为后续高级功能开发
    # 目前先确保 Session 内可用

# ==========================================
# 4. 侧边栏 (Sidebar)
# ==========================================
def render_sidebar():
    with st.sidebar:
        # 显示 Logo (从 images 文件夹读取)
        st.logo("images/logo.png", icon_image="images/logo.png")
        
        st.subheader("Engine V2 Console")
        st.markdown("---")
        
        # 库存监控
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            c1, c2, c3 = st.columns(3)
            c1.metric("Graphic", len(db.get("Subject", [])))
            c2.metric("Styles", len(db.get("StyleSystem", []))) # 监控核心风格
            c3.metric("Refs", len(db.get("Ref_Images", [])))
        
        st.markdown("---")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            for key in st.session_state.db_all.keys():
                del st.session_state.db_all[key]
            init_data()
            st.rerun()

# ==========================================
# 5. 图库扫描 (只看 gallery)
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
