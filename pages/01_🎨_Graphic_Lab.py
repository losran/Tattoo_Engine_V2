import streamlit as st
import random
from openai import OpenAI
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
# 2. 核心逻辑：精密组装
# ===========================
def smart_pick(category):
    """从仓库的安全抽取函数"""
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if items:
        return random.choice(items)
    return ""

def assemble_complex_logic(user_input):
    """
    精密组装逻辑链条
    Subject -> System -> Tech -> Color -> Texture -> Comp -> Action -> Mood -> (Accent)
    """
    # 1. 确定主体
    subject = user_input if user_input.strip() else smart_pick("Subject")
    
    # 2. 抽取配方
    s_system = smart_pick("StyleSystem")
    s_tech   = smart_pick("Technique")
    s_color  = smart_pick("Color")
    s_tex    = smart_pick("Texture")
    s_comp   = smart_pick("Composition")
    action   = smart_pick("Action")
    mood     = smart_pick("Mood")
    
    # 3. 组装链条
    parts = [subject]
    if s_system: parts.append(f"{s_system} style")
    if s_tech:   parts.append(f"{s_tech} technique")
    if s_color:  parts.append(f"{s_color} palette")
    if s_tex:    parts.append(f"{s_tex} texture")
    if s_comp:   parts.append(f"{s_comp} composition")
    if action:   parts.append(action)
    if mood:     parts.append(f"{mood} vibe")
    
    # 4. 随机点缀 (40% 概率)
    if random.random() > 0.6:
        accent = smart_pick("Accent")
        if accent: parts.append(f"with {accent} details")
        
    return ", ".join(parts)

def run_pipeline(user_input, count):
    results = []
    sys_prompt = "You are a tattoo art director. Refine the keywords into a high-quality Midjourney prompt."
    
    for i in range(count):
        idx = i + 1
        
        # A. 组装骨架 (本地逻辑，永远可用)
        skeleton = assemble_complex_logic(user_input)
        
        # B. AI 润色 (带容错降级)
        user_prompt = f"""
        Raw Keywords: {skeleton}
        Task: Write a descriptive Midjourney prompt (40-60 words).
        Start EXACTLY with "**Option {idx}:**".
        """
        
        try:
            if client:
                resp = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.9
                )
                content = resp.choices[0].message.content.strip()
                # 强制格式修正
                prefix = f"**方案{idx}："  # 保持中文前缀以便 Automation 识别
                if not content.startswith("**"):
                    content = f"{prefix} {content}"
                results.append(content)
            else:
                # 无 Key 降级
                results.append(f"**方案{idx}：** {skeleton} (Offline Mode)")
                
        except Exception as e:
            # 异常降级 (保留骨架)
            err_msg = str(e)
            note = "Connection Error"
            if "401" in err_msg: note = "Invalid API Key"
            elif "402" in err_msg: note = "Insufficient Balance"
            
            results.append(f"**方案{idx}：** {skeleton} ({note} - Raw Data Used)")
            
    return results

# ===========================
# 3. 界面交互 (无表情符号版)
# ===========================
st.title("Graphic Lab")
st.caption("Precision Assembly & AI Polish")

c1, c2 = st.columns([3, 1])
with c1:
    user_in = st.text_input("Core Subject", placeholder="Leave empty for Blind Box mode...")
with c2:
    qty = st.number_input("Batch Size", 1, 8, 4)

if st.button("Generate", type="primary", use_container_width=True):
    with st.spinner("Processing..."):
        res = run_pipeline(user_in, qty)
        st.session_state.final_solutions = res
        st.rerun()

# ===========================
# 4. 结果展示
# ===========================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.markdown("---")
    st.subheader("Generated Options")
    
    for s in st.session_state.final_solutions:
        st.info(s)
        
    c_send, c_clear = st.columns([3, 1])
    
    with c_send:
        if st.button("Send to Automation", type="primary", use_container_width=True):
            st.switch_page("pages/03_🚀_Automation.py")
            
    with c_clear:
        if st.button("Clear Results", use_container_width=True):
            st.session_state.final_solutions = []
            st.rerun()
