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
    【高权重组装引擎】
    逻辑：Intent -> 多重Subject -> 核心Action -> 核心Mood -> 其他配料
    """
    # 1. 抽取多重主体 (2-3个)
    sub_count = random.randint(1, 2)
    subjects = smart_pick("Subject", sub_count)
    if user_input.strip():
        subjects = [user_input.strip()] + subjects[:sub_count-1]
    
    # 2. 强化配料
    action = " ".join(smart_pick("Action", 2))
    mood = " ".join(smart_pick("Mood", 2))
    
    # 3. 基础配料
    s_sys   = " ".join(smart_pick("StyleSystem", 1))
    s_tech  = " ".join(smart_pick("Technique", 1))
    s_col   = " ".join(smart_pick("Color", 2))
    s_tex   = " ".join(smart_pick("Texture", 1))
    s_comp  = " ".join(smart_pick("Composition", 1))
    usage   = " ".join(smart_pick("Usage", 1))
    s_acc   = " ".join(smart_pick("Accent", 1))

    # 4. 组装逻辑：将动作和情绪前置，增加视觉冲突
    parts = [
        f"【核心动作：{action}】",
        f"【氛围基调：{mood}】",
        f"主体元素：{' & '.join(subjects)}",
        f"风格：{s_sys}",
        f"技法：{s_tech}",
        f"色调：{s_col}",
        f"质感：{s_tex}",
        f"构图：{s_comp}",
        f"细节：{s_acc}"
    ]

    raw_chain = " | ".join([p for p in parts if "：" in p and p.split("：")[1].strip()])
    
    if usage:
        raw_chain += f" | 纹刺部位：{usage}"
        
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
    subject_anchors = [] 
    
    # --- 第一阶段：骨架生成 ---
    for i in range(qty):
        ph = st.empty()
        placeholders.append(ph)
        sk, subs = assemble_weighted_skeleton(user_idea)
        skeletons.append(sk)
        subject_anchors.append(subs)
        
        with ph.container(border=True):
            st.markdown(f"**方案{i+1}：** {sk}")
            st.caption("正在进行深度叙事润色...") 
    
    # --- 第二阶段：AI 深度润色指令 ---
    sys_prompt = """你是一位顶级的纹身艺术策展人与视觉叙事大师。
    你的任务是将干燥的关键词转化为极具冲击力、充满灵魂的纹身设计方案。
    每段描述必须包含'纹身'二字，字数控制在 100-200 字之间。
    
    润色重点：
    1. 极力放大【核心动作】的动态张力。
    2. 深度渲染【氛围基调】的情绪感染力。
    3. 将多个主体有机融合，构建一个有故事感的视觉画面。
    4. 词汇要高级且富有绘画感（如：破碎感、流动性、神圣感、狂乱的线条）。"""

    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        anchors = "、".join(subject_anchors[i])
        
        user_prompt = f"""
        【原始骨架信息】：{sk}
        【必须保留的主体】：{anchors}
        
        【定制指令】：
        1. 严格以 "**方案{idx}：**" 开头。
        2. 将字数扩展至 100-200 字，增加对动作和情绪的文学化描写。
        3. 确保视觉描述能够指导 Midjourney 生成高品质图像。
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
    st.rerun()

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
