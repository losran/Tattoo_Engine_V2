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
# 2. 界面布局 (调整比例)
# ===========================
st.title("Tattoo Engine V2")
st.caption("Smart Ingest & Asset Management")
st.divider()

# 🔴 关键修改：左 1 : 右 1.2 (右边更宽敞)
col_ingest, col_warehouse = st.columns([1, 1.2])

# ===========================
# 3. 左侧：智能入库 (更紧凑)
# ===========================
with col_ingest:
    st.subheader("Smart Ingest")
    
    # 🔴 关键修改：高度减小到 120 (更精致)
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=120, 
        placeholder="Input keywords..."
    )

    # 按钮
    if st.button("Analyze", type="primary", use_container_width=True):
        if not st.session_state.input_text:
            st.warning("Input is empty")
        elif not client:
            st.error("DeepSeek Key missing")
        else:
            with st.spinner("Processing..."):
                prompt = f"""
                Task: Extract keywords from tattoo description into JSON.
                Categories: {", ".join(WAREHOUSE.keys())}
                Rules: Return JSON ONLY. No markdown.
                Format: {{"Subject": ["item1"], "StyleSystem": ["style1"]}}
                Input: {st.session_state.input_text}
                """
                try:
                    res = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    ).choices[0].message.content
                    
                    clean_json = res.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    parsed = []
                    for cat, words in data.items():
                        target_key = None
                        for k in WAREHOUSE:
                            if k.lower() == cat.lower(): target_key = k; break
                        if target_key and isinstance(words, list):
                            for w in words: parsed.append({"Category": target_key, "Keyword": w})
                                
                    st.session_state.ai_results = parsed
                except Exception as e:
                    st.error(f"Error: {e}")

    # 结果预览
    if st.session_state.ai_results:
        st.write("")
        st.caption("Preview")
        df_preview = pd.DataFrame(st.session_state.ai_results)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        
        if st.button("Confirm Import", type="secondary", use_container_width=True):
            changed_cats = set()
            for item in st.session_state.ai_results:
                cat, val = item["Category"], item["Keyword"]
                current_list = st.session_state.db_all.get(cat, [])
                if val not in current_list:
                    current_list.append(val)
                    st.session_state.db_all[cat] = current_list
                    changed_cats.add(cat)
            
            if changed_cats:
                for c in changed_cats:
                    save_data(WAREHOUSE[c], st.session_state.db_all[c])
                st.success("Imported.")
                st.session_state.ai_results = []
                st.rerun()

# ===========================
# 4. 右侧：仓库管理 (更宽敞)
# ===========================
with col_warehouse:
    st.subheader("Warehouse")
    
    # 1. 选择分类
    target_cat = st.selectbox("Category", list(WAREHOUSE.keys()))
    current_words = st.session_state.db_all.get(target_cat, [])
    
    # 2. 展示数据 (容器高度增加，显示更多行)
    with st.container(border=True):
        st.caption(f"Total: {len(current_words)}")
        if current_words:
            df_words = pd.DataFrame(current_words, columns=["Keywords"])
            st.dataframe(
                df_words, 
                use_container_width=True, 
                hide_index=True,
                height=400  # 🔴 关键修改：表格高度加高
            )
        else:
            st.caption("No data.")

    # 3. 删除功能 (多选)
    with st.expander("Manage / Delete", expanded=False):
        if current_words:
            to_delete = st.multiselect(
                "Select items to delete:", 
                options=current_words
            )
            if to_delete:
                if st.button("Delete Selected", type="primary", use_container_width=True):
                    new_list = [w for w in current_words if w not in to_delete]
                    st.session_state.db_all[target_cat] = new_list
                    save_data(WAREHOUSE[target_cat], new_list)
                    st.rerun()
