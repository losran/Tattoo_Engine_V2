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
# 1. 数据接收
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

current_queue_text = "\n".join(st.session_state.global_queue)

# ===========================
# 2. 界面
# ===========================
st.markdown("## Automation Central")
st.caption("Universal AI Platform Adaptor (Button State Detection Mode)")

col_info, col_clear = st.columns([4, 1])
with col_info:
    st.markdown(f"**Pending Tasks:** {len(st.session_state.global_queue)}")
with col_clear:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        st.rerun()

user_input = st.text_area(
    "Queue Preview", 
    value=current_queue_text, 
    height=350, 
    label_visibility="collapsed"
)

if user_input != current_queue_text:
    st.session_state.global_queue = [line.strip() for line in user_input.split('\n') if line.strip()]

st.divider()

# ===========================
# 3. 核心脚本逻辑 (🔥 按钮状态机版 🔥)
# ===========================
if st.button("⚡ Generate Smart Script (Button Lock)", type="primary", use_container_width=True):
    
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
            console.log("%c 🚀 Button-Lock Automation Started ", "background: #000; color: #0f0; font-size: 14px");
            window.kill = false;
            
            const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
            
            // --- UI ---
            function showStatus(text, color = "#333", sub = "") {{
                let el = document.getElementById('magic-status-bar');
                if (!el) {{
                    el = document.createElement('div');
                    el.id = 'magic-status-bar';
                    el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:12px 24px; border-radius:8px; font-family:monospace; font-size:14px; font-weight:bold; color:#fff; box-shadow:0 8px 30px rgba(0,0,0,0.5); transition: all 0.2s; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px); display:flex; flex-direction:column; align-items:center;";
                    document.body.appendChild(el);
                }}
                el.innerHTML = `<span style="font-size:15px">${{text}}</span>${{sub ? `<span style="font-size:11px; opacity:0.8; margin-top:4px">${{sub}}</span>` : ''}}`;
                el.style.backgroundColor = color;
            }}

            // --- 核心：按钮状态检测 ---
            function getButtonState() {{
                // 1. 找发送按钮
                const sendBtn = document.querySelector('[data-testid="send-button"]') || 
                                document.querySelector('button[aria-label="Send prompt"]') ||
                                document.querySelector('button[aria-label="Send"]') ||
                                document.querySelector('button[aria-label="发送"]');
                
                // 2. 找停止按钮 (这是关键)
                const stopBtn = document.querySelector('[aria-label="Stop generating"]') ||
                                document.querySelector('button[aria-label="Stop"]') ||
                                document.querySelector('.stop-button');

                // 状态判断
                if (stopBtn) return "BUSY"; // 看到停止按钮 -> 绝对忙碌
                if (!sendBtn) return "BUSY"; // 连发送按钮都找不到 -> 可能在加载 -> 忙碌
                if (sendBtn.disabled) return "BUSY"; // 发送按钮是灰的 -> 忙碌
                
                return "IDLE"; // 发送按钮存在且可点 -> 空闲
            }}

            // --- 基础工具 ---
            function getInputBox() {{
                const selectors = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]'];
                for (let s of selectors) {{
                    let el = document.querySelector(s);
                    if (el) return el;
                }}
                return null;
            }}

            // --- 主循环 ---
            showStatus("🚀 Ready", "#212121", tasks.length + " tasks loaded");
            
            for (let i = 0; i < tasks.length; i++) {{
                if (window.kill) {{ showStatus("🛑 Stopped", "#d32f2f"); break; }}
                
                // 1. 寻找输入框
                let box = getInputBox();
                if (!box) {{
                    showStatus("🔍 Finding Input...", "#ff9800");
                    await new Promise(r => setTimeout(r, 2000));
                    box = getInputBox();
                }}

                if (box) {{
                    // 2. 输入任务
                    showStatus("✍️ Writing Task " + (i+1), "#1976d2", (i+1)+"/"+tasks.length);
                    box.focus();
                    document.execCommand('insertText', false, tasks[i]); 
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    await new Promise(r => setTimeout(r, 1000)); 

                    // 3. 点击发送 (强制触发)
                    const sendBtn = document.querySelector('[data-testid="send-button"]') || document.querySelector('button[aria-label="Send prompt"]');
                    if (sendBtn) sendBtn.click();
                    else box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    
                    // 4. 🔥 按钮状态死锁逻辑 (Deadlock Logic) 🔥
                    // 发送后，系统需要一点时间反应，先强制等 5 秒
                    showStatus("⏳ Sent... Waiting for response", "#555");
                    await new Promise(r => setTimeout(r, 5000));

                    if (i < tasks.length - 1) {{
                        let stabilityCounter = 0;
                        let maxWait = 900; // 15分钟超时
                        
                        while (true) {{
                            if (window.kill) break;
                            
                            let state = getButtonState();
                            
                            if (state === "BUSY") {{
                                // 只要是忙碌，计数器归零，无限等待
                                stabilityCounter = 0;
                                showStatus("🎨 Generating...", "#7b1fa2", "System is busy. Waiting...");
                                await new Promise(r => setTimeout(r, 1000)); // 每秒检查一次
                            }} else {{
                                // 如果检测到空闲 (IDLE)，开始累积“稳定值”
                                stabilityCounter++;
                                let remaining = 10 - stabilityCounter; // 目标：连续 10 秒空闲
                                
                                if (remaining > 0) {{
                                    showStatus("✅ Verifying Completion...", "#2e7d32", "Confirming in " + remaining + "s...");
                                    await new Promise(r => setTimeout(r, 1000));
                                }} else {{
                                    // 连续 10 秒都是 IDLE，才敢放行
                                    showStatus("🆗 Confirmed!", "#4caf50", "Next task incoming...");
                                    await new Promise(r => setTimeout(r, 2000));
                                    break; 
                                }}
                            }}
                        }}
                    }}
                }} else {{
                    showStatus("❌ Error: No Input", "#d32f2f");
                    break;
                }}
            }}
            if(!window.kill) showStatus("🎉 All Done!", "#00c853");
        }})();"""

        st.success(f"✅ Button-Lock Script Generated ({len(task_list)} Tasks)")
        
        with st.expander("📦 Get Script", expanded=True):
            st.code(js_code, language="javascript")
        st.caption("Tip: This script watches the 'Send/Stop' button. It only proceeds if the Send button is visible and clickable for 10 continuous seconds.")
    
    else:
        st.error("❌ Queue is empty.")
