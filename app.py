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

if "db_all" not in st.session_state:
    init_data()

client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(
            api_key=st.secrets["DEEPSEEK_KEY"],
            base_url="https://api.deepseek.com"
        )
    except:
        pass

if "ai_results" not in st.session_state: st.session_state.ai_results = []
if "input_text" not in st.session_state: st.session_state.input_text = ""

# ===========================
# 2. 标题区
# ===========================
st.markdown("## Tattoo Engine V2") 
st.markdown("---")

# ===========================
# 3. 左右分栏 (2:1) -> 左大右小
# ===========================
col_ingest, col_warehouse = st.columns([2, 1])

# ===========================
# 4. 左侧：智能入库 (大头)
# ===========================
with col_ingest:
    st.markdown("#### Smart Ingest")
    st.caption("AI Parser")
    
    # 输入框高度增加到 200，利用左侧空间
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=200, 
        placeholder="Paste text here...",
        label_visibility="collapsed"
    )

    if st.button("Analyze & Extract", use_container_width=True):
        if not st.session_state.input_text:
            st.warning("Input is empty")
        elif not client:
            st.error("DeepSeek Key missing")
        else:
            with st.spinner("Processing..."):
                prompt = f"""
                Task: Extract keywords to JSON.
                Categories: {", ".join(WAREHOUSE.keys())}
                Format: {{"Subject": ["item"], "StyleSystem": ["style"]}}
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

    if st.session_state.ai_results:
        st.write("")
        st.caption("Preview")
        df_preview = pd.DataFrame(st.session_state.ai_results)
        st.dataframe(df_preview, use_container_width=True, hide_index=True, height=200)
        
        if st.button("Import to Warehouse", use_container_width=True):
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
                st.success("Done.")
                st.session_state.ai_results = []
                st.rerun()

# ===========================
# 5. 右侧：紧凑型清单 (小头)
# ===========================
with col_warehouse:
    # 头部工具栏
    c1, c2, c3 = st.columns([2, 2, 1.5])
    with c1:
        st.markdown("#### Warehouse")
    with c2:
        target_cat = st.selectbox("Category", list(WAREHOUSE.keys()), label_visibility="collapsed")
    with c3:
        current_words = st.session_state.db_all.get(target_cat, [])
        st.markdown(f"<div style='text-align:right; padding-top: 5px; color:#666; font-size: 0.9em;'>{len(current_words)} Items</div>", unsafe_allow_html=True)

    # 列表容器 (高度700，在右侧形成一个长条)
    with st.container(height=700, border=True):
        if not current_words:
            st.caption("No items.")
        else:
            for i, word in enumerate(current_words):
                # 布局调整：给删除按钮留小一点的位置 (0.15)
                row_c1, row_c2 = st.columns([0.85, 0.15])
                
                with row_c1:
                    st.markdown(f"""
                    <div style="
                        background-color: #0e0e0e; 
                        padding: 5px 10px; 
                        border-radius: 4px; 
                        border: 1px solid #222; 
                        margin-bottom: 2px;
                        font-size: 13px;
                        white-space: nowrap; 
                        overflow: hidden; 
                        text-overflow: ellipsis;
                        color: #d0d0d0;">
                        {word}
                    </div>
                    """, unsafe_allow_html=True)
                
                with row_c2:
                    if st.button("✕", key=f"del_{target_cat}_{i}_{word}", use_container_width=True):
                        new_list = [w for w in current_words if w != word]
                        st.session_state.db_all[target_cat] = new_list
                        save_data(WAREHOUSE[target_cat], new_list)
                        st.rerun()

    # 底部快速添加
    # 修复点：这里是报错的地方，确保这一行完整
    c_add1, c_add2 = st.columns([3, 1])
    
    with c_add1:
        new_word_in = st.text_input("Add new item...", label_visibility="collapsed")
    with c_add2:
        if st.button("Add", use_container_width=True):
            if new_word_in and new_word_in not in current_words:
                current_words.append(new_word_in)
                st.session_state.db_all[target_cat] = current_words
                save_data(WAREHOUSE[target_cat], current_words)
                st.rerun()
