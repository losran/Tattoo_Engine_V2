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

def render_dark_card(content):
    """渲染深灰色卡片 (替代 st.info)"""
    # 使用 Streamlit 的背景色微调，做出卡片感
    st.markdown(f"""
    <div style="
        background-color: #000000; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #3d3d3d; 
        margin-bottom: 10px;
        color: #e0e0e0;
        font-family: sans-serif;
    ">
        {content}
    </div>
    """, unsafe_allow_html=True)

# ===========================
# 3. 界面交互
# ===========================
st.title("Graphic Lab")
st.caption("Instant Skeleton -> Real-time AI Polish")

c1, c2 = st.columns([3, 1])
with c1:
    user_in = st.text_input("Core Subject", placeholder="Leave empty for Blind Box mode...")
with c2:
    qty = st.number_input("Batch Size", 1, 8, 4)

# ===========================
# 4. 执行逻辑
# ===========================
if st.button("Generate", type="primary", use_container_width=True):
    
    st.session_state.final_solutions = [] 
    placeholders = []   
    skeletons = []      
    
    # --- 第一阶段：秒出骨架 ---
    for i in range(qty):
        idx = i + 1
        # 使用 st.empty 占位
        ph = st.empty()
        placeholders.append(ph)
        
        sk = assemble_skeleton(user_in)
        skeletons.append(sk)
        
        # 初始状态：显示骨架 (用 Markdown 模拟深色块)
        with ph.container():
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 15px; border-radius: 8px; border: 1px dashed #444; color: #888;">
                <strong>Option {idx}:</strong> {sk} <br><br>
                <span style="color: #4caf50;">✨ AI is thinking...</span>
            </div>
            """, unsafe_allow_html=True)
    
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
            # 清空占位符，准备开始流式输出
            ph.empty()
            
            # 创建一个深色容器来承载流式文字
            # 注意：st.write_stream 很难直接嵌在 HTML div 里，
            # 所以这里我们用 st.container(border=True) 自带的深灰背景
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
                    # 无 Key 模拟
                    dummy = f"**Option {idx}:** {sk} (Offline Mode)"
                    def dummy_stream():
                        for w in dummy.split(" "):
                            yield w + " "
                            time.sleep(0.05)
                    full_response = st.write_stream(dummy_stream)

        except Exception as e:
            # 报错时的显示 (使用深灰卡片)
            ph.empty()
            with ph.container():
                err_msg = str(e)
                note = "Connection Error"
                if "401" in err_msg: note = "Invalid API Key (Check Secrets)"
                
                final_text = f"**Option {idx}:** {sk} <br><br> <span style='color:#ff6b6b; font-size:0.9em;'>⚠️ {note} - Using Raw Data</span>"
                
                render_dark_card(final_text) # 调用深灰卡片函数
                
                # 存纯文本给自动化用
                full_response = f"**Option {idx}:** {sk} ({note})"

        final_results.append(full_response)

    st.session_state.final_solutions = final_results
    st.rerun()

# ===========================
# 5. 结果展示 (静态)
# ===========================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.markdown("---")
    st.subheader("Final Output")
    
    for sol in st.session_state.final_solutions:
        # 这里把 st.info 换成了自定义的深灰卡片
        render_dark_card(sol)
        
    c_send, c_clear = st.columns([3, 1])
    
    with c_send:
        if st.button("Send to Automation", type="primary", use_container_width=True):
            st.switch_page("pages/03_🚀_Automation.py")
            
    with c_clear:
        if st.button("Clear Results", use_container_width=True):
            st.session_state.final_solutions = []
            st.rerun()
