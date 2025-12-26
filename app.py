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
render_sidebar()

# 初始化数据
if "db_all" not in st.session_state:
    init_data()

# 初始化 AI
client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(
            api_key=st.secrets["DEEPSEEK_KEY"],
            base_url="https://api.deepseek.com"
        )
    except:
        pass

# Session 初始化
if "ai_results" not in st.session_state: st.session_state.ai_results = []
if "input_text" not in st.session_state: st.session_state.input_text = ""

# ===========================
# 2. 界面布局 (去 Emoji 极简风)
# ===========================
st.title("Tattoo Engine V2")
st.caption("Smart Ingest & Asset Management")
st.divider()

col_ingest, col_warehouse = st.columns([2, 1])

# ===========================
# 3. 左侧：智能入库 (Smart Ingest)
# ===========================
with col_ingest:
    st.subheader("Smart Ingest")
    
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=180,
        placeholder="Paste your messy inspiration or keywords here..."
    )

    # 按钮区
    c1, c2 = st.columns([1, 4])
    with c1:
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    
    # --- AI 分析逻辑 ---
    if analyze_btn:
        if not st.session_state.input_text:
            st.warning("Input is empty")
        elif not client:
            st.error("DeepSeek Key missing")
        else:
            with st.spinner("Processing..."):
                prompt = f"""
                Task: Extract keywords from tattoo description into JSON.
                Categories: {", ".join(WAREHOUSE.keys())}
                
                Rules:
                1. Distinguish StyleSystem (Art genre) vs Technique (Drawing method).
                2. Return JSON ONLY. No markdown.
                
                Format:
                {{
                    "Subject": ["item1"],
                    "StyleSystem": ["style1"],
                    "Technique": ["tech1"],
                    "Mood": ["mood1"]
                }}
                
                Input: {st.session_state.input_text}
                """
                try:
                    res = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    ).choices[0].message.content
                    
                    # 强力清洗 JSON
                    clean_json = res.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    parsed = []
                    for cat, words in data.items():
                        # 模糊匹配 Key
                        target_key = None
                        for k in WAREHOUSE:
                            if k.lower() == cat.lower(): 
                                target_key = k
                                break
                        
                        if target_key and isinstance(words, list):
                            for w in words:
                                parsed.append({"Category": target_key, "Keyword": w})
                                
                    st.session_state.ai_results = parsed
                    
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    # --- 结果确认区 (表格化展示) ---
    if st.session_state.ai_results:
        st.write("")
        st.subheader("Results Preview")
        
        # 转换为 DataFrame 展示，更整齐
        df_preview = pd.DataFrame(st.session_state.ai_results)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        
        if st.button("Confirm Import", type="primary"):
            changed_cats = set()
            count = 0
            for item in st.session_state.ai_results:
                cat, val = item["Category"], item["Keyword"]
                current_list = st.session_state.db_all.get(cat, [])
                if val not in current_list:
                    current_list.append(val)
                    st.session_state.db_all[cat] = current_list
                    changed_cats.add(cat)
                    count += 1
            
            # 保存逻辑
            if changed_cats:
                for c in changed_cats:
                    save_data(WAREHOUSE[c], st.session_state.db_all[c])
                st.success(f"Imported {count} new keywords.")
                st.session_state.ai_results = [] # 清空结果
                st.rerun()
            else:
                st.info("No new unique keywords found.")

# ===========================
# 4. 右侧：仓库管理 (修复删除功能)
# ===========================
with col_warehouse:
    st.subheader("Warehouse")
    
    # 1. 选择分类
    target_cat = st.selectbox("Category", list(WAREHOUSE.keys()))
    
    # 获取当前数据
    current_words = st.session_state.db_all.get(target_cat, [])
    
    # 2. 展示数据 (使用容器 + DataFrame，干净整洁)
    with st.container(border=True):
        if current_words:
            # 简单展示列表
            st.markdown(f"**Total Items:** {len(current_words)}")
            st.dataframe(
                pd.DataFrame(current_words, columns=["Keywords"]), 
                use_container_width=True, 
                hide_index=True,
                height=300
            )
        else:
            st.caption("No data in this category.")

    # 3. 删除功能 (改为多选删除，解决按钮卡死问题)
    with st.expander("Manage / Delete", expanded=False):
        if current_words:
            to_delete = st.multiselect(
                "Select items to delete:", 
                options=current_words,
                placeholder="Choose keywords..."
            )
            
            if to_delete:
                if st.button("Delete Selected", type="secondary", use_container_width=True):
                    # 执行删除
                    new_list = [w for w in current_words if w not in to_delete]
                    st.session_state.db_all[target_cat] = new_list
                    
                    # 保存
                    save_data(WAREHOUSE[target_cat], new_list)
                    st.success("Deleted.")
                    st.rerun()
        else:
            st.caption("Nothing to delete.")
