import streamlit as st
from style_manager import apply_pro_style
import streamlit.components.v1 as components
import json
import urllib.parse
import re
import os
import sys

# ===========================
# 0. 路径修复 (防止报错)
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import render_sidebar, init_data

# 1. 基础配置
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()
init_data()

# 2. 样式注入 (保留您喜欢的深色样式)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
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

st.title("🤖 自动化任务分发中控")

# 3. 数据同步 (🔥 核心修复：接通 Text Studio 的数据 🔥)
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 优先从 global_queue 取数据，如果没有才取旧缓存
default_text = ""
if st.session_state.global_queue:
    # 过滤空行并拼接
    valid_tasks = [t for t in st.session_state.global_queue if t.strip()]
    default_text = "\n\n".join(valid_tasks)
else:
    default_text = st.session_state.get('auto_input_cache', "")

# 4. 平台选择
col_opt1, col_opt2 = st.columns([2, 1])
with col_opt1:
    target_platform = st.selectbox(
        "选择目标 AI 平台", 
        ["万能自适应 (推荐)", "Gemini", "ChatGPT", "Doubao"],
        help="Universal mode adapts to most chat interfaces."
    )

# 5. 输入区域
user_input = st.text_area("Prompt Queue", value=default_text, height=300, key="main_input_area")

# 双向绑定：修改文本框后更新队列
if user_input != default_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

# --- Options ---
st.divider()
col_check, col_btn = st.columns([1, 2])
with col_check:
    need_white_bg = st.checkbox("Production Mode: Auto White Background", value=False)

# --- Generation Logic ---
with col_btn:
    # Primary button (Deep Grey Style)
    if st.button("Generate Script (v15.0 Fixed)", type="primary", use_container_width=True):
        # --- A. Task Parsing ---
        task_list = []
        if user_input:
            # Handle manual separator '###'
            if "###" in user_input:
                raw_tasks = [t.strip() for t in user_input.split("###") if len(t.strip()) > 2]
            elif "**方案" in user_input:
                # Handle auto-generated format "**Scheme 1:**"
                blocks = re.split(r'\*\*.*?(?:方案|Scheme|Option).*?[\d]+[:：].*?\*\*', user_input)
                raw_tasks = [b.strip().replace('* ', '').replace('\n', ' ') for b in blocks if len(b.strip()) > 5]
            else:
                # 简单换行切分 (兜底)
                raw_tasks = [t.strip() for t in user_input.split('\n\n') if len(t.strip()) > 5]
            
            if need_white_bg:
                for t in raw_tasks:
                    task_list.append(t)
                    task_list.append("Generate a white background version of the image above")
            else:
                task_list = raw_tasks

        # --- B. Script Construction ---
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            # JS Core Logic (保留 v15.0 原味，微调兼容性)
            js_code = f"""(async function() {{
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                // 🔥 状态条渲染 (使用 textContent 防止 TrustedHTML 报错) 🔥
                function showStatus(text, color = "#1e293b", textColor = "#fff") {{
                    let el = document.getElementById('magic-status-bar');
                    if (!el) {{
                        el = document.createElement('div');
                        el.id = 'magic-status-bar';
                        el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:10px 20px; border-radius:30px; font-family:sans-serif; font-size:14px; font-weight:bold; box-shadow:0 10px 25px rgba(0,0,0,0.2); transition: all 0.3s;";
                        document.body.appendChild(el);
                    }}
                    el.textContent = text; 
                    el.style.backgroundColor = color;
                    el.style.color = textColor;
                }}

                function getInputBox() {{
                    let geminiBox = document.querySelector('div[role="textbox"][contenteditable="true"]') || document.querySelector('.rich-textarea');
                    if (geminiBox) return geminiBox;
                    return document.querySelector('#prompt-textarea, [data-testid="rich-textarea"], textarea, .n-input__textarea-el, [placeholder*="Enter"], [placeholder*="Message"], [placeholder*="输入"]');
                }}

                function getSendBtn() {{
                    // 1. 优先找明确的 Send 按钮
                    let explicitBtn = document.querySelector('button[aria-label*="Send"], button[aria-label*="发送"], button[data-testid="send-button"]');
                    if (explicitBtn && !explicitBtn.disabled) return explicitBtn;
                    
                    // 2. 模糊查找 (适配 Gemini 图标按钮)
                    let btns = Array.from(document.querySelectorAll('button, [role="button"], i'));
                    return btns.find(b => {{
                        const t = (b.innerText || b.ariaLabel || b.className || b.outerHTML || "").toLowerCase();
                        const isSend = t.includes('send') || t.includes('发') || t.includes('m12 2 2 21 5 12 10 12'); 
                        const isStop = t.includes('stop') || t.includes('停止');
                        return isSend && !isStop && b.offsetParent !== null && !b.disabled;
                    }});
                }}

                function isGenerating() {{
                    let btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                    return btns.some(b => {{
                        const t = (b.innerText || b.ariaLabel || "").toLowerCase();
                        return t.includes('stop') || t.includes('停止') || t.includes('generating');
                    }});
                }}

                showStatus("🚀 Script Ready...", "#444444"); 
                
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 Stopped", "#ef4444"); break; }}
                    
                    showStatus("✍️ Inputting: " + (i+1) + "/" + tasks.length, "#666666");
                    let box = getInputBox();
                    if (!box) {{ showStatus("❌ Input Box Not Found", "#ef4444"); break; }}
                    
                    box.focus();
                    // 使用 execCommand 兼容性最强
                    if (document.execCommand) {{
                        document.execCommand('insertText', false, tasks[i]); 
                    }} else {{
                        box.value = tasks[i];
                        box.innerText = tasks[i];
                    }}
                    
                    await new Promise(r => setTimeout(r, 1000));
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 800));
                    let sendBtn = getSendBtn();
                    if (sendBtn) {{
                        sendBtn.click();
                    }} else {{
                        // 回车兜底
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}
                    
                    if (i < tasks.length - 1) {{
                        let waitTime = 0;
                        await new Promise(r => setTimeout(r, 3000));
                        while(true) {{
                            if (window.kill) break;
                            if (!isGenerating()) break;
                            showStatus("🎨 Generating (" + waitTime + "s)...", "#888888");
                            await new Promise(r => setTimeout(r, 1000));
                            waitTime++;
                            if (waitTime > 180) break;
                        }}
                        for (let s = 5; s > 0; s--) {{
                            if (window.kill) break;
                            showStatus("⏳ Cooldown: " + s + "s", "#b45309");
                            await new Promise(r => setTimeout(r, 1000));
                        }}
                    }}
                }}
                if(!window.kill) showStatus("🎉 All Tasks Completed!", "#15803d");
            }})();"""

            js_val = json.dumps(js_code)
            components.html(f"""
            <script>
                const text = {js_val};
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(text).catch(err => console.log('Auto-copy failed'));
                }}
            </script>
            """, height=0)

            st.success(f"Generated {len(task_list)} task instructions. Script copied to clipboard.")
            st.code(js_code, language="javascript")
            
        else:
            st.error("No valid tasks found in queue.")

# Clear Button
if st.button("Clear Queue"):
    st.session_state.global_queue = []
    st.session_state.auto_input_cache = ""
    st.session_state.polished_text = ""
    st.rerun()
