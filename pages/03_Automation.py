import streamlit as st
import json
import urllib.parse
import re
from engine_manager import render_sidebar, init_data
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置与初始化
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# 2. 数据接收与同步
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 获取全量文本用于编辑或展示
current_queue_text = ""
if st.session_state.global_queue:
    current_queue_text = "\n\n".join(st.session_state.global_queue)

# ===========================
# 3. 极简 UI 呈现
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

# 核心：直接全量呈现编辑器，不再使用下拉框
user_input = st.text_area(
    "Queue Preview", 
    value=current_queue_text, 
    height=350, 
    placeholder="Waiting for tasks from Studio...",
    label_visibility="collapsed"
)

# 同步编辑内容
if user_input != current_queue_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 4. 万能脚本生成逻辑
# ===========================
if st.button("⚡ Generate Universal Script", type="primary", use_container_width=True):
    # A. 精准解析方案内容
    task_list = []
    if user_input:
        # 使用正则提取 "**方案N：" 之后的内容，或者直接按空行切分
        segments = re.split(r"\*\*方案\d+：\*\*", user_input)
        for seg in segments:
            clean = seg.strip()
            # 过滤掉无用的后缀提示词
            clean = clean.split("(Invalid")[0].split("(Connection")[0].split("(Offline")[0].strip()
            if len(clean) > 2:
                task_list.append(clean.replace("\n", " "))

    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))
        
        # --- 核心万能适配 JS 脚本 ---
        js_code = f"""(async function() {{
            console.clear();
            console.log("%c 🚀 Universal Automation Started ", "background: #000; color: #0f0; font-size: 14px");
            window.kill = false;
            const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
            
            // 状态条组件
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

            // 万能输入框查找器
            function getInputBox() {{
                const selectors = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]', '.chat-input-textarea'];
                for (let s of selectors) {{
                    let el = document.querySelector(s);
                    if (el) return el;
                }}
                return null;
            }}

            // 万能发送按钮查找器
            function getSendBtn() {{
                return document.querySelector('[data-testid="send-button"]') || 
                       document.querySelector('button[aria-label="Send prompt"]') ||
                       document.querySelector('button[aria-label="发送"]') ||
                       document.querySelector('button[aria-label="Send"]');
            }}

            showStatus("🚀 Loaded " + tasks.length + " tasks", "#444"); 
            
            for (let i = 0; i < tasks.length; i++) {{
                if (window.kill) {{ showStatus("🛑 Stopped", "#d32f2f"); break; }}
                
                let box = getInputBox();
                if (!box) {{ 
                    showStatus("⚠️ Waiting for Input Box...", "#f57c00");
                    await new Promise(r => setTimeout(r, 2000));
                    box = getInputBox();
                }}
                
                showStatus("✍️ Task " + (i+1) + "/" + tasks.length, "#1976d2");
                box.focus();
                
                // 输入注入
                if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                    box.innerText = tasks[i]; 
                }} else {{
                    box.value = tasks[i];
                }}
                
                // 触发页面监听事件
                box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                await new Promise(r => setTimeout(r, 800)); 

                // 点击发送
                let sendBtn = getSendBtn();
                if (sendBtn && !sendBtn.disabled) {{
                    sendBtn.click();
                }} else {{
                    // 如果找不到按钮或按钮禁用，尝试模拟 Enter
                    box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                }}
                
                // 智能冷却与检测
                if (i < tasks.length - 1) {{
                    showStatus("⏳ Cooldown...", "#616161");
                    await new Promise(r => setTimeout(r, 4000));
                    
                    let waitSec = 0;
                    while(true) {{
                        if (window.kill) break;
                        // 适配多种停止/生成中状态
                        let isGenerating = document.querySelector('[aria-label="Stop generating"]') || 
                                           document.querySelector('.stop-button') || 
                                           document.querySelector('button[aria-label="停止"]');
                        
                        if (isGenerating) {{
                            showStatus("🎨 AI Generating (" + waitSec + "s)...", "#7b1fa2");
                            await new Promise(r => setTimeout(r, 1000));
                            waitSec++;
                            if (waitSec > 300) break; // 超时退出
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

        st.success(f"✅ Ready! ({len(task_list)} Tasks Parsed)")
        
        # 胶囊呈现
        with st.expander("📦 Get Universal Script", expanded=True):
            st.code(js_code, language="javascript")
        st.caption("Tip: Copy the code, F12 on ChatGPT/Gemini/Doubao, paste into Console and Enter.")
    else:
        st.error("No valid tasks found in the queue.")
