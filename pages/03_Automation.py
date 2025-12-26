import streamlit as st
from style_manager import apply_pro_style
import streamlit.components.v1 as components
import json
import urllib.parse
import re
from engine_manager import render_sidebar

# ===========================
# 1. 页面配置
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()

st.markdown("## Automation Central")
st.caption("Batch Processing Center")

# ===========================
# 2. 接收数据 (Global Queue)
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

current_queue_text = ""
if st.session_state.global_queue:
    current_queue_text = "\n\n".join(st.session_state.global_queue)

# ===========================
# 3. 界面布局 (控制台风格)
# ===========================
# 上半部分：控制栏
c1, c2 = st.columns([2, 1])
with c1:
    target_platform = st.selectbox(
        "Target Platform", 
        ["ChatGPT (Universal)", "Midjourney Web", "Claude"],
        index=0,
        label_visibility="collapsed"
    )

with c2:
    st.markdown(f"<div style='text-align:right; line-height: 42px; color:#666;'>Pending Tasks: {len(st.session_state.global_queue)}</div>", unsafe_allow_html=True)

# 下半部分：任务队列编辑器
user_input = st.text_area(
    "Queue Editor", 
    value=current_queue_text, 
    height=300, 
    placeholder="Waiting for tasks from Graphic Lab or Text Studio...",
    label_visibility="collapsed"
)

# 双向绑定更新
if user_input != current_queue_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 4. 隐形生成逻辑 (No Code Display)
# ===========================
c_clear, c_gen = st.columns([1, 4])

with c_clear:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

with c_gen:
    # 按钮文案简单直接
    if st.button("⚡ Generate & Copy Script", type="primary", use_container_width=True):
        # A. 智能清洗
        task_list = []
        if user_input:
            lines = user_input.split('\n\n')
            for line in lines:
                clean = line.strip()
                # 自动剪掉报错小尾巴
                clean = clean.split("(Invalid")[0].strip()
                clean = clean.split("(Connection")[0].strip()
                clean = clean.split("(Offline")[0].strip()
                if len(clean) > 2:
                    task_list.append(clean)

        # B. 生成代码 (依然是那个强大的 V20 逻辑，只是不给你看了)
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            # JS 核心逻辑 (压缩版)
            js_code = f"""(async function() {{
                console.clear();
                console.log("%c 🚀 Automation Started ", "background: #000; color: #0f0; font-size: 14px");
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                function showStatus(text, color = "#333") {{
                    let el = document.getElementById('magic-status-bar');
                    if (!el) {{
                        el = document.createElement('div');
                        el.id = 'magic-status-bar';
                        el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:8px 16px; border-radius:4px; font-family:sans-serif; font-size:13px; font-weight:bold; color:#fff; box-shadow:0 5px 15px rgba(0,0,0,0.3); transition: all 0.3s;";
                        document.body.appendChild(el);
                    }}
                    el.textContent = text;
                    el.style.backgroundColor = color;
                }}

                function getInputBox() {{
                    const ids = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]'];
                    for (let selector of ids) {{
                        let el = document.querySelector(selector);
                        if (el) return el;
                    }}
                    let allDivs = document.querySelectorAll('div[contenteditable="true"]');
                    if(allDivs.length > 0) return allDivs[0];
                    return null;
                }}

                function getSendBtn() {{
                    return document.querySelector('[data-testid="send-button"]') || 
                           document.querySelector('button[aria-label="Send prompt"]') ||
                           document.querySelector('button[aria-label="Send"]');
                }}

                showStatus("🚀 Loaded " + tasks.length + " tasks", "#444"); 
                
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 Stopped", "#d32f2f"); break; }}
                    
                    let box = getInputBox();
                    if (!box) {{ 
                        showStatus("⚠️ Input box not found", "#f57c00");
                        await new Promise(r => setTimeout(r, 2000));
                        box = getInputBox();
                        if(!box) {{ alert("Error: Can't find input box"); break; }}
                    }}
                    
                    showStatus("✍️ Task " + (i+1) + "/" + tasks.length, "#1976d2");
                    box.focus();
                    
                    if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                        box.innerHTML = ""; 
                        box.innerText = tasks[i]; 
                    }} else {{
                        box.value = tasks[i];
                    }}
                    
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    await new Promise(r => setTimeout(r, 800)); 

                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}
                    
                    if (i < tasks.length - 1) {{
                        showStatus("⏳ Cooldown...", "#616161");
                        await new Promise(r => setTimeout(r, 5000));
                        
                        let waitSec = 0;
                        while(true) {{
                            if (window.kill) break;
                            let stopBtn = document.querySelector('[aria-label="Stop generating"]');
                            if (stopBtn) {{
                                showStatus("🎨 Generating (" + waitSec + "s)...", "#7b1fa2");
                                await new Promise(r => setTimeout(r, 1000));
                                waitSec++;
                                if (waitSec > 300) break;
                            }} else {{
                                break; 
                            }}
                        }}
                        showStatus("✅ Next in 3s...", "#388e3c");
                        await new Promise(r => setTimeout(r, 3000));
                    }}
                }}
                if(!window.kill) showStatus("🎉 All Done!", "#2e7d32");
            }})();"""

            js_val = json.dumps(js_code)
            
            # C. 隐形执行复制 (高度为0的HTML组件)
            components.html(f"""
            <script>
                const text = {js_val};
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(text)
                        .then(() => console.log('Copied!'))
                        .catch(err => console.log('Copy failed', err));
                }}
            </script>
            """, height=0)

            # D. 只显示简单的成功提示
            st.success(f"✅ Script for {len(task_list)} tasks copied to clipboard!")
            st.caption("Now open ChatGPT/Midjourney, press **F12** (Console), and paste (**Ctrl+V**).")
            
        else:
            st.error("Queue is empty.")
