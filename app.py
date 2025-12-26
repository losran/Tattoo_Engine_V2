import streamlit as st
import json
import os
from openai import OpenAI
from engine_manager import render_sidebar, init_data, save_data
from style_manager import apply_pro_style

# ===========================
# Configuration
# ===========================
st.set_page_config(layout="wide", page_title="Tattoo Engine V2", page_icon="🧠")
apply_pro_style()
render_sidebar()

# 尝试从 engine_manager 导入配置，如果失败则使用默认配置 (防崩设计)
try:
    from engine_manager import WAREHOUSE
except ImportError:
    # 默认仓库结构定义
    WAREHOUSE = {
        "Subject": "subjects.txt",
        "StyleSystem": "styles.txt",
        "Technique": "techniques.txt", 
        "Mood": "moods.txt",
        "Action": "actions.txt",
        "Color": "colors.txt",
        "Texture": "textures.txt",
        "Composition": "compositions.txt",
        "Usage": "usages.txt",
        "Accent": "accents.txt",
        "Text_English": "text_en.txt",
        "Text_Spanish": "text_es.txt"
    }

# ===========================
# Logic & Helpers
# ===========================
client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(
            api_key=st.secrets["DEEPSEEK_KEY"],
            base_url="https://api.deepseek.com"
        )
    except:
        pass

# Session State Init
if "ai_results" not in st.session_state:
    st.session_state.ai_results = []
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "db_all" not in st.session_state:
    init_data()

# ===========================
# UI Layout
# ===========================
st.title("🧠 Tattoo Engine V2")
st.caption("Smart Ingest (智能采集) → Warehouse (资产沉淀)")
st.divider()

center, right = st.columns([4, 2])

# --- Left Column: Smart Ingest ---
with center:
    st.subheader("💡 Smart Ingest (智能拆解)")
    st.session_state.input_text = st.text_area(
        "输入灵感 (Inspiration Input)",
        st.session_state.input_text,
        height=220,
        placeholder="在这里描述你的纹身想法，或者粘贴一堆混乱的关键词...\nAI 会自动识别并分类归档。"
    )

    if st.button("⚡ 开始分析与拆解 (Start Analysis)", use_container_width=True):
        if not st.session_state.input_text:
            st.warning("输入不能为空")
        elif not client:
            st.error("DeepSeek Key 未配置")
        else:
            with st.spinner("DeepSeek 正在思考并拆解你的灵感..."):
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
                
                可用Key: {", ".join(WAREHOUSE.keys())}

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
                    
                    # JSON Parsing Logic
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
                        st.warning("JSON 解析失败，切换到回退模式...")
                        # 简单的兜底解析
                        parsed.append({"cat": "Subject", "val": "解析失败请手动录入"})

                    st.session_state.ai_results = parsed

                except Exception as e:
                    st.error(f"请求错误: {e}")

    # Display Results
    if st.session_state.ai_results:
        st.success(f"成功提取 {len(st.session_state.ai_results)} 个关键词")
        st.markdown("##### 确认入库 (Verify & Import)")
        
        selected = []
        cols = st.columns(3)
        for i, item in enumerate(st.session_state.ai_results):
            with cols[i % 3]:
                if st.checkbox(f'**{item["cat"]}** · {item["val"]}', key=f'chk_{i}', value=True):
                    selected.append(item)
        
        st.write("")
        if st.button("📥 确认存入仓库 (Confirm Import)", type="primary", use_container_width=True):
            if "db_all" not in st.session_state:
                init_data()
            
            changed_cats = set()
            for item in selected:
                cat, val = item["cat"], item["val"]
                if cat not in st.session_state.db_all:
                    st.session_state.db_all[cat] = []
                    
                current = st.session_state.db_all[cat]
                if val not in current:
                    current.append(val)
                    st.session_state.db_all[cat] = current
                    changed_cats.add(cat)
            
            if changed_cats:
                with st.spinner("正在写入 GitHub 仓库..."):
                    # 尝试调用 engine_manager 的保存，如果不存在则仅更新 Session
                    try:
                        for c in changed_cats: 
                            save_data(WAREHOUSE[c], st.session_state.db_all[c])
                        st.success("入库成功！")
                    except Exception as e:
                        st.warning(f"本地保存成功，但 GitHub 同步可能失败: {e}")
                
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.info("没有新的关键词需要入库。")

# --- Right Column: Warehouse Manager ---
with right:
    st.subheader("📦 仓库管理")
    cat = st.selectbox("选择分类 (Category)", list(WAREHOUSE.keys()))
    
    words = st.session_state.db_all.get(cat, [])

    with st.container(height=500):
        if not words:
            st.caption("暂无数据 (No Data)")
        for w in words:
            c1, c2 = st.columns([4, 1]) 
            with c1:
                # 点击词条反哺到输入框
                if st.button(w, key=f"add_{w}", use_container_width=True):
                    st.session_state.input_text += f" {w}"
            with c2:
                # 删除词条
                if st.button("✕", key=f"del_{cat}_{w}"):
                    new_list = [i for i in words if i != w]
                    st.session_state.db_all[cat] = new_list
                    try:
                        save_data(WAREHOUSE[cat], new_list)
                    except:
                        pass
                    st.rerun()
