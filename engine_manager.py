import streamlit as st
import os

# ==========================================
# 1. 本地仓库映射 (完全对应你的文件截图)
# ==========================================
# 这里的路径必须和你截图里的一模一样
WAREHOUSE = {
    # --- Graphic Core (data/graphic) ---
    "Subject":       "data/graphic/subjects.txt",
    "Action":        "data/graphic/actions.txt",
    "StyleSystem":   "data/graphic/styles_system.txt",
    "Technique":     "data/graphic/styles_technique.txt",
    "Color":         "data/graphic/styles_color.txt",
    "Texture":       "data/graphic/styles_texture.txt",
    "Composition":   "data/graphic/styles_composition.txt",
    "Accent":        "data/graphic/styles_accent.txt",
    
    # --- Atmosphere (data/common) ---
    "Mood":          "data/common/moods.txt",
    "Usage":         "data/common/usage.txt",
    
    # --- Text Asset (data/text) ---
    "Text_English":  "data/text/text_en.txt",
    "Text_Spanish":  "data/text/text_es.txt",
    "Font_Style":    "data/text/fonts.txt",
    "Ref_Images":    "data/text/ref_images.txt"
}

# ==========================================
# 2. 数据读取与初始化 (Local First)
# ==========================================
def read_local_file(filepath):
    """直接读取本地 txt 文件"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                # 读取非空行，并去除首尾空格
                return [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []
    return []

def init_data():
    """初始化数据到 Session State"""
    if "db_all" not in st.session_state:
        st.session_state.db_all = {}
        
    for key, path in WAREHOUSE.items():
        # 如果内存里没有数据，或者数据为空，就去硬盘读一次
        if key not in st.session_state.db_all or not st.session_state.db_all[key]:
            data = read_local_file(path)
            # 如果本地文件还没建，给个默认空列表防止报错
            st.session_state.db_all[key] = data if data else []

# ==========================================
# 3. 数据保存 (持久化到本地 txt)
# ==========================================
def save_data(file_key, new_list):
    """
    当你在网页上添加新词时，直接写回本地 txt 文件
    """
    # 1. 更新内存
    target_key = None
    for k, v in WAREHOUSE.items():
        if v == file_key:
            target_key = k
            break
            
    if target_key:
        st.session_state.db_all[target_key] = new_list
    
    # 2. 写入硬盘
    # 自动创建父文件夹 (如果不存在)
    os.makedirs(os.path.dirname(file_key), exist_ok=True)
    
    try:
        with open(file_key, "w", encoding="utf-8") as f:
            # 每个词占一行
            f.write("\n".join(new_list))
    except Exception as e:
        st.error(f"Save failed: {e}")

# ==========================================
# 4. 侧边栏 (Sidebar)
# ==========================================
def render_sidebar():
    with st.sidebar:
        try:
            # 如果你有 logo 图片，这里会显示
            if os.path.exists("images/logo.png"):
                st.image("images/logo.png", width=60)
            st.markdown("### IVIØD ENGINE")
        except:
            st.markdown("### TATTOO ENGINE")
        
        st.markdown("---")
        st.caption("Local Warehouse Status")
        
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # 使用折叠栏让侧边栏更干净
            with st.expander("🎨 Graphic Assets", expanded=True):
                st.caption(f"Sub: {len(db.get('Subject', []))} | Act: {len(db.get('Action', []))}")
                st.caption(f"Style: {len(db.get('StyleSystem', []))} | Tech: {len(db.get('Technique', []))}")
            
            with st.expander("🔤 Text Assets", expanded=False):
                st.caption(f"Fonts: {len(db.get('Font_Style', []))} | Refs: {len(db.get('Ref_Images', []))}")

# ==========================================
# 5. 图片库扫描 (images 文件夹)
# ==========================================
def fetch_image_refs_auto():
    refs = {}
    
    # 1. 扫描你的本地 'images' 文件夹
    local_img_dir = "images"
    
    if os.path.exists(local_img_dir):
        try:
            files = os.listdir(local_img_dir)
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
            
            count = 0
            for file in files:
                if file.lower().endswith(valid_exts):
                    key_name = os.path.splitext(file)[0]
                    # Key: 显示的名字 (加个文件夹图标)
                    # Value: 文件名
                    refs[f"📂 {key_name}"] = file 
                    count += 1
            # print(f"Found {count} images in {local_img_dir}") # 调试用
            
        except Exception as e:
            print(f"Error scanning images: {e}")
            
    # 2. 只有当文件夹真是空的时候，才给保底
    if not refs:
        refs["(No Local Images)"] = ""
        
    return refs
