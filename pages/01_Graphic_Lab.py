import streamlit as st
import sys
import os
import random
import time
from openai import OpenAI

# ===========================
# 0. 环境路径修复
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置与初始化
# ===========================
st.set_page_config(layout="wide", page_title="Graphic Lab")
apply_pro_style()
render_sidebar()
init_data()

client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(api_key=st.secrets["DEEPSEEK_KEY"], base_url="https://api.deepseek.com")
    except:
        pass

# ==========================================
# 2. 核心引擎 (权重升级版)
# ==========================================
def smart_pick(category, count=1):
    """从数据库抽取指定数量的元素"""
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if not items: return []
    # 允许抽取的数量不超过库存
    actual_count = min(count, len(items))
    return random.sample(items, actual_count)

def assemble_weighted_skeleton(user_input):
    """
    【融合版组装引擎：高权重 + 混沌灵性】
    修复重复感问题，恢复随机惊喜
    """
    # 1. 主体逻辑：尊重用户输入 (关键修改)
    # 如果用户有输入，不再强制拼接数据库元素，除非用户输入很少
    if user_input.strip():
        subjects = [user_input.strip()]
        # 只有 30% 的概率在用户输入的基础上再额外加一个数据库元素（制造惊喜，而不是制造干扰）
        if random.random() > 0.6: 
            extra_sub = smart_pick("Subject", 1)
            if extra_sub: subjects.extend(extra_sub)
    else:
        # 盲盒模式：随机 1-2 个主体
        sub_count = random.randint(1, 2)
        subjects = smart_pick("Subject", sub_count)

    # 2. 动态配料 (恢复随机性，而不是硬塞)
    # 动作：随机 0-1 个（不再强制 2 个，留白给 AI）
    action_list = smart_pick("Action", random.randint(3, 4)) 
    action = action_list[0] if action_list else ""

    # 情绪：随机 1 个
    mood_list = smart_pick("Mood", 5)
    mood = mood_list[0] if mood_list else ""
    
    # 3. 基础配料 (引入旧版的混沌机制)
    s_sys   = smart_pick("StyleSystem", 1)
    s_tech  = smart_pick("Technique", 1)
    s_col   = smart_pick("Color", 2) # 颜色改回 1 个，避免太乱
    
    # 4. 混沌参数 (40% 概率触发额外点缀，重现旧版灵魂)
    s_acc = ""
    if random.random() > 0.4: # <--- 这里就是你要的“混沌参数”
        acc_list = smart_pick("Accent", 1)
        if acc_list: s_acc = acc_list[0]

    # 5. 组装部分 (使用更柔和的提示词引导)
    parts = []
    
    # 只有存在时才添加，避免空标签
    if action: parts.append(f"动态：{action}")
    if mood: parts.append(f"氛围：{mood}")
    
    parts.append(f"主体：{' + '.join(subjects)}")
    
    if s_sys: parts.append(f"风格：{s_sys[0]}")
    if s_tech: parts.append(f"技法：{s_tech[0]}")
    if s_col: parts.append(f"色调：{s_col[0]}")
    if s_acc: parts.append(f"点缀元素：{s_acc}") # 只有触发了混沌才有

    # 用竖线分割，保留结构感
    raw_chain = " | ".join(parts)
        
    return raw_chain, subjects

# ===========================
# 3. 界面交互
# ===========================
st.markdown("## Graphic Lab")
st.caption("High Weight Action & Mood -> Multi-Subject -> 200 Words Polish")

c1, c2 = st.columns([3, 1])
with c1:
    user_idea = st.text_input("Core Idea", placeholder="输入关键词或留空盲盒...", label_visibility="collapsed")
with c2:
    qty = st.number_input("Batch", 1, 8, 4, label_visibility="collapsed")

