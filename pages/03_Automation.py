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

st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# 1. 数据同步
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 将列表转换为字符串显示在文本框中
default_text = "\n\n".join(st.session_state.global_queue) if st.session_state.global_queue else ""

# ===========================
# 2. UI 布局
# ===========================
st.markdown("## Automation Central")
st.caption("Universal AI Platform Adaptor (Classic Stable Version)")

col_opt1, col_opt2 = st.columns([3, 1])
with col_opt1:
    target_platform = st.selectbox(
        "Target Platform",
        ["Universal (Recommended)", "Midjourney/Discord", "ChatGPT", "Gemini"],
        help="Universal mode works on 99% of chat interfaces."
    )
with col_opt2:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

# 核心输入区域
user_input = st.text_area(
    "Task Queue", 
    value=default_text, 
    height=350, 
    key="main_input_area",
    placeholder="Tasks from Studio will appear here..."
)

# 双向绑定：文本框修改后回写到 session
if user_input != default_text:
    st.session_state.global_queue = [t for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 3. 核心生成逻辑 (还原经典版)
# ===========================
if st.button("⚡ Generate Script (v15.0)", type="primary", use_container_width=True):
    
    # --- A. 任务解析 (Regex Splitting) ---
    task_list = []
    if user_input:
        # 优先尝试按 "###" 分割
        if "###" in user_input:
            raw_tasks = [t.strip() for t in user_input.split("###") if len(t.strip()) > 2]
        else:
            # 经典正则分割：匹配 "**方案N：**" 或 "**Option N:**"
            # 这种方式最稳，不管中间有多少换行符都能切开
            blocks = re.split(r'\*\*.*?(?:方案|Scheme|Option|Task).*?[\d]+[:：].*?\*\*', user_input)
            
            # 如果正则没切开（比如没有方案头），就按双换行切
            if len(blocks) < 2:
                raw_tasks = [t.strip() for t in user_input.split('\n\n') if t.strip()]
            else:
                raw_tasks = [b.strip() for b in blocks if len(b.strip()) > 5]
        
        task_list = raw_tasks

    # --- B. 脚本构造 ---
    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))
        
        # 经典的 JS 逻辑
        js_code = f"""(async function() {{
            console.clear();
            console.log("%c 🚀 Automation Started ", "background: #222; color: #bada55");
            window.kill = false;
            const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
            
            // 状态条
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

            // 查找输入框
            function getInputBox() {{
                // 优先找 contenteditable (适用 Gemini, MJ Web, Claude)
                let divBox = document.querySelector('div[role="textbox"][contenteditable="true"]');
                if (divBox) return divBox;
                // 其次找 textarea (适用 ChatGPT, Discord)
                return document.querySelector('#prompt-textarea, [data-testid="rich-textarea"], textarea, .n-input__textarea-el, [placeholder*="Message"], [placeholder*="输入"]');
            }}

            // 查找发送按钮
            function getSendBtn() {{
                // 1. 显式 aria-label
                let explicitBtn = document.querySelector('button[aria-label*="Send"], button[aria-label*="发送"]');
                if (explicitBtn && !explicitBtn.disabled) return explicitBtn;
                
                // 2. 遍历查找
                let btns = Array.from(document.querySelectorAll('button, [role="button"], i'));
                return btns.find(b => {{
                    const t = (b.innerText || b.ariaLabel || b.className || b.outerHTML || "").toLowerCase();
                    const isSend = t.includes('send') || t.includes('发') || b.getAttribute('data-testid') === 'send-button';
                    const isStop = t.includes('stop') || t.includes('停止');
                    // 必须包含 send 且不包含 stop，且可见
                    return isSend && !isStop && b.offsetParent !== null && !b.disabled;
                }});
            }}

            // 检测是否正在生成 (核心逻辑)
            function isGenerating() {{
                let btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                // 只要页面上有 "Stop" 或 "停止" 按钮，就说明在生成
                return btns.some(b => {{
                    const t = (b.innerText || b.ariaLabel || "").toLowerCase();
                    return t.includes('stop') || t.includes('停止') || t.includes('generating');
                }});
            }}

            showStatus("🚀 Script Ready: " + tasks.length + " tasks", "#444");
            
            for (let i = 0; i < tasks.length; i++) {{
                if (window.kill) {{ showStatus("🛑 Stopped", "#ef4444"); break; }}
                
                showStatus("✍️ Task " + (i+1) + "/" + tasks.length, "#2563eb");
                
                // 1. 寻找输入框
                let box = getInputBox();
                if (!box) {{ 
                    showStatus("❌ Input not found", "#ef4444"); 
                    await new Promise(r => setTimeout(r, 2000));
                    box = getInputBox(); // Retry
                    if (!box) break;
                }}
                
                box.focus();
                
                // 2. 输入文字 (兼容性最强的 execCommand)
                if (box.tagName === 'DIV' || box.contentEditable === "true") {{ 
                    // 先清空一下，防止追加
                    // box.innerText = ""; 
                    document.execCommand('insertText', false, tasks[i]); 
                }} else {{ 
                    box.value = tasks[i]; 
                    box.innerText = tasks[i];
                }}
                
                // 3. 触发 React/Vue 绑定事件
                await new Promise(r => setTimeout(r, 800));
                box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                // 4. 点击发送
                await new Promise(r => setTimeout(r, 800));
                let sendBtn = getSendBtn();
                if (sendBtn) {{
                    sendBtn.click();
                }} else {{
                    // 回车兜底
                    box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                }}
                
                // 5. 等待生成结束 (Polling)
                if (i < tasks.length - 1) {{
                    // 先给它 5 秒反应时间，进入生成状态
                    showStatus("⏳ Waiting to start...", "#64748b");
                    await new Promise(r => setTimeout(r, 5000));
                    
                    let waitSec = 0;
                    while(true) {{
                        if (window.kill) break;
                        
                        // 如果检测不到 "Stop" 按钮，说明生成结束了
                        if (!isGenerating()) {{
                            break;
                        }}
                        
                        showStatus("🎨 Generating (" + waitSec + "s)...", "#7c3aed");
                        await new Promise(r => setTimeout(r, 1000));
                        waitSec++;
                        
                        if (waitSec > 300) break; // 超时防止死循环
                    }}
                    
                    // 6. 冷却时间 (Cool Down)
                    for (let s = 10; s > 0; s--) {{
                        if (window.kill) break;
                        showStatus("🍵 Cooldown: " + s + "s", "#d97706");
                        await new Promise(r => setTimeout(r, 1000));
                    }}
                }}
            }}
            if(!window.kill) showStatus("🎉 All Done!", "#16a34a");
        }})();"""

        # --- C. 自动复制到剪贴板 (Auto-Copy) ---
        js_val = json.dumps(js_code)
        components.html(f"""
        <script>
            const text = {js_val};
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text)
                    .then(() => console.log('✅ Script copied to clipboard!'))
                    .catch(err => console.error('❌ Copy failed', err));
            }}
        </script>
        """, height=0)

        st.success(f"✅ Generated {len(task_list)} tasks. Code copied to clipboard!")
        
        # 显示代码块
        with st.expander("Show Code", expanded=True):
            st.code(js_code, language="javascript")
        
    else:
        st.error("⚠️ No valid tasks found. Please ensure Text Studio generated prompts correctly.")
