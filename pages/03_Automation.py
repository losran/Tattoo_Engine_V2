import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import os
import sys

# ===========================
# 0. 基础路径设置
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

default_text = ""
if st.session_state.global_queue:
    valid_tasks = [t for t in st.session_state.global_queue if t.strip()]
    default_text = "\n\n".join(valid_tasks)

# ===========================
# 2. 界面布局
# ===========================
st.markdown("## Automation Central")
st.caption("🚀 Universal Script (Compatible with Mirror Sites)")

col_opt, col_clear = st.columns([3, 1])
with col_opt:
    # 🔥 新增了 "Mirror Site / Doubao" 选项 🔥
    target_platform = st.selectbox(
        "Select Target Platform", 
        ["Mirror Site / Doubao (镜像站/豆包)", "Gemini (Google)", "Midjourney (Discord)", "ChatGPT (Official)"],
        help="Use 'Mirror Site' for Doubao, domestic AI wrappers, or unknown sites."
    )
with col_clear:
    if st.button("🗑️ Clear Queue"):
        st.session_state.global_queue = []
        st.rerun()

user_input = st.text_area("Task Queue", value=default_text, height=350, key="main_input_area")

if user_input != default_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 3. 核心生成逻辑
# ===========================
if st.button(f"⚡ Generate Script for {target_platform}", type="primary", use_container_width=True):
    task_list = []
    if user_input:
        if "###" in user_input:
            task_list = [t.strip() for t in user_input.split("###") if len(t.strip()) > 5]
        elif "**方案" in user_input:
            import re
            blocks = re.split(r'(?:\*\*)?方案[一二三四五六七八九十\d]+[:：\s]?(?:\*\*)?', user_input)
            task_list = [b.strip() for b in blocks if len(b.strip()) > 5]
        else:
            task_list = [t.strip() for t in user_input.split('\n\n') if len(t.strip()) > 5]

    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))

        # 公共安全 UI (No innerHTML)
        common_ui_safe = """
            function showStatus(text, color) {
                let el = document.getElementById('magic-status-bar');
                if (!el) {
                    el = document.createElement('div');
                    el.id = 'magic-status-bar';
                    el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:9999999; padding:12px 24px; border-radius:30px; font-family:sans-serif; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 10px 25px rgba(0,0,0,0.4); transition: all 0.3s;";
                    document.body.appendChild(el);
                }
                el.textContent = text;
                el.style.backgroundColor = color || "#333";
            }
        """

        # ---------------------------------------------------------
        # 🎯 镜像站 / 豆包 / 通用暴力版 (Mirror/Universal)
        # ---------------------------------------------------------
        if "Mirror" in target_platform:
            js_code = f"""(async function() {{
                {common_ui_safe}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;

                showStatus("🚀 Mirror/Universal Mode", "#8b5cf6");

                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    
                    // 1. 暴力查找输入框 (遍历常见的输入框特征)
                    let box = document.querySelector('textarea') || 
                              document.querySelector('div[contenteditable="true"]') || 
                              document.querySelector('input[type="text"]');
                              
                    if (!box) {{ 
                        // 如果没找到，尝试找 class 里带 input 的 div
                        box = Array.from(document.querySelectorAll('div')).find(e => e.className.includes('input'));
                    }}

                    if (!box) {{ 
                        showStatus("❌ No Input Found", "#ef4444"); 
                        break; 
                    }}
                    
                    showStatus("✍️ Writing Task " + (i+1), "#8b5cf6");
                    box.focus();
                    
                    // 2. 暴力输入 (兼容 React/Vue)
                    // 先尝试 execCommand (最通用)
                    if (document.execCommand) {{
                        document.execCommand('insertText', false, tasks[i]);
                    }} else {{
                        box.value = tasks[i];
                        box.innerText = tasks[i];
                    }}
                    
                    // 触发 Input 事件 (唤醒前端框架)
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 1000));

                    // 3. 暴力查找发送按钮
                    // 策略：找由 button 标签、或 role=button 的元素
                    let allBtns = Array.from(document.querySelectorAll('button, div[role="button"], span[role="button"]'));
                    let sendBtn = allBtns.find(b => {{
                        let t = (b.innerText || b.getAttribute('aria-label') || "").toLowerCase();
                        // 特征词：send, 发送, 提交, submit
                        // 排除：stop, 停止, cancel
                        if (t.includes('stop') || t.includes('停止') || t.includes('cancel')) return false;
                        if (b.disabled) return false;
                        
                        return t.includes('send') || t.includes('发送') || t.includes('提交') || b.querySelector('svg'); 
                    }});

                    if (sendBtn) {{
                        sendBtn.click();
                    }} else {{
                        // 没按钮？回车伺候
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}

                    // 4. 盲等 (镜像站通常没有统一的 Stop 按钮标准)
                    showStatus("⏳ Waiting (Blind)...", "#555");
                    
                    // 基础等待 5 秒
                    await new Promise(r => setTimeout(r, 5000));
                    
                    // 智能轮询：检查页面上是否有“停止”字样的按钮出现
                    let waitSec = 0;
                    while (true) {{
                        if (window.kill) break;
                        
                        // 只要有“停止生成”按钮，就继续等
                        let stopBtn = Array.from(document.querySelectorAll('button, div[role="button"]')).find(b => {{
                            let t = (b.innerText || b.getAttribute('aria-label') || "").toLowerCase();
                            return t.includes('stop') || t.includes('停止');
                        }});
                        
                        if (!stopBtn) break; // 没停止按钮了，说明好了
                        
                        await new Promise(r => setTimeout(r, 1000));
                        waitSec++;
                        if (waitSec > 180) break; // 最多等3分钟
                    }}

                    // 额外冷却
                    showStatus("✅ Done. Next...", "#43a047");
                    await new Promise(r => setTimeout(r, 3000));
                }}
            }})();"""

        # ---------------------------------------------------------
        # 🎯 Gemini 专用
        # ---------------------------------------------------------
        elif "Gemini" in target_platform:
            js_code = f"""(async function() {{
                {common_ui_safe}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;
                showStatus("🚀 Gemini Mode", "#1e88e5");
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    let box = document.querySelector('.rich-textarea') || document.querySelector('div[contenteditable="true"]');
                    if (!box) {{ showStatus("❌ No Input", "#ef4444"); break; }}
                    showStatus("✍️ Task " + (i+1), "#1e88e5");
                    box.focus();
                    document.execCommand('insertText', false, tasks[i]); 
                    await new Promise(r => setTimeout(r, 1000));
                    let sendBtn = document.querySelector('.send-button') || document.querySelector('button[aria-label*="Send"]');
                    if (sendBtn) sendBtn.click();
                    else box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    showStatus("⏳ Generating...", "#555");
                    await new Promise(r => setTimeout(r, 5000));
                    while(true) {{
                        if (window.kill) break;
                        let stopBtn = document.querySelector('button[aria-label*="Stop"]');
                        if (!stopBtn) break;
                        await new Promise(r => setTimeout(r, 1000));
                    }}
                    await new Promise(r => setTimeout(r, 3000));
                }}
            }})();"""

        # ---------------------------------------------------------
        # 🎯 Midjourney / Discord
        # ---------------------------------------------------------
        elif "Midjourney" in target_platform:
            js_code = f"""(async function() {{
                {common_ui_safe}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;
                showStatus("🚀 Discord Mode", "#5865F2");
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    let box = document.querySelector('[role="textbox"]');
                    if (!box) {{ showStatus("❌ No Input", "#ef4444"); break; }}
                    showStatus("✍️ Task " + (i+1), "#5865F2");
                    box.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('insertText', false, tasks[i]); 
                    await new Promise(r => setTimeout(r, 800));
                    box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    showStatus("⏳ Queued...", "#555");
                    await new Promise(r => setTimeout(r, 5000));
                    while(true) {{
                        if (window.kill) break;
                        let msgs = document.querySelectorAll('li[class*="message"]');
                        if (msgs.length > 0) {{
                            let lastTxt = msgs[msgs.length-1].innerText;
                            if (!lastTxt.includes('Waiting') && !lastTxt.includes('%') && !lastTxt.includes('(fast)')) break;
                        }}
                        await new Promise(r => setTimeout(r, 2000));
                    }}
                    await new Promise(r => setTimeout(r, 3000));
                }}
            }})();"""

        # ---------------------------------------------------------
        # 🎯 ChatGPT (Official)
        # ---------------------------------------------------------
        else:
            js_code = f"""(async function() {{
                {common_ui_safe}
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                window.kill = false;
                showStatus("🚀 ChatGPT Mode", "#10a37f");
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) break;
                    let box = document.querySelector('#prompt-textarea');
                    if (!box) {{ showStatus("❌ No Input", "#ef4444"); break; }}
                    showStatus("✍️ Task " + (i+1), "#10a37f");
                    box.value = tasks[i];
                    box.dispatchEvent(new Event('input', {{bubbles:true}}));
                    await new Promise(r => setTimeout(r, 500));
                    let sendBtn = document.querySelector('[data-testid="send-button"]');
                    if (sendBtn) sendBtn.click();
                    showStatus("⏳ Waiting...", "#555");
                    await new Promise(r => setTimeout(r, 3000));
                    while(true) {{
                        if (window.kill) break;
                        if (!document.querySelector('[aria-label="Stop generating"]')) break;
                        await new Promise(r => setTimeout(r, 1000));
                    }}
                    await new Promise(r => setTimeout(r, 2000));
                }}
            }})();"""

        # 自动复制
        js_val = json.dumps(js_code)
        components.html(f"""
        <script>
            const text = {js_val};
            if(navigator.clipboard) {{
                navigator.clipboard.writeText(text).then(() => console.log('Copied')).catch(err => console.log('Err', err));
            }}
        </script>
        """, height=0)

        st.success(f"✅ Generated Script for **{target_platform}**. Copied!")
        with st.expander("View Code"):
            st.code(js_code, language="javascript")
    else:
        st.error("❌ Queue is empty")
