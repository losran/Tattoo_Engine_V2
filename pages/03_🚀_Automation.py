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

st.title("Automation Central")
st.caption("Batch Processing Center (批量处理中心)")

# ===========================
# 2. 🟢 核心修复：读取全局购物车
# ===========================
# 初始化队列
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 将列表转换为文本显示
current_queue_text = ""
if st.session_state.global_queue:
    current_queue_text = "\n\n".join(st.session_state.global_queue)

# ===========================
# 3. 界面布局
# ===========================
col_opt1, col_opt2 = st.columns([2, 1])
with col_opt1:
    target_platform = st.selectbox(
        "Target AI Platform", 
        ["ChatGPT (Specialized)", "Midjourney Web", "Universal"],
        index=0
    )

with col_opt2:
    # 显示当前队列数量
    count = len(st.session_state.global_queue)
    st.metric("Pending Tasks", count)

# 输入框 (允许用户手动编辑购物车)
user_input = st.text_area(
    "Global Task Queue", 
    value=current_queue_text, 
    height=400, 
    placeholder="Queue is empty. Go to Graphic Lab or Text Studio to generate tasks."
)

# 🔄 双向绑定：如果用户手动改了输入框，也要更新回队列
if user_input != current_queue_text:
    # 简单的按双换行符分割回写
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

# ===========================
# 4. 生成脚本逻辑
# ===========================
st.divider()
c1, c2 = st.columns([1, 2])
with c1:
    if st.button("🗑️ Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

with c2:
    if st.button("🚀 Generate Script (Execute Batch)", type="primary", use_container_width=True):
        # A. 解析
        task_list = []
        if user_input:
            # 智能清洗：去掉前缀，只留核心Prompt
            lines = user_input.split('\n\n')
            for line in lines:
                clean_line = line.strip()
                # 去掉 (Invalid API Key...) 这种报错后缀
                clean_line = clean_line.split("(Invalid")[0].strip()
                # 去掉 **Option X:** 这种前缀 (可选，根据你的喜好)
                # clean_line = re.sub(r'\*\*Option \d+:\*\*\s*', '', clean_line) 
                
                if len(clean_line) > 5:
                    task_list.append(clean_line)

        # B. 生成代码
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            js_code = f"""(async function() {{
                console.clear();
                console.log("%c 🚀 Automation V18 Started ", "background: #222; color: #bada55; font-size: 16px");
                
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                function showStatus(text, color = "#1e293b") {{
                    let el = document.getElementById('magic-status-bar');
                    if (!el) {{
                        el = document.createElement('div');
                        el.id = 'magic-status-bar';
                        el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:10px 20px; border-radius:30px; font-family:sans-serif; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 10px 25px rgba(0,0,0,0.2); transition: all 0.3s;";
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
                    return null;
                }}

                function getSendBtn() {{
                    return document.querySelector('[data-testid="send-button"]') || 
                           document.querySelector('button[aria-label="Send prompt"]');
                }}

                function isBusy() {{
                    const sendBtn = getSendBtn();
                    const stopBtn = document.querySelector('[aria-label="Stop generating"]') || document.querySelector('[data-testid="stop-button"]');
                    if (stopBtn) return true;
                    if (!sendBtn) return true;
                    if (sendBtn.disabled) return true;
                    return false;
                }}

                showStatus("🚀 Tasks: " + tasks.length, "#444444"); 
                
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 Stopped", "#ef4444"); break; }}
                    
                    showStatus("✍️ Input: " + (i+1) + "/" + tasks.length, "#3b82f6");
                    
                    let box = getInputBox();
                    if (!box) {{ 
                        showStatus("❌ No Input Box", "#ef4444"); 
                        await new Promise(r => setTimeout(r, 2000));
                        box = getInputBox();
                        if(!box) {{ alert("Can't find input box"); break; }}
                    }}
                    
                    box.focus();
                    if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                        box.innerHTML = ""; 
                        box.innerText = tasks[i]; 
                    }} else {{
                        box.value = tasks[i];
                    }}
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 1000)); 

                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', bubbles: true }}));
                    }}
                    
                    if (i < tasks.length - 1) {{
                        showStatus("⏳ Waiting...", "#f59e0b");
                        await new Promise(r => setTimeout(r, 5000));
                        
                        let waitSec = 0;
                        while(true) {{
                            if (window.kill) break;
                            if (isBusy()) {{
                                showStatus("🎨 Generating (" + waitSec + "s)...", "#6366f1");
                                await new Promise(r => setTimeout(r, 1000));
                                waitSec++;
                                if (waitSec > 600) break;
                            }} else {{
                                break; 
                            }}
                        }}
                        
                        for (let s = 5; s > 0; s--) {{
                            if (window.kill) break;
                            showStatus("✅ Cooldown: " + s + "s", "#10b981");
                            await new Promise(r => setTimeout(r, 1000));
                        }}
                    }}
                }}
                if(!window.kill) showStatus("🎉 All Done!", "#15803d");
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

            st.success(f"Generated script for {len(task_list)} tasks (Copied!)")
            st.code(js_code, language="javascript")
            
        else:
            st.error("Queue is empty")
