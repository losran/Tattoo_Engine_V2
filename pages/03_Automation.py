import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import re
import os
import sys

# ===========================
# 0. 基础设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import render_sidebar, init_data
from style_manager import apply_pro_style

# 1. 页面配置 & 全局样式
st.set_page_config(layout="wide", page_title="Automation Central")

# 🔥 核心：只调用全局样式，不写任何局部 CSS 🔥
apply_pro_style() 
render_sidebar()
init_data()

st.title("🤖 自动化任务分发")

# ===========================
# 2. 数据接通
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

default_text = ""
if st.session_state.global_queue:
    valid_tasks = [t for t in st.session_state.global_queue if t.strip()]
    default_text = "\n\n".join(valid_tasks)
else:
    default_text = st.session_state.get('auto_input_cache', "")

# ===========================
# 3. 界面布局
# ===========================
col_opt1, col_opt2 = st.columns([3, 1])

with col_opt1:
    target_platform = st.selectbox(
        "选择目标平台", 
        ["万能自适应 (推荐)", "ChatGPT", "Doubao (豆包/镜像站)", "Claude"],
        help="v15.0 内核：最强兼容性版本"
    )

with col_opt2:
    # 稍微留白对齐
    st.write("") 
    if st.button("🗑️ 清空队列", use_container_width=True):
        st.session_state.global_queue = []
        st.session_state.auto_input_cache = ""
        st.rerun()

user_input = st.text_area("任务队列", value=default_text, height=350, key="main_input_area")

if user_input != default_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 4. 核心逻辑 (v15.0 原版内核)
# ===========================
col_check, col_btn = st.columns([1, 2])
with col_check:
    need_white_bg = st.checkbox("🏭 生产模式：追加白底指令", value=False)

with col_btn:
    if st.button("🚀 生成自动化脚本 (v15.0 Core)", type="primary", use_container_width=True):
        task_list = []
        if user_input:
            if "###" in user_input:
                raw_tasks = [t.strip() for t in user_input.split("###") if len(t.strip()) > 5]
            elif "**方案" in user_input:
                blocks = re.split(r'(?:\*\*)?方案[一二三四五六七八九十\d]+[:：\s]?(?:\*\*)?', user_input)
                raw_tasks = [b.strip() for b in blocks if len(b.strip()) > 10]
            else:
                raw_tasks = [t.strip() for t in user_input.split('\n\n') if len(t.strip()) > 5]
            
            for t in raw_tasks:
                task_list.append(t)
                if need_white_bg:
                    task_list.append("生成上图的白底平面图，去除背景，纯白底， isolated on white background")

        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))

            # 🔥🔥🔥 100% v15.0 原版 JS 逻辑 (含 safeInput & execCommand) 🔥🔥🔥
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

                showStatus("🚀 脚本启动 (v15.0)", "#6366f1");

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
                        if (t.includes('stop') || t.includes('停止')) return false;
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

            js_val = json.dumps(js_code)
            components.html(f"""
            <script>
                const text = {js_val};
                if(navigator.clipboard) {{
                    navigator.clipboard.writeText(text).then(() => console.log('Copied')).catch(err => console.log('Err', err));
                }}
            </script>
            """, height=0)

            st.success(f"✅ 已生成 {len(task_list)} 条指令，代码已复制！")
            with st.expander("查看代码"):
                st.code(js_code, language="javascript")
        else:
            st.error("❌ 队列为空")
