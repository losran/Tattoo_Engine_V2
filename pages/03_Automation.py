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
# 2. 接收全局购物车数据
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 列表转文本
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
        ["ChatGPT (Universal)", "Midjourney Web", "Claude"],
        index=0
    )

with col_opt2:
    count = len(st.session_state.global_queue)
    st.metric("Pending Tasks", count)

# 输入框 (双向绑定)
user_input = st.text_area(
    "Global Task Queue", 
    value=current_queue_text, 
    height=400, 
    placeholder="Queue is empty..."
)

# 实时更新回队列
if user_input != current_queue_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

# ===========================
# 4. 生成脚本逻辑 (V19)
# ===========================
st.divider()
c1, c2 = st.columns([1, 2])
with c1:
    if st.button("🗑️ Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

with c2:
    if st.button("🚀 Generate Script (V19 Force Mode)", type="primary", use_container_width=True):
        # A. 智能解析 (更安全的清洗逻辑)
        task_list = []
        if user_input:
            lines = user_input.split('\n\n')
            for line in lines:
                clean_line = line.strip()
                # 🛡️ 修复：只删除特定的报错后缀，不误伤用户自己写的括号
                clean_line = clean_line.replace("(Invalid API Key - Raw Data Used)", "")
                clean_line = clean_line.replace("(Invalid API Key)", "")
                clean_line = clean_line.strip()
                
                if len(clean_line) > 2:
                    task_list.append(clean_line)

        # B. 生成代码 (V19 - 暴力搜索版)
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            js_code = f"""(async function() {{
                console.clear();
                console.log("%c 🚀 Automation V19 (Force Mode) ", "background: #222; color: #ff0055; font-size: 16px");
                
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                // 1. 状态条
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

                // 2. 暴力寻找输入框
                function getInputBox() {{
                    // A计划: 标准ID
                    const ids = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]'];
                    for (let selector of ids) {{
                        let el = document.querySelector(selector);
                        if (el) return el;
                    }}
                    // B计划: 盲找页面上可见的第一个 div[contenteditable]
                    let allDivs = document.querySelectorAll('div[contenteditable="true"]');
                    if(allDivs.length > 0) return allDivs[0];
                    
                    return null;
                }}

                // 3. 寻找发送按钮
                function getSendBtn() {{
                    return document.querySelector('[data-testid="send-button"]') || 
                           document.querySelector('button[aria-label="Send prompt"]') ||
                           document.querySelector('button[aria-label="Send"]');
                }}

                // 4. 忙碌检测
                function isBusy() {{
                    const stopBtn = document.querySelector('[aria-label="Stop generating"]') || document.querySelector('[data-testid="stop-button"]');
                    if (stopBtn) return true;
                    
                    const sendBtn = getSendBtn();
                    // 如果发送按钮不存在或不可点击，通常意味着正在生成或输入框为空
                    // 但为了防止死锁，我们只在"有停止按钮"时才严格判定为忙
                    return false; 
                }}

                showStatus("🚀 Tasks Loaded: " + tasks.length, "#444444"); 
                
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 Stopped", "#ef4444"); break; }}
                    
                    // --- 寻找 ---
                    let box = getInputBox();
                    if (!box) {{ 
                        showStatus("⚠️ Finding Input Box...", "#f59e0b");
                        await new Promise(r => setTimeout(r, 2000));
                        box = getInputBox();
                        if(!box) {{ alert("Error: No Input Box Found!"); break; }}
                    }}
                    
                    // --- 填入 ---
                    showStatus("✍️ Writing " + (i+1) + "...", "#3b82f6");
                    box.focus();
                    
                    // 模拟真实 React 输入逻辑
                    if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                        box.innerHTML = ""; 
                        box.innerText = tasks[i]; 
                    }} else {{
                        box.value = tasks[i];
                    }}
                    
                    // 触发事件链，激活发送按钮
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 800)); 

                    // --- 发送 ---
                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        // 如果按钮是灰的或者找不到，尝试暴力回车
                        showStatus("⚠️ Simulating Enter Key...", "#b45309");
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}
                    
                    // --- 等待生成 ---
                    if (i < tasks.length - 1) {{
                        showStatus("⏳ Waiting for AI...", "#6b7280");
                        
                        // 强制等待 5秒 避免过快
                        await new Promise(r => setTimeout(r, 5000));
                        
                        // 循环检测是否忙碌 (每秒检测一次)
                        let waitSec = 0;
                        while(true) {{
                            if (window.kill) break;
                            
                            // 检查是否有"停止生成"按钮，如果有，说明还在忙
                            let stopBtn = document.querySelector('[aria-label="Stop generating"]');
                            if (stopBtn) {{
                                showStatus("🎨 Generating (" + waitSec + "s)...", "#6366f1");
                                await new Promise(r => setTimeout(r, 1000));
                                waitSec++;
                                if (waitSec > 300) break; // 5分钟超时
                            }} else {{
                                // 没有停止按钮了，说明生成完毕
                                break; 
                            }}
                        }}
                        
                        showStatus("✅ Next task in 3s...", "#10b981");
                        await new Promise(r => setTimeout(r, 3000));
                    }}
                }}
                if(!window.kill) showStatus("🎉 Batch Complete!", "#15803d");
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

            st.success(f"Generated {len(task_list)} tasks. Code copied!")
            st.code(js_code, language="javascript")
            
        else:
            st.error("Queue is empty. Please generate tasks first.")