# ===========================
# 4. 执行生成 (AI 深度润色)
# ===========================
if st.button("一键生成高权重方案", type="primary", use_container_width=True):
    
    st.session_state.graphic_solutions = [] 
    placeholders = []   
    skeletons = []      
    
    # --- 第一阶段：拼盘 (牛肉火锅逻辑) ---
    for i in range(qty):
        ph = st.empty()
        placeholders.append(ph)
        
        # 1. 先抓随机配菜 (不管有没有输入，先备好料)
        # 注意：这里直接从 db_all 取，不再调用复杂的 assemble 函数
        r_style = random.choice(st.session_state.db_all.get("StyleSystem", ["插画风格"]))
        r_subject = random.choice(st.session_state.db_all.get("Subject", ["几何"]))
        r_tech = random.choice(st.session_state.db_all.get("Technique", ["线条"]))
        r_color = random.choice(st.session_state.db_all.get("Color", ["黑白"]))
        
        # 2. 组合 (你的词在最前面，权重最高)
        if user_idea and user_idea.strip():
            # 逻辑：[你的输入] + [随机风格] + [随机主体] + [随机技法] + [随机颜色]
            sk = f"{user_idea.strip()}, {r_style}, {r_subject}, {r_tech}, {r_color}"
        else:
            # 逻辑：[随机风格] + [随机主体] + [随机技法] + [随机颜色]
            sk = f"{r_style}, {r_subject}, {r_tech}, {r_color}"
            
        skeletons.append(sk)
        
        with ph.container(border=True):
            st.markdown(f"**方案{i+1} (骨架)：** `{sk}`")
            st.caption("⏳ 正在进行深度叙事润色...") 
    
    # --- 第二阶段：AI 深度润色指令 ---
    sys_prompt = """你是一位顶级的纹身艺术策展人。
    任务：将给定的【关键词骨架】转化为极具冲击力的纹身设计方案。
    规则：
    1. 必须保留骨架中所有的关键词信息，特别是排在第一位的用户核心词。
    2. 描述必须包含'微型纹身'二字。
    3. 语言风格：高级、艺术感、富有画面张力。
    """

    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        
        user_prompt = f"""
        【原始关键词骨架】：{sk}
        
        【定制指令】：
        1. 严格以 "**方案{idx}：**" 开头。
        2. 将字数扩展至 80-120 字。
        3. 这是一个组合任务：请将骨架里的关键词（{sk}）有机融合，不要遗漏用户输入的词。
        """
        
        try:
            ph.empty()
            with ph.container(border=True):
                if client:
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": sys_prompt},{"role": "user", "content": user_prompt}],
                        temperature=0.9, 
                        stream=True 
                    )
                    full_response = st.write_stream(stream)
                else:
                    full_response = f"**方案{idx}：** {sk} (AI Offline)"
                    st.write(full_response)
        except Exception as e:
            full_response = f"**方案{idx}：** {sk} (Error: {str(e)})"
            ph.markdown(full_response)

        final_results.append(full_response)

    st.session_state.graphic_solutions = final_results
    # 这里不需要 st.rerun()，否则字还没打完就刷新了
# ===========================
# 5. 结果展示
# ===========================
if "graphic_solutions" in st.session_state and st.session_state.graphic_solutions:
    st.markdown("---")
    st.subheader("Ready for Automation")
    
    for sol in st.session_state.graphic_solutions:
        with st.container(border=True):
            st.markdown(sol)
        
    c_send, c_clear = st.columns([3, 1])
    with c_send:
        if st.button("发送至自动化流水线", type="primary", use_container_width=True):
            if "global_queue" not in st.session_state:
                st.session_state.global_queue = []
            st.session_state.global_queue.extend(st.session_state.graphic_solutions)
            st.toast(f"已添加 {len(st.session_state.graphic_solutions)} 组高权重方案")
            time.sleep(0.8)
            st.switch_page("pages/03_Automation.py")
            
    with c_clear:
        if st.button("清空结果", use_container_width=True):
            st.session_state.graphic_solutions = []
            st.rerun()
