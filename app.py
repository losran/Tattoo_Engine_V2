import streamlit as st
import json
import os
import sys
import pandas as pd
from openai import OpenAI
from github import Github  # 🔥 必须引入这个库
# ===========================
# 0. 基础路径 & 引入模块
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import render_sidebar, WAREHOUSE, init_data
from style_manager import apply_pro_style

# ========================================================
# 🔥 用这一段替换原来的 find_real_file_path 和 save_category_to_disk 🔥
# ========================================================

def find_remote_file_path(repo, category):
    """在 GitHub 仓库里找真实文件路径 (自动匹配 styles_ 等前缀)"""
    clean_cat = category.strip().lower()
    candidates = [
        f"{clean_cat}.txt",
        f"styles_{clean_cat}.txt",
        f"{clean_cat}s.txt",
        f"styles_{clean_cat}s.txt",
        f"text_{clean_cat}.txt"
    ]
    
    # 搜索 graphic 和 text 目录
    for d in ["data/graphic", "data/text"]:
        try:
            contents = repo.get_contents(d)
            for file in contents:
                if file.name.lower() in candidates:
                    return file.path
        except:
            continue
    # 默认路径
    return f"data/graphic/{category}.txt"

def save_category_to_disk(category, new_list):
    """
    连接 GitHub 并提交修改 (Commit & Push)
    """
    # 1. 获取 Secrets
    try:
        # 兼容 [general] 和直接格式
        secrets = st.secrets["general"] if "general" in st.secrets else st.secrets
        token = secrets["GITHUB_TOKEN"]
        repo_name = secrets["REPO_NAME"]
        branch = secrets.get("BRANCH", "main")
    except KeyError:
        st.error("❌ Secrets 配置缺失！请检查 GITHUB_TOKEN 和 REPO_NAME")
        return False

    # 2. 连接 GitHub
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
    except Exception as e:
        st.error(f"❌ GitHub 连接失败: {e}")
        return False

    # 3. 准备数据
    file_path = find_remote_file_path(repo, category)
    content_str = "\n".join([str(x).strip() for x in new_list if str(x).strip()])
    
    # 4. 提交更新
    msg_box = st.toast(f"⏳ 正在同步 GitHub: {file_path}...", icon="☁️")
    
    try:
        # 尝试获取文件 (为了拿 sha 进行更新)
        try:
            contents = repo.get_contents(file_path, ref=branch)
            repo.update_file(
                path=contents.path,
                message=f"Update {category} via App",
                content=content_str,
                sha=contents.sha,
                branch=branch
            )
            time.sleep(1)
            st.toast(f"✅ 同步成功！GitHub 已更新", icon="🎉")
            return True
        except:
            # 文件不存在，创建新文件
            repo.create_file(
                path=file_path,
                message=f"Create {category}",
                content=content_str,
                branch=branch
            )
            st.toast(f"✅ 新建成功！文件已创建", icon="✨")
            return True
            
    except Exception as e:
        st.error(f"💥 同步炸了: {e}")
        return False
# ===========================
# 2. 页面初始化
# ===========================
st.set_page_config(layout="wide", page_title="Tattoo Engine V2")
apply_pro_style()

# 初始化数据
if "db_all" not in st.session_state:
    init_data()

render_sidebar()

# 初始化 AI 客户端
client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(
            api_key=st.secrets["DEEPSEEK_KEY"],
            base_url="https://api.deepseek.com"
        )
    except:
        pass

# 初始化 Session State
if "ai_results" not in st.session_state: st.session_state.ai_results = []
if "input_text" not in st.session_state: st.session_state.input_text = ""

# ===========================
# 3. 界面布局
# ===========================
st.markdown("## Tattoo Engine V2") 
st.markdown("---")

col_ingest, col_warehouse = st.columns([2, 1])

