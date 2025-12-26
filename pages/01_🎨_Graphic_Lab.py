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
# 2. 核心组件
# ===========================
def smart_pick(category):
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if items: return random.choice(items)
    return ""

def assemble_skeleton(user_input):
    """秒级组装骨架 (CPU 本地运算)"""
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
        
    return ", ".join([p for p in parts if p and " style" not in p[:1]]) # 简单清洗空值

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
# 4. 执行逻辑 (核心修改区)
# ===========================
if st.button("Generate", type="primary", use_container_width=True):
    
    # --- 第一阶段：秒出骨架 (Instant) ---
    st.session_state.final_solutions = [] # 清空旧数据
    placeholders = []   # 用于存放 UI 占位符
    skeletons = []      # 用于存放原始数据
    
    # 1. 瞬间生成所有框框和骨架
    for i in range(qty):
        idx = i + 1
        # 创建一个带有边框的容器
        with st.container(border=True):
            # 创建一个空的占位符，用来变魔术
            ph = st.empty()
            placeholders.append(ph)
            
            # 立即生成骨架
            sk = assemble_skeleton(user_in)
            skeletons.append(sk)
            
            # ⚡️ 立即显示骨架 + 思考状态
            # 这里用灰色字体显示，表示是“生肉”
            ph.markdown(f"""
            **Option {idx}:** `{sk}`  
            \n
            *✨ AI is polishing...*
            """)
    
    # --- 第二阶段：逐个流式润色 (Streaming) ---
    sys_prompt = "You are a tattoo art director. Refine the keywords into a high-quality Midjourney prompt."
    
    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i] # 找到对应的那个框
        
        user_prompt = f"""
        Raw Keywords: {sk}
        Task: Write a descriptive Midjourney prompt (40-60 words).
        Start EXACTLY with "**Option {idx}:**".
        """
        
        full_response = ""
        
        try:
            if client:
                # 🌊 开启流式传输 (Stream=True)
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.9,
                    stream=True  # <--- 关键！
                )
                
                # 🎬 逐字打印效果 (覆盖掉原来的骨架)
                full_response = st.write_stream(stream)
                
                # 如果 AI 没按格式返回，手动补前缀
                if not full_response.startswith("**"):
                    # 因为 write_stream 已经写到屏幕上了，这里修正内存里的数据即可
                    full_response = f"**Option {idx}:** {full_response}"

            else:
                # 无 Key 模式：模拟打字机效果
                dummy_text = f"**Option {idx}:** {sk} (Offline Mode)"
                
                def dummy_stream():
                    for word in dummy_text.split(" "):
                        yield word + " "
                        time.sleep(0.05)
                
                full_response = st.write_stream(dummy_stream)

        except Exception as e:
            # 报错时的回退
            err_msg = str(e)
            note = "Connection Error"
            if "401" in err_msg: note = "Invalid API Key"
            
            final_text = f"**Option {idx}:** {sk} \n\n*({note} - Raw Data)*"
            ph.info(final_text) # 用静态显示替换流式
            full_response = final_text

        # 存入列表，为了后面发给 Automation
        final_results.append(full_response)

    # 存入 Session，防止刷新丢失
    st.session_state.final_solutions = final_results
    st.rerun() # 重新运行一次以显示底部的按钮 (Streamlit 机制限制)

# ===========================
# 5. 结果处理区 (从 Session 读取)
# ===========================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    # 如果不是刚点击生成（即页面刷新后），需要重新把结果画出来
    # 因为刚才的 write_stream 是暂时的
    
    # 只有当按钮没被按下的时候才重绘，避免重复
    # 这里我们简单一点：每次 Rerun 后直接显示静态结果
    st.markdown("---")
    st.subheader("Final Output")
    
    for sol in st.session_state.final_solutions:
        st.info(sol)
        
    c_send, c_clear = st.columns([3, 1])
    
    with c_send:
        if st.button("Send to Automation", type="primary", use_container_width=True):
            st.switch_page("pages/03_🚀_Automation.py")
            
    with c_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.final_solutions = []
            st.rerun()
