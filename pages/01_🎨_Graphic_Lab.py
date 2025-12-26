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
    【核心】复刻原版的高级组装逻辑
    链条：主体 -> 风格体系 -> 技法 -> 颜色 -> 纹理 -> 构图 -> 动作 -> 情绪 -> (点缀)
    """
    # 1. 确定主体 (Subject)
    subject = user_input if user_input.strip() else smart_pick("Subject")
    
    # 2. 抽取配方 (从细分文件里抽)
    s_system = smart_pick("StyleSystem")   # 对应 styles_system.txt
    s_tech   = smart_pick("Technique")     # 对应 styles_technique.txt
    s_color  = smart_pick("Color")         # 对应 styles_color.txt
    s_tex    = smart_pick("Texture")       # 对应 styles_texture.txt
    s_comp   = smart_pick("Composition")   # 对应 styles_composition.txt
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
    
    # 4. 随机点缀 (Accent) - 40% 概率触发
    if random.random() > 0.6:
        accent = smart_pick("Accent")
        if accent: parts.append(f"with {accent} details")
        
    return ", ".join(parts)

def run_pipeline(user_input, count):
    results = []
    # 系统提示词：强调艺术性和 Prompt 格式
    sys_prompt = "You are a tattoo art director. Refine the keywords into a high-quality Midjourney prompt."
    
    for i in range(count):
        idx = i + 1
        # A. 组装骨架
        skeleton = assemble_complex_logic(user_input)
        
        # B. AI 润色
        user_prompt = f"""
        Raw Keywords: {skeleton}
        
        Task: 
        1. Write a descriptive Midjourney prompt (40-60 words).
        2. Keep all specific style/technique keywords.
        3. Start EXACTLY with "**方案{idx}：**".
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
                if not content.startswith(f"**方案{idx}"):
                    content = f"**方案{idx}：** {content}"
                results.append(content)
            else:
                results.append(f"**方案{idx}：** {skeleton} (AI未连接，仅骨架)")
        except Exception as e:
            results.append(f"**方案{idx}：** 生成出错 {e}")
            
    return results

# ===========================
# 3. 界面交互
# ===========================
st.title("🎨 Graphic Lab")
st.caption("Precision Assembly (精密组装) -> AI Polish")

c1, c2 = st.columns([3, 1])
with c1:
    user_in = st.text_input("核心主体 (Core Subject)", placeholder="留空则开启全盲盒模式...")
with c2:
    qty = st.number_input("数量", 1, 8, 4)

if st.button("✨ 启动精密引擎 (Generate)", type="primary", use_container_width=True):
    with st.spinner("正在调用复杂逻辑链条..."):
        res = run_pipeline(user_in, qty)
        st.session_state.final_solutions = res
        st.rerun()

# ===========================
# 4. 结果展示
# ===========================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.markdown("---")
    for s in st.session_state.final_solutions:
        st.info(s)
        
    if st.button("🚀 发送至自动化中心", use_container_width=True):
        st.switch_page("pages/03_🚀_Automation.py")
