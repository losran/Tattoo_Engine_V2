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
# 2. 标题区 (手动写标题，防止被CSS隐藏)
# ===========================
st.markdown("## Tattoo Engine V2") 
st.markdown("---")

# ===========================
# 3. 左右分栏 (1:2)
# ===========================
col_ingest, col_warehouse = st.columns([1, 2])

# ===========================
# 4. 左侧：智能入库
# ===========================
with col_ingest:
    st.markdown("#### Smart Ingest")
    
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=100, 
        placeholder="Paste inspiration keywords...",
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

    # 结果预览表格
    if st.session_state.ai_results:
        st.write("")
        st.caption("Preview")
        df_preview = pd.DataFrame(st.session_state.ai_results)
        st.dataframe(df_preview, use_container_width=True, hide_index=True, height=150)
        
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
# 5. 右侧：清单式仓库 (List View)
# ===========================
with col_warehouse:
    # 头部工具栏
    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        st.markdown("#### Warehouse")
    with c2:
        target_cat = st.selectbox("Category", list(WAREHOUSE.keys()), label_visibility="collapsed")
    with c3:
        # 统计数字
        current_words = st.session_state.db_all.get(target_cat, [])
        st.markdown(f"<div style='text-align:right; line-height: 2.5em; color:#666;'>Count: {len(current_words)}</div>", unsafe_allow_html=True)

    # 🔴 核心变化：自适应列表视图 (Scrollable Container)
    # 给容器一个固定高度，形成滚动条，不再无限拉长页面
    with st.container(height=650, border=True):
        if not current_words:
            st.caption("No items in this category.")
        else:
            # 遍历渲染每一行
            # enumerate 拿到索引，防止 key 冲突
            for i, word in enumerate(current_words):
                # 布局：文字占绝大部分(0.85)，删除按钮占一小部分(0.15)
                row_c1, row_c2 = st.columns([0.88, 0.12])
                
                with row_c1:
                    # 使用 text_input 的 disabled 模式来模拟一个漂亮的只读条，或者直接 markdown
                    # 这里用 markdown + CSS 样式模拟数据条
                    st.markdown(f"""
                    <div style="
                        background-color: #111; 
                        padding: 8px 12px; 
                        border-radius: 4px; 
                        border: 1px solid #222; 
                        margin-bottom: 2px;
                        font-size: 14px;">
                        {word}
                    </div>
                    """, unsafe_allow_html=True)
                
                with row_c2:
                    # 删除按钮：纯 X
                    if st.button("✕", key=f"del_{target_cat}_{i}_{word}", use_container_width=True):
                        # 删除逻辑
                        new_list = [w for w in current_words if w != word]
                        st.session_state.db_all[target_cat] = new_list
                        save_data(WAREHOUSE[target_cat], new_list)
                        st.rerun()

    # 底部手动添加
    c_add1, c_add2 = st.columns([4, 1])
    with c_add1:
        new_word_in = st.text_input("Add new item...", label_visibility="collapsed")
    with c_add2:
        if st.button("Add", use_container_width=True):
            if new_word_in and new_word_in not in current_words:
                current_words.append(new_word_in)
                st.session_state.db_all[target_cat] = current_words
                save_data(WAREHOUSE[target_cat], current_words)
                st.rerun()
