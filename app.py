import streamlit as st
import json
from openai import OpenAI
from engine_manager import render_sidebar, init_data, WAREHOUSE
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置
# ===========================
st.set_page_config(layout="wide", page_title="Tattoo Engine V2", page_icon="🧠")
apply_pro_style()
render_sidebar()
init_data()

# 初始化 DeepSeek
client = None
try:
    client = OpenAI(api_key=st.secrets["DEEPSEEK_KEY"], base_url="https://api.deepseek.com")
except:
    pass

# 状态初始化
if "ai_results" not in st.session_state: st.session_state.ai_results = []
if "input_text" not in st.session_state: st.session_state.input_text = ""

# ===========================
# 2. 界面布局
# ===========================
st.title("🧠 Tattoo Engine V2")
st.caption("Smart Ingest (智能采集) → Warehouse (资产沉淀)")
st.divider()

col_ingest, col_warehouse = st.columns([4, 2])

# --- 左侧：智能采集 (Smart Ingest) ---
with col_ingest:
    st.subheader("💡 灵感入库 (Smart Ingest)")
    st.session_state.input_text = st.text_area(
        "灵感输入",
        st.session_state.input_text,
        height=200,
        placeholder="在此输入任何混乱的灵感...\n例如：想做一个赛博朋克风格的艺伎，带一点故障艺术的纹理，构图要对称，黑红配色..."
    )

    if st.button("⚡ 深度拆解 (Analyze)", use_container_width=True):
        if not client:
            st.error("DeepSeek Key 未配置")
        elif not st.session_state.input_text:
            st.warning("请输入内容")
        else:
            with st.spinner("正在进行结构化拆解..."):
                # 能够识别所有细分维度的 Prompt
                keys_str = ", ".join(WAREHOUSE.keys())
                prompt = f"""
                任务：将纹身描述拆解为结构化数据。
                目标库分类：{keys_str}
                
                【规则】
                1. StyleSystem (风格流派) 和 Technique (技法) 要区分开。
                2. Accent (点缀) 是指具体的装饰元素（如：光晕、火花）。
                3. Composition (构图) 指形态（如：对称、黄金螺旋）。
                
                【输出JSON】
                {{
                    "Subject": ["词1"],
                    "StyleSystem": ["词1"],
                    "Technique": ["词1"],
                    "Mood": ["词1"],
                    ...
                }}
                输入：{st.session_state.input_text}
                """
                
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    raw_json = resp.choices[0].message.content.replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw_json)
                    
                    parsed = []
                    for cat, items in data.items():
                        # 模糊匹配逻辑
                        target_key = None
                        for warehouse_key in WAREHOUSE.keys():
                            if warehouse_key.lower() == cat.lower():
                                target_key = warehouse_key
                                break
                        
                        if target_key and isinstance(items, list):
                            for item in items:
                                parsed.append({"cat": target_key, "val": item})
                                
                    st.session_state.ai_results = parsed
                except Exception as e:
                    st.error(f"解析失败: {e}")

    # 结果确认区
    if st.session_state.ai_results:
        st.success(f"识别出 {len(st.session_state.ai_results)} 个有效资产")
        
        # 预览卡片
        selected_items = []
        c1, c2, c3 = st.columns(3)
        for i, item in enumerate(st.session_state.ai_results):
            with [c1, c2, c3][i % 3]:
                if st.checkbox(f"**{item['cat']}**: {item['val']}", value=True, key=f"check_{i}"):
                    selected_items.append(item)
        
        st.markdown("---")
        if st.button("📥 确认存入仓库", type="primary"):
            # 写入 Session (实际项目会写入 GitHub)
            count = 0
            for item in selected_items:
                cat, val = item['cat'], item['val']
                if cat in st.session_state.db_all:
                    if val not in st.session_state.db_all[cat]:
                        st.session_state.db_all[cat].append(val)
                        count += 1
            st.success(f"成功入库 {count} 个新词条！")
            st.rerun()

# --- 右侧：仓库概览 ---
with col_warehouse:
    st.subheader("📦 资产管理")
    view_cat = st.selectbox("查看分类", list(WAREHOUSE.keys()))
    
    items = st.session_state.db_all.get(view_cat, [])
    st.caption(f"当前库存: {len(items)}")
    
    with st.container(height=400):
        for item in items:
            st.text(f"• {item}")
