import streamlit as st
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
# 1. 数据接收与同步
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 获取全量文本
current_queue_text = "\n".join(st.session_state.global_queue)

# ===========================
# 2. 极简 UI
# ===========================
st.markdown("## Automation Central")
st.caption("Universal AI Platform Adaptor")

col_info, col_clear = st.columns([4, 1])
with col_info:
    st.markdown(f"**Pending Tasks:** {len(st.session_state.global_queue)}")
with col_clear:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

# 编辑器
user_input = st.text_area(
    "Queue Preview", 
    value=current_queue_text, 
    height=350, 
    placeholder="Waiting for tasks from Studio...",
    label_visibility="collapsed",
    help="Each line represents one task."
)

if user_input != current_queue_text:
    st.session_state.global_queue = [line.strip() for line in user_input.split('\n') if line.strip()]

st.divider()

# ===========================
# 3. 万能脚本生成逻辑 (🔥 视觉识别 + 10s 缓冲 🔥)
# ===========================
if st.button("⚡ Generate Smart Script", type="primary", use_container_width=True):
    
    task_list = []
    if user_input:
        raw_lines = user_input.split('\n')
        for line in raw_lines:
            clean_line = line.strip()
            if clean_line:
                task_list.append(clean_line)

    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))
        
        js_code = f"""(async function() {{
            console.clear();
            console.log("%c 🚀 Smart Automation Started (Relaxed Mode) ", "background: #000; color: #0f0; font-size: 14px");
            window.kill = false;
            
            const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
            
            // --- 1. UI 状态条 ---
            function showStatus(text, color = "#333", progress = "") {{
                let el = document.getElementById('magic-status-bar');
                if (!el) {{
                    el = document.createElement('div');
                    el.id = 'magic-status-bar';
                    el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:10px 20px; border-radius:8px; font-family:monospace; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 5px 15px rgba(0,0,0,0.5); transition: all 0.3s; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(5px);";
                    document.body.appendChild(el);
                }}
                el.innerHTML = `<span>${{text}}</span> <span style="opacity:0.7; font-size:12px; margin-left:10px">${{progress}}</span>`;
                el.style.backgroundColor = color;
            }}

            // --- 2. 视觉检测 ---
            function isGenerating() {{
                // A. 停止按钮
                const stopSelectors = [
                    '[aria-label="Stop generating"]',
                    'button[aria-label="Stop"]',
                    '.stop-button',
                    'button.btn-danger'
                ];
                for (let s of stopSelectors) {{
                    if (document.querySelector(s)) return true;
                }}

                // B. 文本关键词 (Discord/MJ)
                const loadingKeywords = [
                    "Waiting to start", "Generating", "(fast)", "(relaxed)", 
                    "0%", "15%", "30%", "60%", "90%"
                ];
                
                // 检查最后一条消息
                const messages = document.querySelectorAll('li[class*="message"], div[class*="message"]');
                if (messages.length > 0) {{
                    const lastMsg = messages[messages.length - 1].innerText;
                    for (let key of loadingKeywords) {{
                        if (lastMsg.includes(key)) return true;
                    }}
                }} else {{
                    // 全局扫描进度条
                    if (document.querySelector('[role="progressbar"]')) return true;
                }}
                return false;
            }}

            // --- 3. 基础工具 ---
            function getInputBox() {{
                const selectors = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]'];
                for (let s of selectors) {{
                    let el = document.querySelector(s);
                    if (el) return el;
                }}
                return null;
            }}

            function getSendBtn() {{
                return document.querySelector('[data-testid="send-button"]') || 
                       document.querySelector('button[aria-label="Send prompt"]') ||
                       document.querySelector('button[aria-label="Send"]');
            }}

            // --- 4. 主执行循环 ---
            showStatus("🚀 Loaded " + tasks.length + " tasks", "#212121");
            
            for (let i = 0; i < tasks.length; i++) {{
                if (window.kill) {{ showStatus("🛑 Stopped", "#d32f2f"); break; }}
                
                let box = getInputBox();
                if (!box) {{
                    showStatus("🔍 Searching for input...", "#ff9800");
                    await new Promise(r => setTimeout(r, 2000));
                    box = getInputBox();
                }}

                if (box) {{
                    // 输入
                    showStatus("✍️ Task " + (i+1), "#1976d2", (i+1)+"/"+tasks.length);
                    box.focus();
                    document.execCommand('insertText', false, tasks[i]); 
                    if (box.value !== tasks[i] && box.innerText !== tasks[i]) {{ box.value = tasks[i]; }}
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    await new Promise(r => setTimeout(r, 800)); 

                    // 发送
                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}
                    
                    // 启动视觉阻塞
                    showStatus("⏳ Starting...", "#555");
                    await new Promise(r => setTimeout(r, 5000));

                    if (i < tasks.length - 1) {{
                        let busyCount = 0;
                        let maxWait = 600; // 放宽到 10分钟 防止超大图卡死
                        
                        while (true) {{
                            if (window.kill) break;
                            
                            if (isGenerating()) {{
                                busyCount++;
                                showStatus("🎨 Generating detected...", "#7b1fa2", busyCount + "s");
                                await new Promise(r => setTimeout(r, 2000));
                            }} else {{
                                // 确认阶段：先等 3秒 看看是不是真的停了
                                showStatus("✅ Verifying...", "#2e7d32");
                                await new Promise(r => setTimeout(r, 3000));
                                
                                if (!isGenerating()) {{
                                    // 🔥🔥🔥 核心修改：确认完成后，额外强制等待 10秒 🔥🔥🔥
                                    for (let k = 10; k > 0; k--) {{
                                        if (window.kill) break;
                                        showStatus("🍵 Safety Cooldown: " + k + "s", "#4caf50");
                                        await new Promise(r => setTimeout(r, 1000));
                                    }}
                                    break; // 彻底完成，放行下一个
                                }}
                            }}
                            
                            if (busyCount > maxWait) {{
                                showStatus("⚠️ Timeout (Force Next)", "#e65100");
                                break; 
                            }}
                        }}
                    }}
                }} else {{
                    showStatus("❌ Error: No Input Box", "#d32f2f");
                    break;
                }}
            }}
            if(!window.kill) showStatus("🎉 All Tasks Completed!", "#00c853");
        }})();"""

        st.success(f"✅ Smart Script Ready! ({len(task_list)} Tasks)")
        
        with st.expander("📦 Get Smart Script", expanded=True):
            st.code(js_code, language="javascript")
        st.caption("Tip: This script includes a visual detector AND a 10-second safety buffer after each task completes.")
    
    else:
        st.error("❌ Queue is empty.")
