import streamlit as st
import json
from engine_manager import render_sidebar, WAREHOUSE, save_data, init_data
from style_manager import apply_pro_style

# ===========================
# 1. 页面初始化
# ===========================
st.set_page_config(layout="wide", page_title="Tattoo Engine V2")
apply_pro_style()  # 加载你的黑色 Pro 皮肤
render_sidebar()   # 加载侧边栏库存统计

# ===========================
# 2. 标题区
# ===========================
st.title("🧠 Tattoo Engine V2")
st.caption("灵感采集 (Ingest) -> 资产沉淀 (Warehouse) -> 创意组装 (Studio)")
st.markdown("---")

# ===========================
# 3. 灵感采集区 (Smart Ingest)
# ===========================
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("💡 快速入库 (Quick Add)")
    # 这里我们做一个简单的添加器，直接往仓库里加词
    
    # 1. 选择要存入的仓库分类
    target_cat = st.selectbox(
        "存入哪里? (Select Category)", 
        ["Subject", "Style", "Text_English", "Text_Spanish", "Mood"]
    )
    
    # 2. 输入内容
    new_val = st.text_input("输入新灵感 (Input new keyword)", placeholder="例如: Cyber Skull, Neon...")
    
    # 3. 提交按钮
    if st.button("➕ 添加到仓库", type="primary"):
        if new_val:
            # 读取当前库存
            init_data() # 确保数据已加载
            current_list = st.session_state.db_all.get(target_cat, [])
            
            # 判重
            if new_val in current_list:
                st.warning(f"'{new_val}' 已经在库里了！")
            else:
                # 添加并保存
                current_list.append(new_val)
                st.session_state.db_all[target_cat] = current_list
                
                # 写入 GitHub
                path = WAREHOUSE.get(target_cat)
                if path:
                    with st.spinner("正在同步到 GitHub..."):
                        success = save_data(path, current_list)
                        if success:
                            st.success(f"已成功存入 [{target_cat}]: {new_val}")
                        else:
                            st.error("保存失败，请检查网络或 Token")
        else:
            st.warning("内容不能为空")

with c2:
    st.info("👋 欢迎回来")
    st.markdown("""
    **工作流指引:**
    1. 在左侧 **Menu** 切换工作室。
    2. **Graphic Lab**: 做图形设计。
    3. **Text Studio**: 做文字排版。
    4. **Automation**: 拿脚本去跑图。
    """)

# ===========================
# 4. 最近新增展示
# ===========================
st.markdown("---")
st.caption("📦 仓库概览")

if "db_all" in st.session_state:
    # 展示几个核心库的标签云
    st.markdown(f"**Subject (图形主体):** \n`{'` `'.join(st.session_state.db_all.get('Subject', [])[:10])}` ...")
    st.markdown(f"**Text (英文词库):** \n`{'` `'.join(st.session_state.db_all.get('Text_English', [])[:10])}` ...")
