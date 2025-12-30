import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import re
import os
import sys

# ===========================
# 0. 基础路径 & 样式
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import render_sidebar, init_data
from style_manager import apply_pro_style

st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style() # 保持好看的 Pro 样式
render_sidebar()
init_data()

# ===========================
# 1. 样式增强 (复刻 v16 时的输入框样式)
# ===========================
st.markdown("""
<style>
    .stTextArea textarea {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        font-family: 'Consolas', 'Monaco', monospace;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff4b4b 0%, #d62f2f 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2) !important;
        height: 50px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 自动化任务分发")

# ===========================
# 2. 数据接通 (这是唯一必须加的功能，不然无法读取)
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 从 global_queue 获取数据
default_text = ""
if st.session_state.global_queue:
    valid_tasks = [t for t in st.session_state.global_queue if t.strip()]
    default_text = "\n\n".join(valid_tasks)
else:
    # 兼容旧缓存
    default_text = st.session_state.get('auto_input_cache', "") or st.session_state.get('polished_text', "")

# ===========================
# 3. 界面布局
# ===========================
col_opt1, col_opt2 = st.columns([2, 1])
with col_opt1:
    target_platform = st.selectbox(
        "选择目标 AI 平台", 
        ["万能自适应 (推荐)", "ChatGPT", "Doubao (豆包/镜像站)", "Claude"],
        help="不同平台输入框构造不同，手动选择更精准"
    )

with col_opt2:
    st.write("") # 排版占位
    if st.button("🗑️ 清空队列", use_container_width=True):
        st.session_state.global_queue = []
        st.session_state.auto_input_cache = ""
        st.session_state.polished_text = ""
        st.rerun()

user_input = st.text_area("检查待处理的提示词内容：", value=default_text, height=300, key="main_input_area")

# 双向绑定
if user_input != default_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 4. 核心逻辑 (100% 还原 V16.0 JS 代码)
# ===========================
col_check, col_btn = st.columns([1, 2])
with col_check:
    need_white_bg = st.checkbox("🏭 生产模式：每张图后自动生成白底图", value=False)

with col_btn:
    if st.button("🚀 生成全能适配脚本 (v16.0 深度加固版)", type="primary", use_container_width=True):
        task_list = []
        if user_input:
            # V16.0 的切分逻辑
            if "###" in user_input:
                raw_tasks = [t.strip() for t in user_input.split("###") if len(t.strip()) > 5]
            else:
                # 增强正则
                blocks = re.split(r'(?:\*\*)?方案[一二三四五六七八九十\d]+[:：\s]?(?:\*\*)?', user_input)
                raw_tasks = [b.strip() for b in blocks if len(b.strip()) > 10]
            
            # 如果没正则切分出来，尝试简单的换行切分
            if not raw_tasks:
                 raw_tasks = [t.strip() for t in user_input.split('\n\n') if len(t.strip()) > 5]

            # 生产模式插入白底图指令
            for t in raw_tasks:
                task_list.append(t)
                if need_white_bg:
                    task_list.append("生成上图的白底平面图，去除背景，纯白底， isolated on white background")

        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))

            # 🔥🔥🔥 V16.0 原版 JS 代码 (一个字都没改) 🔥🔥🔥
            js_code = f"""(async function() {{
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                function showStatus(text, color = "#6366f1") {{
                    let el = document.getElementById('magic-status-bar');
                    if (!el) {{
                        el = document.createElement('div');
                        el.id = 'magic-status-bar';
                        el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:9999999; padding:12px 24px; border-radius:30px; font-family:sans-serif; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 10px 25px rgba(0,0,0,0.4); transition: all 0.3s;";
                        document.body.appendChild(el);
                    }}
                    el.textContent = text;
                    el.style.backgroundColor = color;
                }}

                function getInputBox() {{
                    return document.querySelector('#prompt-textarea, [contenteditable="true"], textarea, .n-input__textarea-el, [placeholder*="输入"], [placeholder*="提问"]');
                }}

                async function safeInput(box, text) {{
                    box.focus();
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set 
                                || Object.getOwnPropertyDescriptor(window.HTMLElement.prototype, "innerText")?.set;
                    if (box.tagName === 'DIV') box.innerText = text;
                    else setter ? setter.call(box, text) : (box.value = text);
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}

                showStatus("🚀 脚本启动 (v16.0)", "#6366f1");

                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 已停止", "#ef4444"); break; }}
                    
                    showStatus(`✍️ 正在输入: ${{i+1}}/${{tasks.length}}`, "#3b82f6");
                    let box = getInputBox();
                    if (!box) {{ showStatus("❌ 未找到输入框", "#ef4444"); break; }}
                    
                    await safeInput(box, tasks[i]);
                    await new Promise(r => setTimeout(r, 1000));

                    let btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                    let sendBtn = btns.find(b => {{
                        const t = (b.innerText || b.ariaLabel || b.className || "").toLowerCase();
                        return (t.includes('发') || t.includes('send') || b.getAttribute('data-testid') === 'send-button') && !b.disabled && b.offsetParent !== null;
                    }});

                    if (sendBtn) sendBtn.click();
                    else box.dispatchEvent(new KeyboardEvent('keydown', {{bubbles:true, key:'Enter', code:'Enter', keyCode:13, ctrlKey: true}}));

                    await new Promise(r => setTimeout(r, 4000));
                    let waitTime = 0;
                    while(!window.kill) {{
                        const isGenerating = Array.from(document.querySelectorAll('button')).some(b => {{
                            const t = (b.innerText || b.ariaLabel || "").toLowerCase();
                            return t.includes('stop') || t.includes('停止') || t.includes('generating');
                        }});
                        if (!isGenerating) break;
                        showStatus(`🎨 作画中 (${{waitTime}}s)...`, "#8b5cf6");
                        await new Promise(r => setTimeout(r, 1000));
                        if (waitTime++ > 180) break;
                    }}

                    if (i < tasks.length - 1) {{
                        for (let s = 5; s > 0; s--) {{
                            if (window.kill) break;
                            showStatus(`⏳ 冷却等待: ${{s}}s`, "#f59e0b");
                            await new Promise(r => setTimeout(r, 1000));
                        }}
                    }}
                }}
                showStatus("🎉 任务全部完成！", "#10b981");
                setTimeout(() => document.getElementById('magic-status-bar')?.remove(), 5000);
            }})();"""

            # 自动复制
            js_val = json.dumps(js_code)
            components.html(f"""
            <script>
                const text = {js_val};
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(text).then(() => console.log('Copied')).catch(err => console.log('Err', err));
                }}
            </script>
            """, height=0)

            st.success(f"✅ 已生成 {len(task_list)} 条任务指令！")
            with st.expander("查看生成的代码"):
                st.code(js_code, language="javascript")
        else:
            st.error("❌ 未识别到任务，请确保包含 '方案' 或 '###'")
