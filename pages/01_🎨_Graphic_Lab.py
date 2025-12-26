
import streamlit as st
import random
from openai import OpenAI
from engine_manager import init_data, render_sidebar
from style_manager import apply_pro_style

# ==========================================
# 1. 页面配置与初始化
# ==========================================
st.set_page_config(layout="wide", page_title="Graphic Lab")
apply_pro_style()
render_sidebar()
init_data()

# 初始化 AI 客户端
try:
    client = OpenAI(
        api_key=st.secrets["DEEPSEEK_KEY"], 
        base_url="https://api.deepseek.com"
    )
except Exception:
    st.error("DeepSeek Key 配置缺失，请检查 secrets.toml")

# ==========================================
# 2. 核心逻辑函数
# ==========================================

def smart_pick(category):
    """从指定仓库分类中随机抽取一个词"""
    # 这里的 db_all 来自 engine_manager 的 fetch_repo_data
    db = st.session_state.get("db_all", {})
    items = db.get(category, [])
    if items:
        return random.choice(items)
    return ""

def assemble_graphic_skeleton(user_intent):
    """
    组装图形纹身的基础骨架
    顺序: Intent -> Subject -> Style -> Action -> Mood -> Usage
    """
    # 1. 备料 (如果用户没填意图，就自动抽取 Subject)
    if not user_intent:
        core_subject = smart_pick("Subject")
    else:
        core_subject = user_intent

    style = smart_pick("Style")
    action = smart_pick("Action")
    mood = smart_pick("Mood")
    usage = smart_pick("Usage")
    
    # 2. 拼接
    # 逻辑: [主体] in [风格] style, [动作], [情绪] vibe, placed on [部位]
    parts = []
    if core_subject: parts.append(core_subject)
    if style: parts.append(f"{style} style")
    if action: parts.append(action)
    if mood: parts.append(f"{mood} vibe")
    if usage: parts.append(f"placement: {usage}")
    
    return ", ".join(parts)

def run_ai_polish(skeleton, count):
    """调用 DeepSeek 进行艺术润色"""
    results = []
    
    # 系统提示词：设定为资深纹身策展人
    sys_prompt = "你是一位资深刺青策展人。请将提供的关键词骨架润色为极具艺术感的英文 Prompt (提示词)。"
    
    for i in range(count):
        idx = i + 1
        user_prompt = f"""
        【原始骨架】: {skeleton}
        
        【指令】:
        1. 输出一段 40-60 个单词的英文 Prompt。
        2. 必须保留骨架中的核心风格和主体。
        3. 格式严格要求: 以 "**方案{idx}：**" 开头 (双星号+中文冒号)。
        4. 不要包含任何解释性废话，直接输出 Prompt。
        """
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9 # 高创造性
            )
            content = response.choices[0].message.content.strip()
            # 强制修正格式，防止 AI 忘记加前缀
            if not content.startswith(f"**方案{idx}"):
                content = f"**方案{idx}：** {content}"
            results.append(content)
            
        except Exception as e:
            results.append(f"**方案{idx}：** 生成失败 ({str(e)})")
            
    return results

# ==========================================
# 3. 界面交互区
# ==========================================
st.title("🎨 Graphic Lab")
st.caption("图形纹身生成实验室")

# 输入区
c1, c2 = st.columns([3, 1])
with c1:
    user_input = st.text_input("核心主体 (Core Subject)", placeholder="留空则开启盲盒模式 (Random Blind Box)")
with c2:
    qty = st.number_input("生成数量", min_value=1, max_value=5, value=4)

# 生成按钮
if st.button("开始生成 (Generate)", type="primary", use_container_width=True):
    with st.spinner("正在组装创意并进行 AI 润色..."):
        # 1. 组装骨架
        skeleton = assemble_graphic_skeleton(user_input)
        st.toast(f"骨架已组装: {skeleton}")
        
        # 2. AI 润色
        solutions = run_ai_polish(skeleton, qty)
        
        # 3. 存入 Session 供自动化使用
        st.session_state.final_solutions = solutions
        
        # 4. 强制刷新显示结果
        st.rerun()

# ==========================================
# 4. 结果展示与投递
# ==========================================
if "final_solutions" in st.session_state and st.session_state.final_solutions:
    st.markdown("---")
    st.subheader("生成结果")
    
    # 展示结果卡片
    for sol in st.session_state.final_solutions:
        st.info(sol)
        
    # 投递按钮
    if st.button("🚀 发送至自动化中心 (Send to Automation)", use_container_width=True):
        st.switch_page("pages/03_🚀_Automation.py")
