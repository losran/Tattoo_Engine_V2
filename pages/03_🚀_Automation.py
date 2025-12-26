import streamlit as st
from style_manager import apply_pro_style
import streamlit.components.v1 as components
import json
import urllib.parse
import re
from engine_manager import render_sidebar

# ===========================
# Configuration
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")

# Apply Styles & Sidebar
apply_pro_style()
render_sidebar()

# ===========================
# UI Layout
# ===========================
st.title("Automation Central (Pro V16)")
st.caption("Auto-Detect ChatGPT State (基于发送按钮状态检测)")

# Platform Selection
col_opt1, col_opt2 = st.columns([2, 1])
with col_opt1:
    target_platform = st.selectbox(
        "Target AI Platform", 
        ["Universal", "ChatGPT (Specialized)", "Midjourney Web"],
        index=1, # 默认选中 ChatGPT
        help="ChatGPT mode uses advanced DOM detection for 'Generating' state."
    )

# Input Area
default_text = st.session_state.get('auto_input_cache', "")
if not default_text:
    default_text = st.session_state.get('polished_text', "")

user_input = st.text_area("Prompt Queue", value=default_text, height=300, key="main_input_area")

# --- Options ---
st.divider()
col_check, col_btn = st.columns([1, 2])
with col_check:
    need_white_bg = st.checkbox("Production Mode: Auto White Background", value=False)

# --- Generation Logic ---
with col_btn:
    if st.button("Generate Script (Smart Wait)", type="primary", use_container_width=True):
        # --- A. Task Parsing ---
        task_list = []
        if user_input:
            if "###" in user_input:
                raw_tasks = [t.strip() for t in user_input.split("###") if len(t.strip()) > 2]
            else:
                blocks = re.split(r'\*\*.*?(?:方案|Scheme|Option).*?[\d]+[:：].*?\*\*', user_input)
                raw_tasks = [b.strip().replace('* ', '').replace('\n', ' ') for b in blocks if len(b.strip()) > 5]
            
            if need_white_bg:
                for t in raw_tasks:
                    task_list.append(t)
                    task_list.append("Generate a white background version of the image above")
            else:
                task_list = raw_tasks

        # --- B. Script Construction ---
        if task_list:
            encoded_data = urllib.parse.quote(json.dumps(task_list))
            
            # ⬇️⬇️⬇️ 核心修复逻辑 ⬇️⬇️⬇️
            js_code = f"""(async function() {{
                console.clear();
                console.log("%c 🚀 自动化脚本 V16 已启动 ", "background: #222; color: #bada55; font-size: 16px");
                
                window.kill = false;
                const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
                
                // 1. 状态条 (UI)
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

                // 2. 找输入框 (兼容 ChatGPT 新旧版)
                function getInputBox() {{
                    const ids = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]'];
                    for (let selector of ids) {{
                        let el = document.querySelector(selector);
                        if (el) return el;
                    }}
                    return null;
                }}

                // 3. 找发送按钮 (核心锚点)
                function getSendBtn() {{
                    return document.querySelector('[data-testid="send-button"]') || 
                           document.querySelector('button[aria-label="Send prompt"]');
                }}

                // 4. 判断是否忙碌 (核心修复：只要发送按钮不在，或者被禁用，就是忙碌)
                function isBusy() {{
                    const sendBtn = getSendBtn();
                    const stopBtn = document.querySelector('[aria-label="Stop generating"]') || document.querySelector('[data-testid="stop-button"]');
                    
                    // 如果有停止按钮，绝对是在忙
                    if (stopBtn) return true;
                    
                    // 如果没有发送按钮，通常也是在忙 (或者UI还没加载出来)
                    if (!sendBtn) return true;
                    
                    // 如果有发送按钮，但是是 disabled (灰的)，说明还在处理或者输入框为空
                    if (sendBtn.disabled) return true;
                    
                    return false; // 不忙
                }}

                // --- 主流程 ---
                showStatus("🚀 脚本就绪，任务数: " + tasks.length, "#444444"); 
                
                for (let i = 0; i < tasks.length; i++) {{
                    if (window.kill) {{ showStatus("🛑 已停止", "#ef4444"); break; }}
                    
                    // --- 步骤A: 输入 ---
                    showStatus("✍️ 正在输入: " + (i+1) + "/" + tasks.length, "#3b82f6");
                    
                    let box = getInputBox();
                    if (!box) {{ 
                        showStatus("❌ 找不到输入框，尝试重试...", "#ef4444"); 
                        await new Promise(r => setTimeout(r, 2000));
                        box = getInputBox();
                        if(!box) {{ alert("脚本无法定位输入框，请刷新页面"); break; }}
                    }}
                    
                    box.focus();
                    // 模拟真实输入
                    if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                        box.innerHTML = ""; 
                        box.innerText = tasks[i]; 
                    }} else {{
                        box.value = tasks[i];
                    }}
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    await new Promise(r => setTimeout(r, 1000)); // 给人眼一点反应时间

                    // --- 步骤B: 发送 ---
                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        // 兜底：回车发送
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', bubbles: true }}));
                    }}
                    
                    // --- 步骤C: 等待生成 (Smart Wait) ---
                    if (i < tasks.length - 1) {{
                        // 1. 先死等 5秒，防止网速慢导致还没进入生成状态脚本就以为闲置了
                        showStatus("⏳ 等待服务器响应...", "#f59e0b");
                        await new Promise(r => setTimeout(r, 5000));
                        
                        // 2. 循环检测忙碌状态
                        let waitSec = 0;
                        while(true) {{
                            if (window.kill) break;
                            
                            if (isBusy()) {{
                                showStatus("🎨 正在绘图 (" + waitSec + "s)...", "#6366f1");
                                await new Promise(r => setTimeout(r, 1000));
                                waitSec++;
                                if (waitSec > 300) break; // 超时保护 (5分钟)
                            }} else {{
                                // 不忙了！说明图出完了
                                break; 
                            }}
                        }}
                        
                        // 3. 冷却时间 (给点缓冲)
                        for (let s = 5; s > 0; s--) {{
                            if (window.kill) break;
                            showStatus("✅ 完成. 冷却中: " + s + "s", "#10b981");
                            await new Promise(r => setTimeout(r, 1000));
                        }}
                    }}
                }}
                if(!window.kill) showStatus("🎉 所有任务执行完毕！", "#15803d");
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
    st.session_state.auto_input_cache = ""
    st.session_state.polished_text = ""
    st.rerun()
