import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
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

st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# 1. 数据同步
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

default_text = "\n\n".join(st.session_state.global_queue) if st.session_state.global_queue else ""

# ===========================
# 2. 界面布局 (回归经典下拉框)
# ===========================
st.markdown("## Automation Central")
st.caption("🚀 Platform-Specific Scripts (Simple & Stable)")

col_opt1, col_opt2 = st.columns([3, 1])
with col_opt1:
    # 🔥 关键：用户选什么，就生成什么，绝不混淆 🔥
    target_platform = st.selectbox(
        "Choose Platform (Target Website)",
        ["Gemini (Google)", "Midjourney (Discord)", "ChatGPT (OpenAI)", "Universal (Fallback)"]
    )
with col_opt2:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

user_input = st.text_area(
    "Task Queue", 
    value=default_text, 
    height=350, 
    key="main_input_area",
    placeholder="Tasks from Studio will appear here..."
)

# 数据回写
if user_input != default_text:
    st.session_state.global_queue = [t for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 3. 核心生成逻辑 (彻底拆分)
# ===========================
if st.button(f"⚡ Generate Script for {target_platform}", type="primary", use_container_width=True):
    
    # --- A. 简单任务解析 ---
    task_list = []
    if user_input:
        # 简单按行或空行切分，不再搞复杂的正则
        if "###" in user_input:
            task_list = [t.strip() for t in user_input.split("###") if len(t.strip()) > 2]
        elif "**方案" in user_input:
             import re
             blocks = re.split(r'\*\*.*?(?:方案|Scheme|Option|Task).*?[\d]+[:：].*?\*\*', user_input)
             task_list = [b.strip() for b in blocks if len(b.strip()) > 5]
        else:
             task_list = [t.strip() for t in user_input.split('\n') if t.strip()]

    # --- B. 脚本构造 (分平台) ---
    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))
        
        # 公共函数：安全的 UI 渲染 (Google不报错)
        common_ui_func = """
            function showStatus(text, color) {
                let el = document.getElementById('magic-status-bar');
                if (!el) {
                    el = document.createElement('div');
                    el.id = 'magic-status-bar';
                    el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:12px 24px; border-radius:8px; font-family:sans-serif; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 5px 15px rgba(0,0,0,0.3);";
                    document.body.appendChild(el);
                }
                el.textContent = text;
                el.style.backgroundColor = color || "#333";
            }
        """

        # 🎯 1. Gemini 专用脚本
        if "Gemini" in target_platform:
            js_code = f"""(async function() {{
                {common_ui_func}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;

                showStatus("🚀 Gemini Mode Started", "#1e88e5");

                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    
                    // 1. 找输入框 (Gemini 是 contenteditable 的 div)
                    let box = document.querySelector('.rich-textarea') || document.querySelector('div[contenteditable="true"]');
                    if (!box) {{ alert("Can't find Gemini input box!"); break; }}
                    
                    showStatus("✍️ Writing Task " + (i+1), "#1e88e5");
                    box.focus();
                    document.execCommand('insertText', false, tasks[i]); 
                    
                    await new Promise(r => setTimeout(r, 1000));

                    // 2. 发送 (点击那个蓝色的箭头或图标)
                    let sendBtn = document.querySelector('.send-button') || document.querySelector('button[aria-label*="Send"]') || document.querySelector('button[aria-label*="发送"]');
                    if (sendBtn) {{
                        sendBtn.click();
                    }} else {{
                        // Gemini 有时候找不到按钮，用回车兜底
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}

                    // 3. 死等 (Gemini 生成时会有 Stop 按钮)
                    showStatus("⏳ Waiting...", "#555");
                    await new Promise(r => setTimeout(r, 5000)); // 强制等5秒
                    
                    while(true) {{
                        if (window.kill) break;
                        // 只要能找到 label 包含 Stop/停止 的按钮，就是正在生成
                        let stopBtn = Array.from(document.querySelectorAll('button')).find(b => (b.ariaLabel||"").toLowerCase().includes('stop'));
                        if (!stopBtn) break; // 没 Stop 了，说明完了
                        await new Promise(r => setTimeout(r, 1000));
                    }}
                    
                    // 冷却
                    showStatus("✅ Done. Cooldown...", "#43a047");
                    await new Promise(r => setTimeout(r, 3000));
                }}
            }})();"""

        # 🎯 2. Midjourney (Discord) 专用脚本
        elif "Midjourney" in target_platform:
            js_code = f"""(async function() {{
                {common_ui_func}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;

                showStatus("🚀 Discord Mode Started", "#5865F2");

                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    
                    // 1. 找输入框 (Discord class 经常变，用 role 最稳)
                    let box = document.querySelector('[role="textbox"]') || document.querySelector('div[class*="slateTextArea"]');
                    if (!box) {{ alert("No Discord input found!"); break; }}
                    
                    showStatus("✍️ Task " + (i+1), "#5865F2");
                    box.focus();
                    
                    // Discord 需要先清空默认的 placeholder
                    document.execCommand('insertText', false, tasks[i]); 
                    
                    await new Promise(r => setTimeout(r, 800));
                    
                    // 2. 发送 (Discord 必须用回车)
                    box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    
                    // 3. 等待 (检测 "Waiting to start" 或 进度条)
                    showStatus("⏳ Queued...", "#555");
                    await new Promise(r => setTimeout(r, 5000));

                    while(true) {{
                        if (window.kill) break;
                        // 检查最后一条消息内容
                        let msgs = document.querySelectorAll('li[class*="message"]');
                        if (msgs.length > 0) {{
                            let lastTxt = msgs[msgs.length-1].innerText;
                            if (!lastTxt.includes('Waiting') && !lastTxt.includes('%') && !lastTxt.includes('(fast)')) {{
                                break; // 没这些关键词了，说明出图了
                            }}
                        }}
                        await new Promise(r => setTimeout(r, 2000));
                    }}
                    
                    showStatus("✅ Next...", "#43a047");
                    await new Promise(r => setTimeout(r, 5000));
                }}
            }})();"""

        # 🎯 3. ChatGPT 专用脚本
        elif "ChatGPT" in target_platform:
            js_code = f"""(async function() {{
                {common_ui_func}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;

                showStatus("🚀 ChatGPT Mode", "#10a37f");

                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    
                    let box = document.querySelector('#prompt-textarea');
                    if (!box) {{ alert("No ChatGPT input!"); break; }}
                    
                    showStatus("✍️ Task " + (i+1), "#10a37f");
                    box.value = tasks[i]; // ChatGPT 支持直接赋值
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 500));
                    
                    let sendBtn = document.querySelector('[data-testid="send-button"]');
                    if (sendBtn) sendBtn.click();
                    
                    showStatus("⏳ Thinking...", "#555");
                    await new Promise(r => setTimeout(r, 3000));
                    
                    while(true) {{
                        if (window.kill) break;
                        // ChatGPT 生成时有 Stop 按钮
                        if (!document.querySelector('[aria-label="Stop generating"]')) break;
                        await new Promise(r => setTimeout(r, 1000));
                    }}
                    
                    showStatus("✅ Done", "#10a37f");
                    await new Promise(r => setTimeout(r, 2000));
                }}
            }})();"""
            
        # 🎯 4. 通用版 (Fallback)
        else:
             js_code = f"""(async function() {{
                {common_ui_func}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                alert("Universal mode: Attempting to type " + tasks.length + " tasks.");
                
                for (let i = 0; i < tasks.length; i++) {{
                    let box = document.querySelector('textarea, [contenteditable="true"]');
                    if(box) {{
                        box.focus();
                        document.execCommand('insertText', false, tasks[i]);
                        await new Promise(r => setTimeout(r, 1000));
                        // 尝试按回车
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                        // 盲等10秒
                        await new Promise(r => setTimeout(r, 10000));
                    }}
                }}
             }})();"""

        # --- C. 自动复制到剪贴板 ---
        js_val = json.dumps(js_code)
        components.html(f"""
        <script>
            const text = {js_val};
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text).catch(e => console.error(e));
            }}
        </script>
        """, height=0)

        st.success(f"✅ Generated script for **{target_platform}**. Code copied!")
        with st.expander("View Code", expanded=True):
            st.code(js_code, language="javascript")
        
    else:
        st.error("⚠️ Queue is empty.")
