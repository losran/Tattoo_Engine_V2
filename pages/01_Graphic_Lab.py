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
# 1. 初始化
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
# 2. 核心引擎 (严格复刻 9+1 配料逻辑)
# ==========================================
def smart_pick(category):
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if items: return random.choice(items)
    return ""

def assemble_skeleton_fixed(user_input):
    """
    【核心逻辑堡垒 - 绝不阉割版】
    严格遵守：Intent -> Subject -> Style -> Tech -> Color -> Texture -> Comp -> Action -> Mood -> Accent -> Usage
    """
    # 1. 备料 (9个核心配料 + 1个点缀)
    sub     = smart_pick("Subject")
    s_sys   = smart_pick("StyleSystem")
    s_tech  = smart_pick("Technique")
    s_col   = smart_pick("Color")
    s_tex   = smart_pick("Texture")
    s_comp  = smart_pick("Composition")
    act     = smart_pick("Action")
    mood    = smart_pick("Mood")
    usage   = smart_pick("Usage")
    s_acc   = smart_pick("Accent") # 将点缀变为可控项

    # 2. 确定核心主体 (如果用户没输入，则从 Subject 抽)
    final_subject = user_input.strip() if user_input.strip() else sub
    
    # 3. 组装链条 (严格按照 01_creative.py 的 Sequence)
    parts = [
        final_subject,                 
        f"{s_sys} style" if s_sys else "",               
        f"{s_tech} technique" if s_tech else "",              
        f"{s_col} palette" if s_col else "",               
        f"{s_tex} texture" if s_tex else "",               
        f"{s_comp} composition" if s_comp else "",              
        act,                 
        f"{mood} vibe" if mood else "",
        f"with {s_acc} details" if s_acc else "" # 取消 40% 随机，有就加上
    ]

    # 4. 生成初步链条
    raw_chain = "，".join([p for p in parts if p])
    
    # 5. 处理 Usage (严格复刻“纹在...”逻辑)
    if usage:
        raw_chain += f"，纹在{usage}"
        
    return raw_chain

# ===========================
# 3. 界面交互
# ===========================
st.markdown("## 🎨 Graphic Lab")
st.caption("Auto-Assembly -> AI Polish -> Batch Handoff")

c1, c2 = st.columns([3, 1])
with c1:
    user_in = st.text_input("Core Idea / Subject", placeholder="在此输入核心创意或主体...", label_visibility="collapsed")
with c2:
    qty = st.number_input("Batch Size", 1, 8, 4, label_visibility="collapsed")

# ===========================
# 4. 执行逻辑
# ===========================
if st.button("Generate", type="primary", use_container_width=True):
    
    st.session_state.graphic_solutions = [] 
    placeholders = []   
    skeletons = []      
    subject_anchors = [] # 记录主体用于 AI 锁死
    
    # --- 第一阶段：骨架成型 ---
    for i in range(qty):
        idx = i + 1
        ph = st.empty()
        placeholders.append(ph)
        
        sk = assemble_skeleton_fixed(user_in)
        skeletons.append(sk)
        
        # 提取第一个逗号前的词作为 Subject 锚点
        anchor = sk.split('，')[0].strip()
        subject_anchors.append(anchor)
        
        with ph.container(border=True):
            st.markdown(f"**方案{idx}：** {sk}")
            st.caption("✨ 资深策展人正在润色文案...") 
    
    # --- 第二阶段：AI 艺术化润色 (还原调教逻辑) ---
    sys_prompt = "你是一位资深刺青策展人。请将提供的关键词组合润色为极具艺术感的纹身描述。每段必须出现'纹身'二字。"
    
    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        anchor = subject_anchors[i]
        
        user_prompt = f"""
        【原始骨架】：{sk}
        【核心主体】：{anchor}
        
        【指令】：
        1. 必须在描述中“字面保留”核心主体：{anchor}。
        2. 必须严格保留骨架中的风格、颜色、部位描述。
        3. 必须严格以 "**方案{idx}：**" 开头。
        4. 输出一段 60-90 字的完整视觉描述。
        """
        
        full_response = ""
        try:
            ph.empty()
            with ph.container(border=True):
                if client:
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": sys_prompt},{"role": "user", "content": user_prompt}],
                        temperature=0.85, 
                        stream=True 
                    )
                    full_response = st.write_stream(stream)
                    
                    if not full_response.startswith(f"**方案{idx}：**"):
                        full_response = f"**方案{idx}：** {full_response}"
                    
                    # 强校验：如果主体被润色丢了，补回来
                    if anchor not in full_response:
                        full_response = full_response.replace(f"**方案{idx}：**", f"**方案{idx}：** 围绕着【{anchor}】展开的纹身")
                else:
                    full_response = f"**方案{idx}：** {sk} (Offline Mode)"
                    st.write(full_response)
        except Exception as e:
            full_response = f"**方案{idx}：** {sk} (Error: {str(e)})"
            ph.markdown(full_response)

        final_results.append(full_response)

    st.session_state.graphic_solutions = final_results
    st.rerun()

# ===========================
# 5. 结果展示与叠加发送
# ===========================
if "graphic_solutions" in st.session_state and st.session_state.graphic_solutions:
    st.markdown("---")
    st.subheader("📦 Ready for Automation")
    
    for sol in st.session_state.graphic_solutions:
        with st.container(border=True):
            st.markdown(sol)
        
    c_send, c_clear = st.columns([3, 1])
    
    with c_send:
        if st.button("🚀 Send ALL to Automation Pipeline (叠加)", type="primary", use_container_width=True):
            if "global_queue" not in st.session_state:
                st.session_state.global_queue = []
            st.session_state.global_queue.extend(st.session_state.graphic_solutions)
            st.toast(f"✅ 已添加 {len(st.session_state.graphic_solutions)} 组方案")
            time.sleep(0.8)
            st.switch_page("pages/03_🚀_Automation.py")
            
    with c_clear:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.graphic_solutions = []
            st.rerun()
