import streamlit as st
import json
import pandas as pd
from openai import OpenAI
from engine_manager import render_sidebar, WAREHOUSE, save_data, init_data
from style_manager import apply_pro_style

# ===========================
# 1. 基础配置
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
# 2. 界面标题
# ===========================
st.markdown("## Tattoo Engine V2") 
st.markdown("---")

# ===========================
# 3. 核心分栏布局
# ===========================
col_ingest, col_warehouse = st.columns([2, 1])

# --- 左侧：智能解析入库 ---
with col_ingest:
    st.markdown("### Smart Ingest")
    st.caption("AI Parser")
    
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=240,
        placeholder="Paste messy inspiration or keywords here...",
        label_visibility="collapsed"
    )

    if st.button("Start Analysis", use_container_width=True):
        if not st.session_state.input_text:
            st.warning("Input is empty.")
        else:
            with st.spinner("Analyzing..."):
                # 🔥 恢复你调教好的核心 Prompt 逻辑
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
                        temperature=0.1 # 保持低随机性，确保输出稳定
                    )
                    res = res_obj.choices[0].message.content
                    
                    parsed = []
                    
                    # --- 1. 深度 JSON 解析逻辑 ---
                    try:
                        clean_json = res.replace("```json", "").replace("```", "").strip()
                        data = json.loads(clean_json)
                        
                        for cat, words in data.items():
                            target_key = None
                            for k in WAREHOUSE:
                                # 模糊匹配分类，增强容错
                                if k.lower() == cat.lower() or k.lower() in cat.lower():
                                    target_key = k
                                    break
                            
                            if target_key and isinstance(words, list):
                                for w in words:
                                    if w and isinstance(w, str):
                                        parsed.append({"cat": target_key, "val": w.strip()})
                                        
                    except json.JSONDecodeError:
                        # --- 2. 备用解析逻辑 (Fallback) ---
                        # 如果 AI 没吐出标准 JSON，尝试强行切分文本
                        clean_res = res.replace("：", ":").replace("\n", "|").replace("，", ",")
                        for block in clean_res.split("|"):
                            if ":" in block:
                                parts = block.split(":", 1)
                                if len(parts) == 2:
                                    cat, words = parts
                                    cat = cat.strip()
                                    target_key = None
                                    for k in WAREHOUSE:
                                        if k.lower() in cat.lower(): 
                                            target_key = k
                                            break
                                    if target_key:
                                        for w in words.split(","):
                                            w = w.strip()
                                            if w: parsed.append({"cat": target_key, "val": w})

                    st.session_state.ai_results = parsed

                except Exception as e:
                    st.error(f"Request Error: {e}")

    # 🔥 核心交互区：恢复勾选确认逻辑 🔥
    if st.session_state.ai_results:
        st.write("")
        st.subheader("Analysis Results (Select to Import)")
        
        # 用于存储用户勾选的结果
        selected_to_import = []
        
        # 使用网格布局展示 Checkboxes
        res_cols = st.columns(3)
        for i, item in enumerate(st.session_state.ai_results):
            with res_cols[i % 3]:
                # 构造显示文本：例如 "StyleSystem · 手绘"
                display_label = f"**{item['cat']}** · {item['val']}"
                # 默认勾选 (value=True)
                if st.checkbox(display_label, key=f"res_{i}", value=True):
                    selected_to_import.append(item)
        
        st.markdown("---")
        
        # 确认入库按钮
        if st.button("Confirm Import to Warehouse", type="primary", use_container_width=True):
            if not selected_to_import:
                st.info("No items selected.")
            else:
                changed_cats = set()
                for item in selected_to_import:
                    cat, val = item["cat"], item["val"]
                    current_list = st.session_state.db_all.get(cat, [])
                    if val not in current_list:
                        current_list.append(val)
                        st.session_state.db_all[cat] = current_list
                        changed_cats.add(cat)
                
                if changed_cats:
                    for c in changed_cats:
                        save_data(WAREHOUSE[c], st.session_state.db_all[c])
                    st.success(f"Successfully imported {len(selected_to_import)} keywords!")
                    st.session_state.ai_results = [] # 入库后清空预览区
                    st.rerun()

# --- 右侧：仓库管理 ---
with col_warehouse:
    st.markdown("## Warehouse")
    c_tools_1, c_tools_2 = st.columns([3, 1])
    with c_tools_1:
        target_cat = st.selectbox("Category", list(WAREHOUSE.keys()), label_visibility="collapsed")
    with c_tools_2:
        current_words = st.session_state.db_all.get(target_cat, [])
        st.markdown(f"<div style='text-align:right; line-height: 42px; color:#666; font-size: 0.9em;'>{len(current_words)} Items</div>", unsafe_allow_html=True)

    with st.container(height=600, border=True):
        if not current_words:
            st.caption("No items in this category.")
        else:
            for i, word in enumerate(current_words):
                row_c1, row_c2 = st.columns([0.85, 0.15])
                with row_c1:
                    # 点击词汇可以直接填入输入框（可选功能）
                    if st.button(word, key=f"word_{target_cat}_{i}", use_container_width=True):
                        st.session_state.input_text += f" {word}"
                with row_c2:
                    if st.button("✕", key=f"del_{target_cat}_{i}_{word}", use_container_width=True):
                        new_list = [w for w in current_words if w != word]
                        st.session_state.db_all[target_cat] = new_list
                        save_data(WAREHOUSE[target_cat], new_list)
                        st.rerun()

    # 底部手动添加
    c_add1, c_add2 = st.columns([3, 1])
    with c_add1:
        new_word_in = st.text_input("Add", placeholder="Add new...", label_visibility="collapsed")
    with c_add2:
        if st.button("Add", use_container_width=True):
            if new_word_in and new_word_in not in current_words:
                current_words.append(new_word_in)
                st.session_state.db_all[target_cat] = current_words
                save_data(WAREHOUSE[target_cat], current_words)
                st.rerun()
