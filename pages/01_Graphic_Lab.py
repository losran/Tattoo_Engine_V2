import streamlit as st
import sys
import os
import random
import time
from openai import OpenAI

# ===========================
# 0. 路径修复 (确保能找到根目录模块)
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

# ===========================
# 2. 核心引擎 (零件组装)
# ===========================
def smart_pick(category):
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if items: return random.choice(items)
    return ""

def assemble_skeleton(user_input):
    """秒级组装骨架 - 100% 还原你的零件逻辑"""
    subject = user_input if user_input.strip() else smart_pick("Subject")
    
    parts = [
        subject,
        f"{smart_pick('StyleSystem')} style",
        f"{smart_pick('Technique')} technique",
        f"{smart_pick('Color')} palette",
        f"{smart_pick('Texture')} texture",
        f"{smart_pick('Composition')} composition",
        smart_pick('Action'),
        f"{smart_pick('Mood')} vibe"
    ]
    
    # 混沌点缀
    if random.random() > 0.6:
        parts.append(f"with {smart_pick('Accent')} details")
        
    return ", ".join([p for p in parts if p and " style" not in p[:1]])

# ===========================
# 3. 界面交互
# ===========================
st.markdown("## 🎨 Graphic Lab")
st.caption("Auto-Assembly -> AI Polish -> Batch Handoff")

c1, c2 = st.columns([3, 1])
with c1:
    user_in = st.text_input("Core Subject", placeholder="Leave empty for Blind Box mode...", label_visibility="collapsed")
with c2:
    qty = st.number_input("Batch Size", 1, 8, 4, label_visibility="collapsed")

# ===========================
# 4. 执行逻辑 (AI 润色堡垒)
# ===========================
if st.button("Generate", type="primary", use_container_width=True):
    
    st.session_state.graphic_solutions = [] 
    placeholders = []   
    skeletons = []      
    
    # --- 第一阶段：秒出骨架 ---
    for i in range(qty):
        idx = i + 1
        ph = st.empty()
        placeholders.append(ph)
        
        sk = assemble_skeleton(user_in)
        skeletons.append(sk)
        
        with ph.container(border=True):
            st.markdown(f"**方案{idx}：** {sk}")
            st.caption("✨ 资深策展人正在润色文案...") 
    
    # --- 第二阶段：流式润色 (还原调教逻辑) ---
    # 🔴 核心修改：还原你的 sys_prompt
    sys_prompt = "你是一位资深刺青策展人。请将提供的关键词组合润色为极具艺术感的纹身描述。每段必须出现'纹身'二字。"
    
    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        
        # 🔴 核心修改：还原你的 user_prompt (含锚点与字数要求)
        user_prompt = f"""
        【原始骨架】：{sk}
        
        【指令】：
        1. 必须严格保留骨架中的风格、颜色、部位等关键信息。
        2. 必须严格以 "**方案{idx}：**" 开头 (双星号+全角冒号)。这是自动化识别的锚点。
        3. 输出一段 50-80 字的完整视觉描述。
        """
        
        full_response = ""
        
        try:
            ph.empty()
            with ph.container(border=True):
                if client:
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.85, # 还原高采样率
                        stream=True 
                    )
                    full_response = st.write_stream(stream)
                    # 强校验锚点
                    if not full_response.startswith("**方案"):
                        full_response = f"**方案{idx}：** {full_response}"
                else:
                    # 离线模拟
                    dummy = f"**方案{idx}：** {sk} (AI Offline)"
                    def dummy_stream():
                        for w in dummy.split(" "):
                            yield w + " "
                            time.sleep(0.05)
                    full_response = st.write_stream(dummy_stream)

        except Exception as e:
            ph.empty()
            with ph.container(border=True):
                st.markdown(f"**方案{idx}：** {sk}")
                st.markdown(f":red[⚠️ 润色失败 - {str(e)}]")
                full_response = f"**方案{idx}：** {sk}"

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
            
            # 叠加发送逻辑
            st.session_state.global_queue.extend(st.session_state.graphic_solutions)
            
            st.toast(f"✅ 已添加 {len(st.session_state.graphic_solutions)} 组方案至自动化队列")
            time.sleep(0.8)
            # 注意：请确保你的自动化文件名与此处一致
            st.switch_page("pages/03_🚀_Automation.py")
            
    with c_clear:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.graphic_solutions = []
            st.rerun()