# ---------------------------------------------------------
# 左侧：智能解析 (Smart Ingest)
# ---------------------------------------------------------
with col_ingest:
    st.markdown("### Smart Ingest (AI Parser)")
    
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=200,
        placeholder="在这里粘贴客户的胡言乱语，或者乱七八糟的灵感关键词...",
        label_visibility="collapsed"
    )

    if st.button("✨ Start Analysis (DeepSeek)", use_container_width=True, type="primary"):
        if not st.session_state.input_text:
            st.warning("Input is empty.")
        elif not client:
            st.error("DeepSeek API Key not found in .streamlit/secrets.toml")
        else:
            with st.spinner("AI 正在解构你的灵感..."):
                # 核心 Prompt
                prompt = f"""
                任务：将纹身描述文本拆解为结构化关键词。
                
                【重要规则】
                1. 请务必区分：
                   - Subject (主体): 具体的物体、生物 (如: 猫, 骷髅, 玫瑰)
                   - StyleSystem (风格): 艺术流派 (如: 赛博朋克, Old School, 水墨)
                   - Mood (情绪): 氛围感受 (如: 压抑, 欢快, 神圣)
                   - Action (动作): 动态 (如: 奔跑, 燃烧, 缠绕)
                2. 不要把风格和情绪全塞进 Subject！
                
                【输出格式】
                请直接返回纯 JSON 数据，不要包含 ```json 代码块标记。格式如下：
                {{
                    "Subject": ["词1", "词2"],
                    "Action": ["词1"],
                    "Mood": ["词1"],
                    "StyleSystem": ["词1"],
                    "Usage": ["词1"]
                }}
                
                可用Key: Subject, Action, Mood, Usage, StyleSystem, Technique, Color, Texture, Composition, Accent

                输入文本：{st.session_state.input_text}
                """
                
                try:
                    res_obj = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    res = res_obj.choices[0].message.content
                    
                    parsed = []
                    
                    # --- JSON 解析逻辑 ---
                    try:
                        clean_json = res.replace("```json", "").replace("```", "").strip()
                        data = json.loads(clean_json)
                        
                        for cat, words in data.items():
                            target_key = None
                            for k in WAREHOUSE:
                                if k.lower() == cat.lower() or k.lower() in cat.lower():
                                    target_key = k
                                    break
                            
                            if target_key and isinstance(words, list):
                                for w in words:
                                    if w and isinstance(w, str):
                                        parsed.append({"cat": target_key, "val": w.strip()})
                                        
                    except json.JSONDecodeError:
                        st.error("AI 返回格式异常，尝试备用解析...")
                        # 简单的备用解析逻辑可以加在这里
                    
                    st.session_state.ai_results = parsed

                except Exception as e:
                    st.error(f"API Request Error: {e}")

    # --- AI 结果交互区 ---
    if st.session_state.ai_results:
        st.divider()
        st.subheader("Analysis Results")
        st.caption("Select items to import into Warehouse")
        
        selected_to_import = []
        
        # 结果展示
        res_cols = st.columns(3)
        for i, item in enumerate(st.session_state.ai_results):
            with res_cols[i % 3]:
                # 默认全选
                if st.checkbox(f"**{item['cat']}** : {item['val']}", key=f"res_{i}", value=True):
                    selected_to_import.append(item)
        
        st.write("")
        if st.button("📥 Confirm Import to Warehouse", use_container_width=True):
            if not selected_to_import:
                st.info("No items selected.")
            else:
                changed_cats = set()
                count = 0
                for item in selected_to_import:
                    cat, val = item["cat"], item["val"]
                    # 确保 list 存在
                    if cat not in st.session_state.db_all:
                        st.session_state.db_all[cat] = []
                        
                    current_list = st.session_state.db_all[cat]
                    if val not in current_list:
                        current_list.append(val)
                        st.session_state.db_all[cat] = current_list
                        changed_cats.add(cat)
                        count += 1
                
                # 🔥 批量写入硬盘 🔥
                if changed_cats:
                    for c in changed_cats:
                        save_category_to_disk(c, st.session_state.db_all[c])
                    
                    st.toast(f"✅ Imported {count} items to Warehouse!", icon="🎉")
                    st.session_state.ai_results = [] # 清空结果
                    st.rerun()
                else:
                    st.toast("⚠️ Items already exist in Warehouse.")

# ---------------------------------------------------------
# 右侧：仓库管理 (Warehouse) - 带强制硬盘写入
# ---------------------------------------------------------
with col_warehouse:
    st.markdown("### Warehouse")
    
    # 工具栏
    c_tools_1, c_tools_2 = st.columns([2, 1])
    with c_tools_1:
        # 只显示列表类型的 Key
        valid_cats = [k for k, v in st.session_state.db_all.items() if isinstance(v, list)]
        target_cat = st.selectbox("Category", valid_cats, label_visibility="collapsed")
    with c_tools_2:
        current_words = st.session_state.db_all.get(target_cat, [])
        st.markdown(f"<div style='text-align:right; color:#888; font-size:0.8em; padding-top:10px;'>{len(current_words)} Items</div>", unsafe_allow_html=True)

    # 列表展示区
    with st.container(height=500, border=True):
        if not current_words:
            st.caption("Empty category.")
        else:
            for i, word in enumerate(current_words):
                row_c1, row_c2 = st.columns([0.8, 0.2])
                with row_c1:
                    # 点击词汇：反向添加到左侧输入框（方便二次编辑）
                    if st.button(word, key=f"word_{target_cat}_{i}", use_container_width=True):
                        st.session_state.input_text += f" {word}"
                        st.rerun()
                with row_c2:
                    # 🔥 删除功能：强制写盘 🔥
                    if st.button("✕", key=f"del_{target_cat}_{i}_{word}", use_container_width=True):
                        new_list = [w for w in current_words if w != word]
                        st.session_state.db_all[target_cat] = new_list
                        
                        # 立即写入
                        save_category_to_disk(target_cat, new_list)
                        st.rerun()

    # 底部手动添加
    st.divider()
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_word_in = st.text_input("Add New", placeholder="New tag...", label_visibility="collapsed")
    with c_add2:
        if st.button("Add", use_container_width=True):
            if new_word_in and target_cat:
                if new_word_in not in current_words:
                    current_words.append(new_word_in)
                    st.session_state.db_all[target_cat] = current_words
                    
                    # 🔥 添加功能：强制写盘 🔥
                    save_category_to_disk(target_cat, current_words)
                    
                    st.success(f"Added: {new_word_in}")
                    st.rerun()
                else:
                    st.warning("Exist!")
