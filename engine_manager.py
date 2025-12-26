# engine_manager.py
import streamlit as st
import requests
import base64

# ===========================
# 1. 配置区域 (Config)
# ===========================
# 请确保你的 .streamlit/secrets.toml 里有 GITHUB_TOKEN
# REPO 格式: "你的用户名/你的仓库名"
REPO = "losran/mod"  # ⚠️ 记得改成你新的仓库名 (例如: yourname/tattoo_engine_v2)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# ===========================
# 2. 仓库地图 (The Map) 🗺️
# ===========================
# 这里定义了所有资产的物理位置，按照 V2 架构严格物理隔离
WAREHOUSE = {
    # === A. 公共基础区 (Common) ===
    "Mood": "data/common/moods.txt",          # 情绪 (通用)
    "Usage": "data/common/usage.txt",         # 部位 (通用)

    # === B. 图形纹身区 (Graphic Assets) ===
    "Subject": "data/graphic/subjects.txt",   # 主体 (如: 骷髅, 蛇)
    "Style": "data/graphic/styles.txt",       # 风格 (如: Old School)
    "Action": "data/graphic/actions.txt",     # 动态 (如: 燃烧, 缠绕)
    
    # === C. 文字纹身区 (Text Assets) ===
    # 这里的 Text_ 前缀很重要，02页面会自动识别所有带 Text_ 的库
    "Text_English": "data/text/text_en.txt",  # 英文词库
    "Text_Spanish": "data/text/text_es.txt",  # 西语词库
    "Text_German": "data/text/text_de.txt",   # 德语词库 (预留)
    
    "Font_Style": "data/text/fonts.txt",      # 字体风格
    "Ref_Images": "data/text/ref_images.txt"  # ⚠️ 核心资产：母本图链接
}

# ===========================
# 3. 核心功能 (Core Functions)
# ===========================
@st.cache_data(ttl=600)
def fetch_repo_data():
    """从 GitHub 拉取所有数据到内存"""
    data_map = {}
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    for k, path in WAREHOUSE.items():
        try:
            url = f"https://api.github.com/repos/{REPO}/contents/{path}"
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                content = base64.b64decode(r.json()["content"]).decode()
                # 按行分割，并过滤空行
                data_map[k] = [i.strip() for i in content.splitlines() if i.strip()]
            else:
                data_map[k] = [] # 如果文件不存在，返回空列表，防止报错
        except Exception as e:
            print(f"Error fetching {k}: {e}")
            data_map[k] = []
            
    return data_map

def save_data(path, data_list):
    """将数据写回 GitHub (用于 CMS 管理)"""
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        # 1. 先获取文件的 SHA (更新文件必须提供)
        old_resp = requests.get(url, headers=headers).json()
        sha = old_resp.get("sha")
        
        # 2. 准备内容 (去重 + 排序)
        content_str = "\n".join(sorted(list(set(data_list))))
        b64_content = base64.b64encode(content_str.encode()).decode()
        
        # 3. 推送更新
        payload = {
            "message": "update via tattoo engine v2",
            "content": b64_content,
            "sha": sha
        }
        r = requests.put(url, headers=headers, json=payload)
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"Save error: {e}")
        return False

def init_data():
    """初始化 Session State，确保页面加载时有数据"""
    if "db_all" not in st.session_state:
        st.session_state.db_all = fetch_repo_data()

# ===========================
# 4. 侧边栏渲染 (Sidebar UI)
# ===========================
def render_sidebar():
    # 引入样式
    try:
        from style_manager import apply_pro_style
        apply_pro_style()
    except ImportError:
        pass # 防止 style_manager 还没创建时报错

    init_data()
    
    with st.sidebar:
        st.header("Engine V2 Console")
        st.markdown("---")
        
        # 分区展示库存状态
        st.caption("📦 Inventory Status")
        
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # 简单统计一下
            graphic_count = len(db.get("Subject", []))
            text_count = len(db.get("Text_English", [])) + len(db.get("Text_Spanish", []))
            ref_count = len(db.get("Ref_Images", []))
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Graphic", graphic_count)
            col_b.metric("Words", text_count)
            col_c.metric("Refs", ref_count)
            
            st.markdown("---")
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                del st.session_state.db_all
                st.rerun()
        else:
            st.warning("Connecting to Warehouse...")


# ... (保留上面的 WAREHOUSE 和 Config 不变) ...

@st.cache_data(ttl=600)
def fetch_image_refs_auto():
    """
    全自动扫描 images 文件夹，获取所有图片的直链
    不需要手动维护 ref_images.txt 了！
    """
    image_refs = {}
    url = f"https://api.github.com/repos/{REPO}/contents/images"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            files = r.json()
            # 遍历返回的文件列表
            for f in files:
                fname = f["name"]
                # 只认图片文件
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    # 生成直链 (Raw URL)
                    # 格式: https://raw.githubusercontent.com/用户名/仓库名/main/images/文件名
                    # 注意: GitHub API 返回的 download_url 就是直链，直接用它最稳
                    raw_url = f.get("download_url")
                    if raw_url:
                        # 用文件名当临时的 Key，虽然乱点但能用
                        image_refs[fname] = raw_url
        else:
            print(f"扫描图片失败: {r.status_code}")
    except Exception as e:
        print(f"扫描出错: {e}")
        
    return image_refs
