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

# 初始化
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

if "ai_results" not in st.session_state: st.session_state.ai_results = []
if "input_text" not in st.session_state: st.session_state.input_text = ""

# ===========================
# 2. 界面布局 (1 : 1.5)
# ===========================
col_ingest, col_warehouse = st.columns([1, 1.5])

# ===========================
# 3. 左侧：智能入库 (纯净版)
# ===========================
with col_ingest:
    st.subheader("Tattoo Engine V2")
    st.caption("Smart Ingest")
    
    st.write("") 
    
    # 输入框
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=100, 
        placeholder="Input keywords here..."
    )

    # 按钮 (无符号)
    if st.button("Analyze & Extract", type="primary", use_container_width=True):
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

    # 预览与入库 (无符号)
    if st.session_state.ai_results:
        st.write("")
        st.markdown("##### Preview Results")
        
        df_preview = pd.DataFrame(st.session_state.ai_results)
        st.dataframe(df_preview, use_container_width=True, hide_index=True, height=200)
        
        if st.button("Import to Warehouse", type="secondary", use_container_width=True):
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
# 4. 右侧：仓库 (标签云 + 瀑布流)
# ===========================
with col_warehouse:
    # 头部：分类选择
    c_head1, c_head2 = st.columns([2, 1])
    with c_head1:
        target_cat = st.selectbox("Category", list(WAREHOUSE.keys()), label_visibility="collapsed")
    with c_head2:
        current_words = st.session_state.db_all.get(target_cat, [])
        # 纯数字统计
        st.markdown(f"<div style='text-align:right; padding-top:10px; color:#666;'>Count: {len(current_words)}</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("##### Inventory")
    
    # 🔴 瀑布流标签云 (Multiselect)
    # 纯净版：没有任何 Emoji 提示
    updated_list = st.multiselect(
        label="Inventory View",
        options=current_words,
        default=current_words, 
        key=f"tag_cloud_{target_cat}",
        label_visibility="collapsed"
    )
    
    # 监听删除
    if len(updated_list) < len(current_words):
        st.session_state.db_all[target_cat] = updated_list
        save_data(WAREHOUSE[target_cat], updated_list)
        st.rerun()

    # 底部：手动添加 (无符号)
    st.write("")
    with st.expander("Manual Add", expanded=False):
        c_add1, c_add2 = st.columns([3, 1])
        with c_add1:
            new_word = st.text_input("New Keyword", label_visibility="collapsed")
        with c_add2:
            if st.button("Add", use_container_width=True):
                if new_word and new_word not in current_words:
                    current_words.append(new_word)
                    st.session_state.db_all[target_cat] = current_words
                    save_data(WAREHOUSE[target_cat], current_words)
                    st.rerun()
