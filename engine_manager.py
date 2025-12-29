import streamlit as st
import os

# ==========================================
# 1. 本地仓库映射
# ==========================================
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
# 2. 数据读取与初始化
# ==========================================
def read_local_file(filepath):
    """直接读取本地 txt 文件"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except:
            return []
    return []

def init_data():
    if "db_all" not in st.session_state:
        st.session_state.db_all = {}
        
    for key, path in WAREHOUSE.items():
        if key not in st.session_state.db_all or not st.session_state.db_all[key]:
            data = read_local_file(path)
            st.session_state.db_all[key] = data if data else []

# ==========================================
# 3. 数据保存
# ==========================================
def save_data(file_key, new_list):
    target_key = None
    for k, v in WAREHOUSE.items():
        if v == file_key:
            target_key = k
            break
            
    if target_key:
        st.session_state.db_all[target_key] = new_list
    
    os.makedirs(os.path.dirname(file_key), exist_ok=True)
    try:
        with open(file_key, "w", encoding="utf-8") as f:
            f.write("\n".join(new_list))
    except Exception as e:
        st.error(f"Save failed: {e}")

# ==========================================
# 4. 侧边栏 (已修复 Logo 路径 & 紧凑布局)
# ==========================================
def render_sidebar():
    with st.sidebar:
        # ✅ 修复：更新 Logo 路径为 images/logo/logo.png
        logo_path = "images/logo/logo.png"
        
        # 优先检测新路径，如果找不到再检测旧路径（做个兼容）
        if os.path.exists(logo_path):
            st.logo(logo_path, icon_image=logo_path)
        elif os.path.exists("images/logo/logo.png"):
            st.logo("images/logo/logo.png", icon_image="images/logo/logo.png")
        
        
        # 库存监控 (保持垂直清单，但合并代码减少间距，防止出现滚动条)
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # --- Part 1: Graphic ---
            st.markdown("### Graphic Core")
            # 使用紧凑写法
            st.markdown(f"""
            **Subject:** {len(db.get('Subject', []))}  
            **Action:** {len(db.get('Action', []))}
            """)
            
            st.markdown("---")
            
            # --- Part 2: Style ---
            st.markdown("### Style Matrix")
            st.markdown(f"""
            **System:** {len(db.get('StyleSystem', []))}  
            **Technique:** {len(db.get('Technique', []))}  
            **Color:** {len(db.get('Color', []))}  
            **Texture:** {len(db.get('Texture', []))}  
            **Composition:** {len(db.get('Composition', []))}  
            **Accent:** {len(db.get('Accent', []))}
            """)
            
            st.markdown("---")
            
            # --- Part 3: Assets ---
            st.markdown("### Assets")
            st.markdown(f"""
            **Mood:** {len(db.get('Mood', []))}  
            **Words:** {len(db.get('Text_English', []))}  
            **Refs:** {len(db.get('Ref_Images', []))}
            """)

# ==========================================
# 5. 图库扫描
# ==========================================
def fetch_image_refs_auto():
    refs = {}
    local_img_dir = "images"
    
    if os.path.exists(local_img_dir):
        try:
            files = os.listdir(local_img_dir)
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
            
            for file in files:
                if file.lower().endswith(valid_exts):
                    key_name = os.path.splitext(file)[0]
                    refs[f"📂 {key_name}"] = file 
        except Exception:
            pass
            
    if not refs:
        refs["(No Local Images)"] = ""
        
    return refs
