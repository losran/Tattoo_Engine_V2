import streamlit as st
import random
import time
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
# 2. 辅助函数
# ===========================
def smart_pick(category):
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if items: return random.choice(items)
    return ""

def assemble_skeleton(user_input):
    """秒级组装骨架"""
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
    
    if random.random() > 0.6:
        parts.append(f"with {smart_pick('Accent')} details")
        
    return ", ".join([p for p in parts if p and " style" not in p[:1]])

# ===========================
# 3. 界面交互
# ===========================
st.title("Graphic Lab")

c1, c2 = st.columns([3, 1])
with c1:
    user_in = st.text_input("Core Subject", placeholder="Leave empty for Blind Box mode...")
with c2:
    qty = st.number_input("Batch Size", 1, 8, 4)

# ===========================
# 4. 执行逻辑
# ===========================
if st.button("Generate", type="primary", use_container_width=True):
    
    st.session_state.graphic_solutions = [] # 改名：graphic专用，互不干扰
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
            st.markdown(f"**Option {idx}:** {sk}")
            st.caption("✨ AI is thinking...") 
    
    # --- 第二阶段：流式润色 ---
    sys_prompt = "You are a tattoo art director. Refine the keywords into a high-quality Midjourney prompt."
    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        
        user_prompt = f"""
        Raw Keywords: {sk}
        Task: Write a descriptive Midjourney prompt (40-60 words).
        Start EXACTLY with "**Option {idx}:**".
        """
        
        full_response = ""
        
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
                    if not full_response.startswith("**"):
                        full_response = f"**Option {idx}:** {full_response}"
                else:
                    dummy = f"**Option {idx}:** {sk} (Offline Mode)"
                    def dummy_stream():
                        for w in dummy.split(" "):
                            yield w + " "
                            time.sleep(0.05)
                    full_response = st.write_stream(dummy_stream)

        except Exception as e:
            ph.empty()
            with ph.container(border=True):
                err_msg = str(e)
                note = "Connection Error"
                if "401" in err_msg: note = "Invalid API Key"
                st.markdown(f"**Option {idx}:** {sk}")
                st.markdown(f":red[⚠️ {note} - Using Raw Data]")
                full_response = f"**Option {idx}:** {sk} ({note})"

        final_results.append(full_response)

    st.session_state.graphic_solutions = final_results
    st.rerun()

# ===========================
# 5. 结果展示与叠加发送
# ===========================
if "graphic_solutions" in st.session_state and st.session_state.graphic_solutions:
    st.markdown("---")
    st.subheader("Final Output")
    
    for sol in st.session_state.graphic_solutions:
        with st.container(border=True):
            st.markdown(sol)
        
    c_send, c_clear = st.columns([3, 1])
    
    with c_send:
        # 🟢 核心修改：叠加逻辑 🟢
        if st.button("Add to Automation Queue (叠加发送)", type="primary", use_container_width=True):
            # 1. 初始化全局购物车
            if "global_queue" not in st.session_state:
                st.session_state.global_queue = []
            
            # 2. 将当前生成的方案“追加”进去，而不是覆盖
            st.session_state.global_queue.extend(st.session_state.graphic_solutions)
            
            # 3. 跳转
            st.toast(f"已添加 {len(st.session_state.graphic_solutions)} 个方案到队列！")
            time.sleep(0.5)
            st.switch_page("pages/03_🚀_Automation.py")
            
    with c_clear:
        if st.button("Clear Results", use_container_width=True):
            st.session_state.graphic_solutions = []
            st.rerun()
